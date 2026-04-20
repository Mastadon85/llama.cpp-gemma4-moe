@echo off
SET PROJECT_ROOT=%~dp0
SET API_SCRIPT="%PROJECT_ROOT%llama.cpp\start-qwen-api.ps1"

echo ========================================
echo   QWEN SUBSTATION - API ONLY MODE
echo ========================================
echo.

:CONTEXT_MENU
echo [1] SELECT CONTEXT SIZE:
echo 1. 128k (Standard)
echo 2. 256k (Advanced)
echo 3. 440k (Extreme - 3090 Redline)
echo 4. Custom (Manual Input)
set /p ctx_choice="Enter choice (1-4) [1]: "
if "%ctx_choice%"=="" set ctx_choice=1
if "%ctx_choice%"=="1" set FINAL_CTX=131072
if "%ctx_choice%"=="2" set FINAL_CTX=262144
if "%ctx_choice%"=="3" set FINAL_CTX=450560
if "%ctx_choice%"=="4" (
    set /p FINAL_CTX="Enter custom token count: "
)
echo.

:CACHE_MENU
echo [2] SELECT CACHE MODE:
echo 1. Q8 Balanced (Recommended)
echo 2. f16 Baseline (High VRAM)
set /p cache_choice="Enter choice (1-2) [1]: "
if "%cache_choice%"=="" set cache_choice=1
if "%cache_choice%"=="1" set FINAL_CACHE=q8_0
if "%cache_choice%"=="2" set FINAL_CACHE=f16
echo.

:AM_MENU
echo [3] SELECT ATTENTION MATCHING (AM):
echo 1. ON (Threshold 10k)
echo 2. OFF (Standard Attention)
set /p am_choice="Enter choice (1-2) [1]: "
if "%am_choice%"=="" set am_choice=1
if "%am_choice%"=="1" set FINAL_AM=10000
if "%am_choice%"=="2" set FINAL_AM=999999
echo.

echo --- INITIALIZING API SERVER ---
echo Settings: %FINAL_CTX% tokens, %FINAL_CACHE% cache, AM=%FINAL_AM%
powershell.exe -ExecutionPolicy Bypass -File %API_SCRIPT% -CacheType %FINAL_CACHE% -AMTrigger %FINAL_AM% -CtxSize %FINAL_CTX%

pause
