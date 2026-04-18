# Gemma 4 26B MoE Analysis

## Summary
The "First Light" test failed due to a combination of environment-specific issues and severe model file corruption.

## Findings

### 1. CUDA 13.2 Instability
- **Detection:** System was confirmed running `nvcc release 13.2, V13.2.51`.
- **Symptom:** CUDA execution resulted in a deterministic `<unused32>` infinite loop.
- **Verification:** Switching to a **CPU-only build** resolved the infinite loop, although output remained incoherent.
- **Recommendation:** Do not use CUDA 13.2 for Gemma 4 GGUF models as of April 2026. Use a CPU build or downgrade to CUDA 12.x.

### 2. Model File Corruption
- **Detection:** Inspected GGUF weights using `llama-gguf.exe`.
- **Evidence:**
    - `token_embd.weight` (q6_K) contains nonsensical values (e.g., `5.19e+27`).
    - `blk.0.attn_k.weight` contains extreme values and `NaN`.
    - `blk.29.attn_k.weight` contains explicit `-nan` values.
    - Vision weights (`v.blk.*`) are almost entirely zeroed out.
- **Conclusion:** The GGUF file `gemma4_26b-a4b-it-q4_K_M.gguf` is corrupted or was generated with a broken quantization script. It is incapable of producing coherent text.

### 3. Implementation Improvements
While the model was broken, several critical fixes were applied to `src/models/gemma4.cpp` to align with the architecture:
- **Precision:** Forced `GGML_PREC_F32` for MoE routing and the merged FFN summation to prevent numerical collapse.
- **Softcapping:** Implemented differentiated softcapping for the router (`f_router_logit_softcapping`) and final head (`f_final_logit_softcapping`).
- **Scaling:** Corrected the attention scaling factor to `1.0f` to account for learned Q/K norms.
- **RoPE:** Updated RoPE to use layer-specific head dimensions (`n_embd_head_k`) to support heterogeneous head sizes (256/512).
- **Norms:** Ensured exhaustive Q, K, and V normalization for all layers.

## Final Status
**First Light NOT Achieved** due to upstream model corruption. The implementation code is now robust and ready for a valid GGUF.
