# Test RAG et LLM - Instructions

## Test du Backend FastAPI

Le backend fonctionne déjà sur http://localhost:8000

### 1. Test Health Endpoint
```bash
curl http://localhost:8000/health
```

### 2. Test Chat Endpoint (LLM)
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Comment gérer le stress pendant les examens?"}'
```

### 3. Test Resources Endpoint
```bash
curl http://localhost:8000/api/resources
```

### 4. Test Tasks Endpoint
```bash
curl http://localhost:8000/api/tasks
```

## Test du Frontend

Frontend: http://localhost:5173

### 1. Test Dashboard
- Allez sur http://localhost:5173
- Vérifiez que le dashboard s'affiche

### 2. Test Navigation
- Cliquez sur chaque lien de la navbar:
  - Dashboard
  - Mood check-in
  - AI assistant
  - Technical PFE
  - Women's Wellbeing
  - Study planner
  - Calendar
  - Resources
  - Breathing
  - Settings
  - Support

### 3. Test Calendar
- Allez sur /calendar
- Ajoutez un événement
- Vérifiez qu'il s'affiche

### 4. Test AI Assistant
- Allez sur /assistant
- Posez une question
- Vérifiez la réponse

## Test RAG (nécessite PostgreSQL + AI Service)

Pour tester le RAG complet:

1. Installer PostgreSQL avec pgvector
2. Démarrer l'AI Service (ai-service)
3. Ingestionner des documents
4. Tester la recherche sémantique

Pour l'instant, le FastAPI backend utilise:
- Mock LLM (si pas de clé API)
- RAG par mots-clés (pas de vecteurs)
- SQLite local

## Configuration LLM

Pour activer un vrai LLM, ajoutez dans backend/.env:

```
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
ANTHROPIC_API_KEY=sk-ant-...
```

Le backend utilisera automatiquement le premier disponible.
