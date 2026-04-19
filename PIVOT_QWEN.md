# Pivot: Qwen 3.6 1M Context via Attention Matching (AM)

## Repository Rebranding
This repository has pivoted from its original focus as a Gemma fork to a dedicated research branch for **Attention Matching (AM) KV Compaction** targeting the **Qwen 3.6 (LLM_ARCH_QWEN2)** architecture.

## The Goal
The primary mission is to achieve a **1,000,000 token context window** on a single consumer-grade GPU (e.g., NVIDIA RTX 3090 24GB).

## Hamilton Hybrid Architecture
This implementation utilizes the "Hamilton Hybrid" approach, which combines:
1.  **GQA-Aware Compaction:** Matching the 8 query heads into the 2 KV heads using Ordinary Least Squares (OLS) fitting (proxied via high-precision pooled averaging).
2.  **Precision Safeguards:** Enforced `GGML_PREC_F32` for the MoE router and AM fitting routines to prevent rounding instability at extreme context depths.
3.  **Governance Bypass:** Surgical overrides of metadata-enforced context limits (256k -> 1M) and server-side slot capping.
4.  **Architectural Integrity:** Native support for Qwen2/Qwen3 logit softcapping and Q/K normalization preserved within the computation graph.

## Configuration
- `--compact`: Enable Attention Matching KV Compaction.
- `--compact-ratio <N>`: Set the compaction ratio (default: 4, capable of 8+).

## Research Status
The AM-graft is fully integrated into the `llama.cpp` core. Verification and performance benchmarking for the 1M token envelope are ongoing.
