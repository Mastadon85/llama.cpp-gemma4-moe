# Gemma 4 26B Commissioning Guide

## 1. Clean Site
Run `clean_site.ps1` to remove old build artifacts and corrupted model blobs.

## 2. Source Clean GGUF
Run the following command to download the verified Bartowski quant (recommended for RTX 3090 speed):

```powershell
huggingface-cli download bartowski/google_gemma-4-26B-A4B-it-GGUF --include "google_gemma-4-26B-A4B-it-Q4_K_M.gguf" --local-dir C:\Users\Don\Documents\Projects\Attention_Matching\models --local-dir-use-symlinks False
```

## 3. CUDA Downgrade
Follow the instructions in `CUDA_DOWNGRADE.md` to move from CUDA 13.2 to 12.8.

## 4. Build and Verify
1.  **Build:**
    ```powershell
    cd llama.cpp
    mkdir build
    cd build
    cmake .. -DGGML_CUDA=ON -G "Visual Studio 17 2022"
    cmake --build . --config Release -j 16
    ```
2.  **Verify Weights:**
    ```powershell
    .\bin\Release\llama-gguf.exe ..\..\models\google_gemma-4-26B-A4B-it-Q4_K_M.gguf r n | Select-String -Pattern "token_embd.weight" -Context 0,5
    ```
    *Look for normal range values (e.g., -0.05 to 0.05).*

## 5. Launch
Run `start-3090-am.ps1` to begin inference.
