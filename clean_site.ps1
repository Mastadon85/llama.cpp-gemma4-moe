$projectRoot = "C:\Users\Don\Documents\Projects\Attention_Matching"
$buildDir = "$projectRoot\llama.cpp\build"
$modelFile = "$projectRoot\models\gemma4_26b-a4b-it-q4_K_M.gguf"

Write-Host "--- Cleaning Site ---" -ForegroundColor Yellow

if (Test-Path $buildDir) {
    Write-Host "Removing build folder: $buildDir"
    Remove-Item -Path $buildDir -Recurse -Force
}

if (Test-Path $modelFile) {
    Write-Host "Removing corrupted model blob: $modelFile"
    Remove-Item -Path $modelFile -Force
}

Write-Host "Site Cleaned. Ready for fresh assets." -ForegroundColor Green
