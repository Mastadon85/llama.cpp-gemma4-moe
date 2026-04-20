# Audit Log: Qwen 3.6 Substation (2026-04-19)

## 1. Hardware & Environment
*   **GPU**: NVIDIA RTX 3090 (24GB VRAM).
*   **System RAM**: 32GB (Baseline usage: 6.3GB).
*   **Status**: VRAM fragmentation managed; no current "spillage" into shared memory at 128k context.
*   **OS**: Windows 11 (PowerShell 5.1/7.x).

## 2. Software Architecture
*   **Core**: Customized `llama.cpp` with Attention Matching (AM) and Turbo4 (Delta-KV).
*   **Entry Point**: `launch_substation_full.bat` (Orchestrates Server + Client).
*   **Server Config**: `llama.cpp\start-qwen-substation.ps1`.
*   **Client**: `qwen-chat.py` (API-based, streaming, `/load` support, live progress bar).

## 3. Successes to Date
*   **RAM Reclamation**: Reclaimed ~16GB of System RAM by disabling the 8GB prompt-cache (`--cache-ram 0`) and pinning weights (`--mlock`).
*   **Stability**: Eliminated `cudaMalloc` and `invalid argument` errors across the stack.
*   **Visibility**: Created a high-signal chat UI with ingestion progress and tokens-per-second analytics.

## 4. Current Bottleneck: The "Ingestion Wall"
*   **Symptoms**: 
    *   CPU: 100% pegged during ingestion.
    *   Speed: ~66 t/s (12-15% of 40k file per minute).
    *   GPU: Underutilized at 22%.
*   **Hypothesis**: The 35B MoE architecture (256 experts) is forcing expert-routing or compute-buffer math onto the CPU, possibly due to a Flash Attention fallback or thread contention on Windows.

## 5. Troubleshooting Vector for Next Session
1.  **MoE Expert Pinning**: Verify if all 256 experts are truly on the 3090.
2.  **PCIe Throughput**: Check if the `--no-mmap` + `--mlock` combo is causing bus contention.
3.  **Tokenizer Bottleneck**: Test if large JSON payloads are stalling the server's parser.
4.  **AM-Solver**: Check for premature CPU-based OLS solver triggers.
