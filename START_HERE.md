# 🎯 INSTRUCTIONS DE DÉMARRAGE - LISEZ-MOI EN PREMIER

## ⚡ Démarrage Rapide (3 minutes)

### Étape 1: Configurer la Clé API (1 min)

1. Ouvrez le fichier `.env` à la racine du projet
2. Remplacez cette ligne:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   ```
   Par:
   ```
   GOOGLE_API_KEY=votre_vraie_clé_api
   ```

**Où obtenir une clé API?**
👉 https://makersuite.google.com/app/apikey

### Étape 2: Démarrer l'Application (2 min)

**Option A: Avec le script automatique (Recommandé)**
```powershell
.\start.ps1
```

**Option B: Manuellement**
```powershell
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Étape 3: Accéder à l'Application

Une fois démarré (attendez ~2 minutes):
- 🌐 **Frontend**: http://localhost:3000
- 🔧 **Backend API**: http://localhost:8000
- 📚 **Documentation**: http://localhost:8000/docs

## 🔧 Ce Qui a Été Corrigé

### ❌ Problème Original
Le backend ne démarrait pas avec cette erreur:
```
AttributeError: module 'torch.utils' has no attribute '_register_pytree_node'
```

### ✅ Solution Appliquée
- Mise à jour de PyTorch: 2.1.2 → 2.2.0
- Mise à jour de sentence-transformers: 2.3.1 → 2.6.0
- Optimisation du Dockerfile
- Ajout de scripts de démarrage automatiques

## 📁 Nouveaux Fichiers Créés

| Fichier | Description |
|---------|-------------|
| `QUICKSTART.md` | Guide de démarrage détaillé |
| `CHANGELOG.md` | Résumé complet des modifications |
| `start.ps1` | Script de démarrage automatique |
| `rebuild.ps1` | Script de reconstruction |
| `backend/README.md` | Documentation du backend |
| `backend/start_backend.py` | Démarrage local du backend |

## ⚠️ Problèmes Courants

### "Docker n'est pas en cours d'exécution"
➡️ Démarrez Docker Desktop et attendez qu'il soit prêt

### "Port 8000 already in use"
➡️ Exécutez:
```powershell
netstat -ano | findstr :8000
taskkill /PID <numéro_trouvé> /F
```

### "Erreur de build Docker"
➡️ Augmentez la mémoire Docker:
- Docker Desktop → Settings → Resources → Memory: 4GB minimum

### "Service not ready: Google API key not configured"
➡️ Vérifiez que vous avez bien configuré votre clé API dans `.env`

## 📖 Documentation Complète

Pour plus de détails, consultez:
- **Guide rapide**: `QUICKSTART.md`
- **Modifications**: `CHANGELOG.md`
- **Backend**: `backend/README.md`
- **README principal**: `README.md`

## 🚀 Commandes Utiles

```powershell
# Démarrer l'application
.\start.ps1

# Reconstruire sans cache
.\rebuild.ps1 -NoCache

# Reconstruire uniquement le backend
.\rebuild.ps1 -BackendOnly -NoCache

# Voir les logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Arrêter l'application
docker-compose down

# Nettoyer complètement
docker-compose down -v
docker system prune -a
```

## ✅ Vérification du Fonctionnement

### Test 1: Backend
```powershell
curl http://localhost:8000/health/
```
Devrait retourner: `{"status":"healthy",...}`

### Test 2: Frontend
Ouvrez http://localhost:3000 dans votre navigateur

### Test 3: Documentation API
Visitez http://localhost:8000/docs

## 🎯 Prochaines Étapes

1. ✅ Configurez votre clé API
2. ✅ Démarrez l'application avec `.\start.ps1`
3. ✅ Testez en uploadant un document
4. ✅ Posez une question dans le chat
5. ✅ Explorez la documentation API

## 🆘 Besoin d'Aide?

1. Consultez `QUICKSTART.md` pour les solutions détaillées
2. Vérifiez les logs: `docker-compose logs backend`
3. Lisez `backend/README.md` pour le dépannage du backend

---

**Temps de démarrage estimé**: 2-5 minutes (première fois: 10-15 minutes pour le build)

**Prêt à commencer?** Lancez `.\start.ps1` ! 🚀
