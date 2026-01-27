# Backend - Intelligent Research Assistant

## 🚀 Démarrage Rapide

### Option 1: Démarrage Local (Recommandé pour le développement)

1. **Installer les dépendances**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configurer l'environnement**
   ```bash
   # Depuis la racine du projet
   cp .env.example .env
   # Éditez .env et ajoutez votre GOOGLE_API_KEY
   ```

3. **Démarrer le serveur**
   ```bash
   # Option A: Avec le script Python
   python start_backend.py
   
   # Option B: Directement avec uvicorn
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Accéder à l'application**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Option 2: Avec Docker

```bash
# Depuis la racine du projet
docker-compose up --build backend
```

## 🔧 Résolution des Problèmes

### Problème: Erreur AttributeError avec torch/sentence-transformers

**Symptôme:**
```
AttributeError: module 'torch.utils' has no attribute '_register_pytree_node'
```

**Solution:**
Les versions de `torch` et `sentence-transformers` ont été mises à jour pour être compatibles:
- torch: 2.1.2 → 2.2.0
- sentence-transformers: 2.3.1 → 2.6.0

Reconstruisez l'image Docker:
```bash
docker-compose down
docker-compose build --no-cache backend
docker-compose up backend
```

### Problème: Le backend ne démarre pas

**Vérifications:**

1. **Clé API Google Gemini**
   ```bash
   # Vérifiez que votre .env contient une vraie clé API
   cat ../.env | grep GOOGLE_API_KEY
   ```

2. **Dépendances Python**
   ```bash
   pip list | grep -E "fastapi|uvicorn|torch|sentence-transformers"
   ```

3. **Port déjà utilisé**
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Linux/Mac
   lsof -i :8000
   ```

### Problème: Timeout lors de l'installation des dépendances

**Solution:**
Utilisez la version simplifiée pour tester:
```bash
pip install -r requirements-simple.txt
```

Ou installez les dépendances lourdes séparément:
```bash
# 1. PyTorch CPU (plus léger)
pip install torch==2.2.0 --index-url https://download.pytorch.org/whl/cpu

# 2. Sentence Transformers
pip install sentence-transformers==2.6.0

# 3. Autres dépendances
pip install -r requirements.txt
```

### Problème: Erreur de mémoire lors du build Docker

**Solution:**
Augmentez la mémoire allouée à Docker:
- Docker Desktop → Settings → Resources → Memory: 4GB minimum

Ou utilisez le Dockerfile optimisé:
```bash
docker build -f Dockerfile.optimized -t research-assistant-backend .
```

## 📦 Versions des Dépendances

### Principales Dépendances

| Package | Version | Description |
|---------|---------|-------------|
| FastAPI | 0.109.0 | Framework web |
| Uvicorn | 0.27.0 | Serveur ASGI |
| PyTorch | 2.2.0 | ML Framework (CPU) |
| Sentence-Transformers | 2.6.0 | Embeddings |
| ChromaDB | 0.4.22 | Vector Store |
| LangChain | >=0.1.0 | LLM Framework |
| Google Generative AI | 0.4.0 | Gemini API |

### Compatibilité

- Python: 3.11+
- OS: Windows, Linux, macOS
- Docker: 20.10+

## 🔐 Configuration

### Variables d'Environnement

Créez un fichier `.env` à la racine du projet:

```env
# Google Gemini API
GOOGLE_API_KEY=votre_clé_api_ici

# Vector Store
VECTOR_STORE_TYPE=chroma
CHROMA_PERSIST_DIRECTORY=./data/vector_store

# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DEVICE=cpu

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# CORS
ALLOWED_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
```

## 🧪 Tests

```bash
# Tests unitaires
pytest tests/ -v

# Tests avec couverture
pytest tests/ --cov=app --cov-report=html

# Test de santé de l'API
curl http://localhost:8000/health/
```

## 📝 Structure du Projet

```
backend/
├── app/
│   ├── api/           # Endpoints API
│   ├── core/          # Configuration et utilitaires
│   ├── models/        # Modèles de données
│   ├── services/      # Logique métier
│   └── main.py        # Point d'entrée
├── data/              # Données et stockage
├── tests/             # Tests
├── requirements.txt   # Dépendances complètes
├── requirements-simple.txt  # Dépendances minimales
├── Dockerfile         # Image Docker
├── Dockerfile.optimized     # Image Docker optimisée
└── start_backend.py   # Script de démarrage
```

## 🆘 Support

Si vous rencontrez des problèmes:

1. Vérifiez les logs: `docker-compose logs backend`
2. Consultez la documentation: http://localhost:8000/docs
3. Vérifiez les issues GitHub
4. Créez une nouvelle issue avec les détails de l'erreur

## 📚 Ressources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Google Gemini API](https://ai.google.dev/)
- [LangChain Documentation](https://python.langchain.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
