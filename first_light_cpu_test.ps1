$buildDir = "C:\Users\Don\Documents\Projects\Attention_Matching\llama.cpp\build"
$modelPath = "C:\Users\Don\Documents\Projects\Attention_Matching\models\gemma4_26b-a4b-it-q4_K_M.gguf"
$serverExe = "$buildDir\bin\Release\llama-server.exe"

Write-Host "--- Step 1: Building llama.cpp (CPU Only) ---"
Push-Location $buildDir
cmake --build . --config Release -j 16
Pop-Location

Write-Host "--- Step 2: Starting llama-server (CPU) ---"
$serverArgs = @(
    "-m", $modelPath,
    "--port", "11434",
    "--n-gpu-layers", "0",
    "--ctx-size", "4096",
    "--compact",
    "--compact-ratio", "0.5",
    "--mlock",
    "--log-disable"
)

$serverProcess = Start-Process -FilePath $serverExe -ArgumentList $serverArgs -NoNewWindow -PassThru

$maxRetries = 60
$retryCount = 0
$serverReady = $false
Write-Host "Waiting for server..."
while (-not $serverReady -and $retryCount -lt $maxRetries) {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:11434/health" -Method Get -ErrorAction Stop
        $serverReady = $true
    } catch {
        $retryCount++
        Start-Sleep -Seconds 2
    }
}

if (-not $serverReady) {
    Write-Error "Server timeout."
    Stop-Process -Id $serverProcess.Id -Force
    exit 1
}

Write-Host "--- Step 3: Sending Test Prompt ---"
$body = @{
    messages = @(
        @{ role = "user"; content = "Explain the benefit of a 128-expert MoE architecture in one concise sentence." }
    )
    max_tokens = 128
    temperature = 0.0
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:11434/v1/chat/completions" -Method Post -Body $body -ContentType "application/json"
    $content = $response.choices[0].message.content
    Write-Host "Response: $content"

    if ($content -like "*<unused*" -or $content.Length -lt 20) {
        Write-Host "Result: Output is still problematic."
    } elseif ($content -match "[a-zA-Z]{3,}\s+[a-zA-Z]{2,}\s+[a-zA-Z]{3,}") {
        Write-Host "First Light Achieved"
    } else {
        Write-Host "Result: Response is incoherent."
    }
} catch {
    Write-Error "Inference failed: $_"
}

Write-Host "--- Step 4: Cleanup ---"
Stop-Process -Id $serverProcess.Id -Force
