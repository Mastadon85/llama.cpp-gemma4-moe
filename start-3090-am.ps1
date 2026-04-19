# Gemma 4 26B Optimized Launch Script (3090 Basement Rig)
$ServerPath = ".\llama.cpp\build\bin\Release\llama-server.exe"
$ModelPath = "C:\Users\Don\Documents\Projects\Attention_Matching\models\gemma4_26b-a4b-it-q4_K_M.gguf"

$Args = @(
    "-m", $ModelPath,
    "--ctx-size", "65536",         # 64k - The "Goldilocks" zone for your 3090
    "--n-gpu-layers", "99",        # Full offload
    "--compact",                   # Enable Attention Matching
    "--compact-ratio", "0.5",      # 50% cache compression
    "--flash-attn", "on",
    "--mlock",                     # Pin weights to VRAM/RAM
    "--host", "0.0.0.0",           # Open for SSH Tunnel
    "--port", "11434"              # Matches your Laptop Tunnel/Ollama port
)

Write-Host "Basement Rig: Launching Gemma 4 (26B MoE) with AM Compaction..." -ForegroundColor Green
& $ServerPath @Args