# Script de démarrage pour le backend
# Usage: python start_backend.py

import os
import sys
import subprocess
from pathlib import Path

def check_env_file():
    """Vérifie si le fichier .env existe et contient la clé API"""
    env_path = Path(__file__).parent.parent / '.env'
    
    if not env_path.exists():
        print("❌ Fichier .env non trouvé!")
        print("📝 Copiez .env.example vers .env et configurez votre GOOGLE_API_KEY")
        return False
    
    with open(env_path, 'r') as f:
        content = f.read()
        if 'your_google_api_key_here' in content:
            print("⚠️  ATTENTION: Vous devez configurer votre GOOGLE_API_KEY dans le fichier .env")
            print("   Remplacez 'your_google_api_key_here' par votre vraie clé API Google Gemini")
            return False
    
    print("✅ Fichier .env configuré")
    return True

def check_dependencies():
    """Vérifie si les dépendances sont installées"""
    try:
        import fastapi
        import uvicorn
        print("✅ Dépendances de base installées")
        return True
    except ImportError:
        print("❌ Dépendances manquantes!")
        print("📦 Installez-les avec: pip install -r requirements.txt")
        return False

def start_server():
    """Démarre le serveur FastAPI"""
    print("\n🚀 Démarrage du serveur backend...")
    print("📍 URL: http://localhost:8000")
    print("📚 Documentation: http://localhost:8000/docs")
    print("\n⏹️  Appuyez sur Ctrl+C pour arrêter\n")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Serveur arrêté")

if __name__ == "__main__":
    print("=" * 60)
    print("🔬 Intelligent Research Assistant - Backend")
    print("=" * 60)
    print()
    
    if not check_env_file():
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    start_server()
