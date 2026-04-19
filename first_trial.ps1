# Gemma 4 Diagnostic Launch (3090 Basement Rig)
$ServerPath = ".\llama.cpp\build\bin\Release\llama-server.exe"
$ModelPath = "C:\Users\Don\Documents\Projects\Attention_Matching\models\gemma4_26b-a4b-it-q4_K_M.gguf"
$LogFile = "debug_load.log"

$Args = @(
    "-m", $ModelPath,
    "--ctx-size", "32768",
    "--parallel", "1",
    "--n-gpu-layers", "99",
    "--compact",
    "--compact-ratio", "0.5",
    "--flash-attn", "on",
    "--no-mmap",           # Keeps it out of System Managed Cache
    "-fit", "off",         # Bypasses the buggy fitting pass
    "--verbose",           # Shows us every tensor as it loads
    "--port", "11434"
)

Write-Host "Basement Rig: Running Diagnostic Load. Check $LogFile if it exits." -ForegroundColor Yellow
# Running with 2>&1 to catch the silent C++ throw
& $ServerPath @Args 2>&1 | Tee-Object -FilePath $LogFile