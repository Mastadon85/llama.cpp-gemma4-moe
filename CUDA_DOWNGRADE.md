# CUDA Downgrade Instructions (RTX 3090)

## Objective
Downgrade from CUDA 13.2 to a stable version (12.8 or 12.4.1) to resolve numerical instability and infinite loops in Gemma 4 GGUF models.

## Steps

1. **Download Requisites:**
   - **DDU (Display Driver Uninstaller):** [Official Guru3D Link](https://www.guru3d.com/files-details/display-driver-uninstaller-download.html).
   - **Stable Driver:** Download the NVIDIA Studio or Game Ready Driver (v560.xx or similar) which packages **CUDA 12.8**.
   - **CUDA Toolkit 12.8:** [NVIDIA Archive](https://developer.nvidia.com/cuda-downloads).

2. **Clean Uninstall (Safe Mode):**
   - **Disconnect Internet** (Prevents Windows Update from interfering).
   - Reboot into **Safe Mode**.
   - Run **DDU**, select "GPU" and "NVIDIA".
   - Click **Clean and Restart**.

3. **Install Stable Version:**
   - Install the NVIDIA Driver downloaded in Step 1.
   - Install the CUDA Toolkit 12.8.
   - Reboot.

4. **Verify:**
   - Open terminal and run: `nvcc --version`.
   - Ensure it reports `release 12.8` (or your chosen 12.x version).
