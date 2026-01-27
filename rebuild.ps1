# Script de reconstruction rapide
# Usage: .\rebuild.ps1

param(
    [switch]$NoCache = $false,
    [switch]$BackendOnly = $false,
    [switch]$FrontendOnly = $false
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Reconstruction de l'Application" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Arrêter les conteneurs existants
Write-Host "🛑 Arrêt des conteneurs..." -ForegroundColor Yellow
docker-compose down 2>&1 | Out-Null
Write-Host "✅ Conteneurs arrêtés" -ForegroundColor Green
Write-Host ""

# Options de build
$buildArgs = @()
if ($NoCache) {
    $buildArgs += "--no-cache"
    Write-Host "🔄 Mode: Reconstruction complète (sans cache)" -ForegroundColor Yellow
} else {
    Write-Host "🔄 Mode: Reconstruction avec cache" -ForegroundColor Yellow
}

# Sélection du service
$service = ""
if ($BackendOnly) {
    $service = "backend"
    Write-Host "🎯 Cible: Backend uniquement" -ForegroundColor Yellow
} elseif ($FrontendOnly) {
    $service = "frontend"
    Write-Host "🎯 Cible: Frontend uniquement" -ForegroundColor Yellow
} else {
    Write-Host "🎯 Cible: Tous les services" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🏗️  Construction en cours..." -ForegroundColor Cyan
Write-Host ""

# Construire
if ($service) {
    docker-compose build $buildArgs $service
} else {
    docker-compose build $buildArgs
}

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Construction réussie!" -ForegroundColor Green
    Write-Host ""
    
    $start = Read-Host "Voulez-vous démarrer l'application maintenant? (O/n)"
    if ($start -ne "n" -and $start -ne "N") {
        Write-Host ""
        Write-Host "🚀 Démarrage..." -ForegroundColor Cyan
        Write-Host ""
        docker-compose up
    }
} else {
    Write-Host ""
    Write-Host "❌ Erreur lors de la construction!" -ForegroundColor Red
    Write-Host "📝 Consultez les logs ci-dessus" -ForegroundColor Yellow
    exit 1
}
