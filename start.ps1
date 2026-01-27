# Script de démarrage pour Windows
# Usage: .\start.ps1

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Intelligent Research Assistant - Démarrage" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier si .env existe
$envFile = ".\.env"
if (-Not (Test-Path $envFile)) {
    Write-Host "❌ Fichier .env non trouvé!" -ForegroundColor Red
    Write-Host "📝 Création du fichier .env depuis .env.example..." -ForegroundColor Yellow
    Copy-Item ".\.env.example" $envFile
    Write-Host "✅ Fichier .env créé" -ForegroundColor Green
    Write-Host "⚠️  IMPORTANT: Éditez le fichier .env et ajoutez votre GOOGLE_API_KEY" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Appuyez sur Entrée après avoir configuré votre clé API"
}

# Vérifier la clé API
$envContent = Get-Content $envFile -Raw
if ($envContent -match "your_google_api_key_here") {
    Write-Host "⚠️  ATTENTION: Vous devez configurer votre GOOGLE_API_KEY dans .env" -ForegroundColor Yellow
    Write-Host "   Ouvrez le fichier .env et remplacez 'your_google_api_key_here'" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Voulez-vous continuer quand même? (o/N)"
    if ($continue -ne "o" -and $continue -ne "O") {
        exit 1
    }
}

Write-Host "🔍 Vérification de Docker..." -ForegroundColor Cyan
$dockerRunning = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker n'est pas en cours d'exécution!" -ForegroundColor Red
    Write-Host "📝 Veuillez démarrer Docker Desktop" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Docker est en cours d'exécution" -ForegroundColor Green
Write-Host ""

Write-Host "🧹 Nettoyage des anciens conteneurs..." -ForegroundColor Cyan
docker-compose down 2>&1 | Out-Null
Write-Host "✅ Nettoyage terminé" -ForegroundColor Green
Write-Host ""

Write-Host "🏗️  Construction des images Docker..." -ForegroundColor Cyan
Write-Host "⏳ Cela peut prendre plusieurs minutes la première fois..." -ForegroundColor Yellow
Write-Host ""

docker-compose build --no-cache

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Erreur lors de la construction!" -ForegroundColor Red
    Write-Host "📝 Consultez les logs ci-dessus pour plus de détails" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "✅ Construction terminée avec succès!" -ForegroundColor Green
Write-Host ""

Write-Host "🚀 Démarrage des services..." -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 URLs d'accès:" -ForegroundColor Yellow
Write-Host "   - Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   - Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   - Documentation API: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "⏹️  Appuyez sur Ctrl+C pour arrêter" -ForegroundColor Yellow
Write-Host ""

docker-compose up

Write-Host ""
Write-Host "👋 Services arrêtés" -ForegroundColor Cyan
