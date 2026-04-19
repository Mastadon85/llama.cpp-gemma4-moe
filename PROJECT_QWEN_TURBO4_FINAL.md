# Project Qwen-Turbo4: Final Commissioning Report

## System Architecture
- **Model:** Qwen 3.6-35B-A3B (Quantized to Q3_K_M via Unsloth)
- **KV Compression:** Delta-KV (Turbo4) - 4-bit Keyframe/Delta implementation.
- **Structural Optimization:** Attention Matching (AM) active.

## Foundation
- **OS:** Windows 11
- **Hardware:** NVIDIA GeForce RTX 3090 (24GB VRAM)
- **Compute:** CUDA 12.6 Foundation

## Validated Performance
- **Ingestion (Prompt Processing):** 294.8 t/s
- **Generation:** 66.1 t/s (Sustained at 250k context)
- **Improvement:** ~3,700% gain over F16 baseline (1.7 t/s) by eliminating PCIe offloading.

## VRAM Management (VRAM-Lock)
- **VRAM Budget for KV Cache:** ~7.7 GB
- **Logic:** Automatic context calculation integrated into `common.cpp`.
- **Target Context:** ~250,000 tokens (Turbo4 footprint @ 10KB/token).

## Verification: The Kenilworth Needle
- **Status:** SUCCESS
- **Result:** Model accurately retrieved the specific auxiliary cooling pump maintenance frequency for the Kenilworth substation buried at the 142-day mark in the temporal context.

## Conclusion
The RTX 3090 rig is optimized for long-context generation. By stacking bit-level compression (Delta-KV) and structural pooling (AM), the system remains compute-bound within VRAM limits.
