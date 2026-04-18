#include "models.h"

#include <cstdio>

template <bool iswa>
llm_build_gemma4<iswa>::llm_build_gemma4(const llama_model & model, const llm_graph_params & params) : llm_graph_context(params) {
    ggml_tensor * cur;
    ggml_tensor * inpL;

    fprintf(stderr, "gemma4 graph: begin iswa=%d n_layer=%lld n_tokens=%lld\n",
            iswa, (long long) n_layer, (long long) n_tokens);
    fflush(stderr);

    inpL = build_inp_embd(model.tok_embd);
    inpL = ggml_scale(ctx0, inpL, sqrtf(n_embd));
    cb(inpL, "inp_scaled", -1);

    ggml_tensor * inp_pos = build_inp_pos();

    using inp_attn_type = std::conditional_t<iswa, llm_graph_input_attn_kv_iswa, llm_graph_input_attn_kv>;
    inp_attn_type * inp_attn = nullptr;

    if constexpr (iswa) {
        inp_attn = build_attn_inp_kv_iswa();
    } else {
        inp_attn = build_attn_inp_kv();
    }

    ggml_tensor * inp_out_ids = build_inp_out_ids();

    for (int il = 0; il < n_layer; ++il) {
        const int64_t n_embd_head_k = hparams.n_embd_head_k_arr[il];
        const int64_t n_embd_head_v = hparams.n_embd_head_v_arr[il];
        const int64_t n_head_l      = hparams.n_head(il);
        const int64_t n_head_kv_l   = hparams.n_head_kv(il);

        fprintf(stderr, "gemma4 graph: layer %d enter (is_swa=%d n_head=%lld n_head_kv=%lld n_head_k=%lld n_head_v=%lld)\n",
                il, hparams.is_swa(il), (long long) n_head_l, (long long) n_head_kv_l,
                (long long) n_embd_head_k, (long long) n_embd_head_v);
        fflush(stderr);

        float freq_base_l  = freq_base;
        float freq_scale_l = freq_scale;

        if constexpr (iswa) {
            freq_base_l  = model.get_rope_freq_base(cparams, il);
            freq_scale_l = model.get_rope_freq_scale(cparams, il);
        }

        ggml_tensor * residual = inpL;

        cur = build_norm(residual, model.layers[il].attn_norm, nullptr, LLM_NORM_RMS, il);
        cb(cur, "attn_norm", il);
        fprintf(stderr, "gemma4 graph: layer %d attn_norm complete\n", il);
        fflush(stderr);

        {
            ggml_tensor * Qcur = build_lora_mm(model.layers[il].wq, cur);
            ggml_tensor * Kcur = build_lora_mm(model.layers[il].wk, cur);
            const bool use_k_eq_v = model.layers[il].wv == nullptr;
            ggml_tensor * Vcur = use_k_eq_v ? Kcur : build_lora_mm(model.layers[il].wv, cur);
            cb(Qcur, "Qcur", il);
            cb(Kcur, "Kcur", il);
            cb(Vcur, "Vcur", il);
            fprintf(stderr, "gemma4 graph: layer %d qkv projections complete\n", il);
            fflush(stderr);

            Qcur = ggml_reshape_3d(ctx0, Qcur, n_embd_head_k, n_head_l,    n_tokens);
            Kcur = ggml_reshape_3d(ctx0, Kcur, n_embd_head_k, n_head_kv_l, n_tokens);
            Vcur = use_k_eq_v
                    ? ggml_reshape_3d(ctx0, Vcur, n_embd_head_k, n_head_kv_l, n_tokens)
                    : ggml_reshape_3d(ctx0, Vcur, n_embd_head_v, n_head_kv_l, n_tokens);
            fprintf(stderr, "gemma4 graph: layer %d qkv reshapes complete\n", il);
            fflush(stderr);

            Qcur = build_norm(Qcur, model.layers[il].attn_q_norm, nullptr, LLM_NORM_RMS, il);
            Kcur = build_norm(Kcur, model.layers[il].attn_k_norm, nullptr, LLM_NORM_RMS, il);
            Vcur = ggml_rms_norm(ctx0, Vcur, hparams.f_norm_rms_eps);

            cb(Qcur, "Qcur_normed", il);
            cb(Kcur, "Kcur_normed", il);
            cb(Vcur, "Vcur_normed", il);
            fprintf(stderr, "gemma4 graph: layer %d qkv norms complete\n", il);
            fflush(stderr);

            Qcur = ggml_rope_ext(
                    ctx0, Qcur, inp_pos, nullptr,
                    n_embd_head_k, rope_type, n_ctx_orig, freq_base_l, freq_scale_l,
                    ext_factor, attn_factor, beta_fast, beta_slow);

            if (!use_k_eq_v) {
                Kcur = ggml_rope_ext(
                        ctx0, Kcur, inp_pos, nullptr,
                        n_embd_head_k, rope_type, n_ctx_orig, freq_base_l, freq_scale_l,
                        ext_factor, attn_factor, beta_fast, beta_slow);
            }

            cb(Qcur, "Qcur_rope", il);
            cb(Kcur, "Kcur_rope", il);
            fprintf(stderr, "gemma4 graph: layer %d rope complete freq_base=%g freq_scale=%g\n", il, freq_base_l, freq_scale_l);
            fflush(stderr);

            // Gemma 4 uses learned Q/K norms instead of the Gemma 2/3 1/sqrt(head_dim) scaling.
            cur = build_attn(inp_attn,
                    model.layers[il].wo, nullptr,
                    Qcur, Kcur, Vcur, nullptr, nullptr, nullptr, 1.0f, il);
            ggml_mul_mat_set_prec(cur, GGML_PREC_F32);
            cb(cur, "attn_out", il);
            fprintf(stderr, "gemma4 graph: layer %d build_attn complete\n", il);
            fflush(stderr);
        }
        fprintf(stderr, "gemma4 graph: layer %d attention complete\n", il);
        fflush(stderr);

        if (il == n_layer - 1 && inp_out_ids) {
            cur      = ggml_get_rows(ctx0, cur,      inp_out_ids);
            residual = ggml_get_rows(ctx0, residual, inp_out_ids);
        }

        cur = build_norm(cur, model.layers[il].attn_post_norm, nullptr, LLM_NORM_RMS, il);
        cb(cur, "attn_post_norm", il);

        cur = ggml_add(ctx0, cur, residual);
        cb(cur, "attn_residual", il);
        fprintf(stderr, "gemma4 graph: layer %d post-attention residual complete\n", il);
        fflush(stderr);

        ggml_tensor * ffn_residual = cur;
        ggml_tensor * dense_inp = build_norm(ffn_residual, model.layers[il].ffn_norm, nullptr, LLM_NORM_RMS, il);
        cb(dense_inp, "ffn_norm", il);

        ggml_tensor * dense_out = build_ffn(dense_inp,
                model.layers[il].ffn_up,   nullptr, nullptr,
                model.layers[il].ffn_gate, nullptr, nullptr,
                model.layers[il].ffn_down, nullptr, nullptr,
                nullptr,
                LLM_FFN_GELU, LLM_FFN_PAR, il);
        cb(dense_out, "ffn_dense_out", il);
        fprintf(stderr, "gemma4 graph: layer %d dense ffn complete\n", il);
        fflush(stderr);

        if (model.layers[il].ffn_norm_exps != nullptr) {
            dense_out = build_norm(dense_out, model.layers[il].ffn_norm_exps, nullptr, LLM_NORM_RMS, il);
            cb(dense_out, "ffn_post_norm_1", il);
        }

        ggml_tensor * ffn_out = dense_out;

        if (model.layers[il].ffn_gate_inp != nullptr &&
            model.layers[il].ffn_gate_up_exps != nullptr &&
            model.layers[il].ffn_down_exps != nullptr) {
            ggml_tensor * moe_inp = ffn_residual;

            if (model.layers[il].layer_out_norm_b != nullptr) {
                moe_inp = build_norm(moe_inp, model.layers[il].layer_out_norm_b, nullptr, LLM_NORM_RMS, il);
                cb(moe_inp, "ffn_pre_norm_2", il);
            }

            ggml_tensor * moe_logits = build_lora_mm(model.layers[il].ffn_gate_inp, moe_inp);
            ggml_mul_mat_set_prec(moe_logits, GGML_PREC_F32);
            if (hparams.f_router_logit_softcapping > 0.0f) {
                moe_logits = ggml_scale(ctx0, moe_logits, 1.0f / hparams.f_router_logit_softcapping);
                moe_logits = ggml_tanh(ctx0, moe_logits);
                moe_logits = ggml_scale(ctx0, moe_logits, hparams.f_router_logit_softcapping);
            }

            ggml_tensor * moe_out = build_moe_ffn(moe_inp,
                    model.layers[il].ffn_gate_inp,
                    nullptr,
                    nullptr,
                    model.layers[il].ffn_down_exps,
                    nullptr,
                    n_expert, n_expert_used,
                    LLM_FFN_GELU, true,
                    hparams.expert_weights_scale,
                    LLAMA_EXPERT_GATING_FUNC_TYPE_SOFTMAX,
                    il,
                    moe_logits,
                    model.layers[il].ffn_gate_up_exps);
            cb(moe_out, "ffn_moe_out", il);
            fprintf(stderr, "gemma4 graph: layer %d moe ffn complete\n", il);
            fflush(stderr);

            if (model.layers[il].layer_out_norm != nullptr) {
                moe_out = build_norm(moe_out, model.layers[il].layer_out_norm, nullptr, LLM_NORM_RMS, il);
                cb(moe_out, "ffn_post_norm_2", il);
            }

            ffn_out = ggml_add(ctx0, ggml_cast(ctx0, dense_out, GGML_TYPE_F32), ggml_cast(ctx0, moe_out, GGML_TYPE_F32));
            cb(ffn_out, "ffn_merged", il);
        }

        if (model.layers[il].ffn_post_norm != nullptr) {
            ffn_out = build_norm(ffn_out, model.layers[il].ffn_post_norm, nullptr, LLM_NORM_RMS, il);
            cb(ffn_out, "ffn_post_norm", il);
        }

        cur = ggml_add(ctx0, ffn_out, ffn_residual);
        cb(cur, "ffn_residual", il);

        if (model.layers[il].ffn_act != nullptr) {
            cur = ggml_mul(ctx0, cur, model.layers[il].ffn_act);
            cb(cur, "layer_output_scale", il);
        }

        cur = build_cvec(cur, il);
        cb(cur, "l_out", il);
        fprintf(stderr, "gemma4 graph: layer %d complete\n", il);
        fflush(stderr);

        inpL = cur;
    }

    fprintf(stderr, "gemma4 graph: entering output head\n");
    fflush(stderr);
    cur = build_norm(inpL, model.output_norm, nullptr, LLM_NORM_RMS, -1);
    cb(cur, "result_norm", -1);
    res->t_embd = cur;

    cur = build_lora_mm(model.output, cur);

    if (hparams.f_final_logit_softcapping > 0.0f) {
        cur = ggml_scale(ctx0, cur, 1.0f / hparams.f_final_logit_softcapping);
        cur = ggml_tanh(ctx0, cur);
        cur = ggml_scale(ctx0, cur, hparams.f_final_logit_softcapping);
    }

    cb(cur, "result_output", -1);
    res->t_logits = cur;

    ggml_build_forward_expand(gf, cur);
    fprintf(stderr, "gemma4 graph: end\n");
    fflush(stderr);
}

template struct llm_build_gemma4<false>;
template struct llm_build_gemma4<true>;
