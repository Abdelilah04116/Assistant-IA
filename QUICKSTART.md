# 🚀 Guide de Démarrage Rapide

## Problème Résolu ✅

Le backend ne démarrait pas à cause d'un **conflit de versions** entre PyTorch et sentence-transformers.

### Modifications Apportées

1. **Mise à jour des dépendances** (`requirements.txt`)
   - PyTorch: 2.1.2 → 2.2.0
   - Sentence-Transformers: 2.3.1 → 2.6.0
   - ChromaDB: 0.4.18 → 0.4.22
   - Autres packages mis à jour pour compatibilité

2. **Dockerfile optimisé**
   - Installation par étapes pour éviter les timeouts
   - Meilleure gestion de la mémoire
   - Versions compatibles

3. **Scripts de démarrage**
   - `start.ps1`: Script PowerShell pour Windows
   - `backend/start_backend.py`: Démarrage local du backend

## 🎯 Démarrage en 3 Étapes

### Étape 1: Configuration de la Clé API

```bash
# Copiez le fichier d'exemple
cp .env.example .env

# Éditez .env et remplacez:
GOOGLE_API_KEY=your_google_api_key_here
# par votre vraie clé API Google Gemini
```

**Comment obtenir une clé API Google Gemini:**
1. Allez sur https://makersuite.google.com/app/apikey
2. Créez une nouvelle clé API
3. Copiez-la dans le fichier `.env`

### Étape 2: Démarrage avec Docker (Recommandé)

**Option A: Avec le script PowerShell (Windows)**
```powershell
.\start.ps1
```

**Option B: Manuellement**
```bash
# Nettoyer les anciens conteneurs
docker-compose down

# Reconstruire et démarrer
docker-compose up --build
```

### Étape 3: Accéder à l'Application

Une fois démarré, ouvrez votre navigateur:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentation API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔧 Démarrage Local (Sans Docker)

Si vous préférez ne pas utiliser Docker:

### Backend

```bash
cd backend

# Installer les dépendances
pip install -r requirements.txt

# Démarrer avec le script
python start_backend.py

# OU directement avec uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend

# Installer les dépendances
npm install

# Démarrer
npm start
```

## ⚠️ Problèmes Courants

### 1. Docker ne démarre pas

**Symptôme:** `docker info` retourne une erreur

**Solution:**
- Démarrez Docker Desktop
- Attendez que Docker soit complètement démarré (icône verte)

### 2. Port déjà utilisé

**Symptôme:** `Error: Port 8000 is already in use`

**Solution Windows:**
```powershell
# Trouver le processus
netstat -ano | findstr :8000

# Tuer le processus (remplacez PID par le numéro trouvé)
taskkill /PID <PID> /F
```

### 3. Erreur de build Docker

**Symptôme:** Timeout ou erreur de mémoire

**Solution:**
1. Augmentez la mémoire Docker (Docker Desktop → Settings → Resources)
2. Utilisez le Dockerfile optimisé:
   ```bash
   cd backend
   docker build -f Dockerfile.optimized -t research-assistant-backend .
   ```

### 4. Clé API invalide

**Symptôme:** Erreur 401 ou 403 lors des requêtes

**Solution:**
- Vérifiez que votre clé API est correcte dans `.env`
- Assurez-vous que l'API Gemini est activée sur votre compte Google Cloud

## 📊 Vérification du Fonctionnement

### Test du Backend

```bash
# Health check
curl http://localhost:8000/health/

# Devrait retourner:
# {"status": "healthy", ...}
```

### Test du Frontend

Ouvrez http://localhost:3000 dans votre navigateur.
Vous devriez voir l'interface de chat.

## 🎨 Nouvelles Fonctionnalités

Les modifications incluent également:

1. **Meilleure gestion des erreurs**
   - Messages d'erreur plus clairs
   - Logs détaillés pour le débogage

2. **Scripts de démarrage**
   - Vérification automatique de la configuration
   - Démarrage simplifié

3. **Documentation améliorée**
   - Guide de dépannage complet
   - Instructions pas à pas

## 📚 Documentation Complète

- **README principal**: `README.md`
- **Backend**: `backend/README.md`
- **Frontend**: `frontend/README.md` (si disponible)

## 🆘 Besoin d'Aide?

Si vous rencontrez toujours des problèmes:

1. **Vérifiez les logs:**
   ```bash
   docker-compose logs backend
   docker-compose logs frontend
   ```

2. **Consultez la documentation:**
   - Backend: `backend/README.md`
   - API: http://localhost:8000/docs

3. **Problèmes connus:**
   - Voir les conversations précédentes pour les solutions aux problèmes GPU/NVIDIA

## 🎯 Prochaines Étapes

Une fois l'application démarrée:

1. **Uploadez des documents** via l'interface
2. **Posez des questions** dans le chat
3. **Explorez l'API** via http://localhost:8000/docs

Bon développement! 🚀
