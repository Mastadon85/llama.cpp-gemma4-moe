# Qwen 3.6-35B-A3B Commissioning Report (V1)

## Status: SUCCESS
- **Verification:** Needle found at 142 days in context.
- **Environment:** RTX 3090 (24GB VRAM).

## Current Performance (Baseline)
- **Ingestion:** 23.6 t/s
- **Generation:** 1.7 t/s
- **Bottleneck:** PCIe Pillage (System RAM offloading) due to KV cache size exceeding VRAM.

## Resource Allocation
- **VRAM Hard Cap:** 24.0 GB
- **Model Weights (Q3_K_M):** ~15.3 GB
- **Available for KV Cache:** ~7.7 GB
- **Target Goal:** >20 t/s Generation by staying strictly within VRAM.

## Strategy: Delta-KV "VRAM-Lock"
1. **4-bit Delta-KV Compression:** Implement `--cache-type-k turbo4` and `--cache-type-v turbo4`.
2. **Dynamic Context Calculation:** Automatically limit `--ctx-size` to fit the ~7.7 GB VRAM budget.
3. **Synergy:** Combine Attention Matching (structural compaction) with Delta-KV (bit-level compression).
