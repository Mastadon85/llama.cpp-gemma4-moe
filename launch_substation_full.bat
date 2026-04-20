@echo off
SET PROJECT_ROOT=%~dp0
SET SERVER_SCRIPT="%PROJECT_ROOT%llama.cpp\start-qwen-substation.ps1"
SET CHAT_SCRIPT="%PROJECT_ROOT%llama.cpp\qwen-terminal.ps1"

echo --- POWERING UP QWEN 3.6 SUBSTATION (440K) ---
echo.
echo Select Configuration:
echo 1. Balanced (Q8 Cache + AM @ 10k) [Recommended]
echo 2. Baseline (f16 Cache + Standard AM)
echo 3. No AM (Q8 Cache + Standard Attention)
echo 4. Deep Save (Turbo4 Cache + AM) [VERY SLOW]
echo.

set /p choice="Enter choice (1-4): "
if "%choice%"=="" set choice=1

set PS_ARGS=
if "%choice%"=="2" set PS_ARGS=-Baseline
if "%choice%"=="3" set PS_ARGS=-NoAM
if "%choice%"=="4" set PS_ARGS=-Turbo4

:: 1. Launch the API Server in a new window
echo [1/2] Energizing VRAM-Lock Server (New Window)...
start "Qwen Substation Server" powershell.exe -ExecutionPolicy Bypass -NoExit -File %SERVER_SCRIPT% %PS_ARGS%

:: 2. Wait for the model to load (Increased for 440k allocation)
echo [2/2] Waiting for 440k VRAM context to stabilize...
timeout /t 15 /nobreak > nul

:: 3. Launch the Chat Terminal
echo --- CONNECTING TERMINAL LINK ---
python qwen-chat.py

pause
