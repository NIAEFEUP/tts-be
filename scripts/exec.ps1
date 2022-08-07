# Deteling Data file. 
if (Test-Path  -Path './mysql/data/') {
    Write-Output ">> Removing ./mysql/data/ folder..." 
    Remove-Item -Recurse -Force './mysql/data/*'
} 

# Create tts_bridge network 
$DockerNetworks = docker network ls
$TTSNetwork = $DockerNetworks | Select-String 'tts_bridge '
if (-Not $TTSNetwork) {
    Write-Output ">> Missing tts_bridge network. Creating..."  
    docker network create 'tts_bridge'
} else {
    Write-Output "Detected tts_bridge network!"
}


Write-Output ">> Formating ./django/entrypoint.sh file..."
$EntrypointPath =  '.\django\entrypoint.sh' 
$result = Get-Content -Raw -Path $EntrypointPath
$result | ForEach-Object {$_ -replace "[`r`n]+", "`n"} | Set-Content $EntrypointPath

Write-Output ">> Removing old containers..."
docker compose down
Write-Output ">> Initializing docker..."
docker compose up --build 