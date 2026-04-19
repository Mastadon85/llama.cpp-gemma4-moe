$ErrorActionPreference = "Continue"
$projectRoot = "C:\Users\Don\Documents\Projects\Attention_Matching\llama.cpp"
$buildDir = "$projectRoot\build"
$modelPath = "C:\Users\Don\Documents\Projects\Attention_Matching\models\gemma4_26b-a4b-it-q4_K_M.gguf"
$logFile = "$PSScriptRoot\server_verify.log"

Write-Host "--- Step 1: Building llama.cpp ---"
Set-Location $buildDir
cmake --build . --config Release -j 16

Write-Host "--- Step 2: Starting llama-server ---"
# Start server and redirect output to a file for debugging
$serverProcess = Start-Process -FilePath ".\bin\Release\llama-server.exe" -ArgumentList "-m `"$modelPath`"", "--port 11434", "--n-gpu-layers 99", "--ctx-size 4096" -PassThru -WindowStyle Hidden -RedirectStandardOutput $logFile -RedirectStandardError $logFile

Write-Host "Waiting for server to be ready (health check)..."
$ready = $false
$maxRetries = 60
$count = 0

while (-not $ready -and $count -lt $maxRetries) {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:11434/health" -Method Get -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            $ready = $true
            Write-Host "Server is healthy!"
        }
    } catch {
        # Port might not be open yet
    }
    if (-not $ready) {
        $count++
        Start-Sleep -Seconds 5
    }
}

if (-not $ready) {
    Write-Host "Server health check timed out. Check $logFile for details."
    Stop-Process -Id $serverProcess.Id -Force
    exit 1
}

Write-Host "--- Step 3: Sending Test Inference Request ---"
$body = @{
    messages = @(
        @{ role = "user"; content = "Explain the benefit of a 128-expert MoE architecture in one concise sentence." }
    )
    max_tokens = 50
    stream = $false
} | ConvertTo-Json

$requestCount = 0
$requestSuccess = $false
while (-not $requestSuccess -and $requestCount -lt 10) {
    try {
        $response = Invoke-RestMethod -Uri "http://127.0.0.1:11434/v1/chat/completions" -Method Post -Body $body -ContentType "application/json"
        $text = $response.choices[0].message.content
        Write-Host "Model Response: $text"

        if ($text -match "<unused>" -or $text.Length -lt 10) {
            Write-Host "Verification Failed: Output contains static or is too short."
        } else {
            Write-Host "First Light Achieved"
            $requestSuccess = $true
        }
    } catch {
        Write-Host "Request attempt $($requestCount+1) failed: $($_.Exception.Message)"
        $requestCount++
        Start-Sleep -Seconds 5
    }
}

Write-Host "--- Step 4: Cleaning up (Stopping Server) ---"
Stop-Process -Id $serverProcess.Id -Force
