# Balance AI 🌸

> **Votre Compagnon de Bien-être Intelligent** pour étudiantes tunisiennes

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![React](https://img.shields.io/badge/React-18.2-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.13-yellow.svg)](https://www.python.org/)

---

## 📖 L'Histoire

**Balance AI** est né d'un besoin urgent observé chez les étudiantes tunisiennes: le stress académique, la pression du PFE, l'anxiété face à l'avenir professionnel, et le manque de soutien psychologique accessible sans stigmatisation.

Notre mission: créer un écosystème numérique holistique qui accompagne les étudiantes tunisiennes dans leur parcours universitaire et personnel, avec empathie, confidentialité et soutien non-diagnostique.

## 🌟 Vision

**Balance AI** offre:

- ✨ **Bien-être émotionnel** - Tracking d'humeur, respiration, ressources de soutien
- 📚 **Organisation académique** - Gestion de tâches, calendrier, planning d'études
- 💻 **Assistant technique PFE** - IA pour debugging, architecture, code review
- 🌸 **Santé féminine** - Cycle tracking (privacy-first)
- 🤝 **Soutien confidentiel** - Chat IA avec RAG, non-diagnostique

## 🎨 Design BalanceAI

Notre design system utilise une palette chaleureuse et apaisante:

- **Palette:** Violet lavender (#B77ACB), Purple (#684477), Peach (#F2D7C4), Sage (#9FB9A7)
- **Typography:** Nunito (body) + Fraunces (headings)
- **Background:** Blobs décoratifs avec blur
- **Cards:** Coins arrondis avec shadow subtil
- **Animations:** fadeUp, pulse, transitions fluides

## 🏗️ Architecture Technique

### Frontend (React + Vite)
- **Framework:** React 18 + Vite
- **Routing:** React Router SPA
- **Icons:** Lucide React
- **Charts:** Recharts
- **API:** Axios avec wrapper centralisé
- **Design:** BalanceAI CSS custom

### Backend (FastAPI + Python)
- **Framework:** FastAPI + Uvicorn
- **Database:** SQLAlchemy + SQLite
- **Auth:** JWT (access token)
- **AI:** LangGraph + LangChain
- **RAG:** sentence-transformers
- **LLM:** Support Gemini/OpenAI/Anthropic/Mock

## 🚀 Fonctionnalités

### ✅ Implémentées
- ✅ **Dashboard** - Vue d'ensemble avec statistiques
- ✅ **Mood Tracking** - Check-in émotionnel quotidien
- ✅ **Tasks Planner** - Gestion des tâches académiques
- ✅ **Calendar** - Calendrier professionnel
- ✅ **Resources** - Bibliothèque éducative RAG
- ✅ **Breathing** - Exercices de respiration
- ✅ **Technical PFE** - Assistant technique IA
- ✅ **AI Voice Assistant** - Avatar avec image professionnelle
- ✅ **Authentication** - Login/Signup avec JWT
- ✅ **RAG** - Retrieval Augmented Generation

### 🔄 En Développement
- 🔄 **TTS Audio** - Synthèse vocale (Piper configuration required)
- 🔄 **LLM Live** - Configuration Gemini API required

## � Installation

### Prérequis
- Node.js 18+
- Python 3.13+
- Git

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Access:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Health: http://localhost:8000/health

## 🔐 Configuration

### Backend (.env)
```env
DATABASE_URL=sqlite:///./herwell.db
LLM_PROVIDER=mock  # or gemini, openai, anthropic
GEMINI_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
CORS_ORIGINS=http://localhost:5173
```

### Authentication
```bash
# Register
POST /api/auth/register
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "User Name"
}

# Login
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}
```

## 🎯 Utilisation

### Mood Tracking
1. Navigate to `/mood`
2. Sélectionnez votre humeur actuelle
3. Ajoutez une note optionnelle
4. Visualisez l'historique

### Tasks Planner
1. Navigate to `/planner`
2. Ajoutez des tâches avec titre, sujet, durée, priorité
3. Marquez les tâches comme complétées
4. Gérez votre charge de travail

### AI Assistant
1. Navigate to `/assistant`
2. Tapez votre question ou utilisez le microphone
3. L'IA répond avec empathie et ressources RAG
4. Non-diagnostique, éducatif seulement

### Technical PFE
1. Navigate to `/technical`
2. Sélectionnez un projet (optionnel)
3. Posez des questions techniques
4. Recevez des réponses avec sources

## 📊 API Endpoints

### Auth
- `POST /api/auth/register` - Créer un compte
- `POST /api/auth/login` - Se connecter
- `GET /api/auth/me` - Profil utilisateur

### Chat
- `POST /api/chat` - Chat IA avec RAG
- `POST /api/voice/chat` - Chat vocal (TTS désactivé)

### Tasks
- `GET /api/tasks` - Lister les tâches
- `POST /api/tasks` - Créer une tâche
- `PUT /api/tasks/{id}` - Mettre à jour une tâche
- `DELETE /api/tasks/{id}` - Supprimer une tâche

### Mood
- `GET /api/mood` - Historique d'humeur
- `POST /api/mood` - Ajouter un check-in

## 🎨 Personnalisation

### Branding
Le branding est configurable dans:
- `frontend/src/App.jsx` - Navbar, footer, page titles
- `frontend/src/styles.css` - Variables CSS BalanceAI
- `backend/app/main.py` - API title

### Avatar
L'avatar image est dans `frontend/public/avatar-woman.jpg`. Remplacez-la avec votre propre image.

## 📝 Développement

### Ajouter une nouvelle page
1. Créer le composant dans `frontend/src/App.jsx`
2. Ajouter la route dans `<Routes>`
3. Ajouter l'item de navigation dans `navItems`

### Ajouter une nouvelle API
1. Créer la fonction dans `backend/app/api/`
2. Ajouter le router dans `backend/app/main.py`
3. Ajouter le modèle SQLAlchemy si nécessaire

## � Sécurité

- ✅ Passwords hashés avec SHA-256
- ✅ JWT tokens avec expiration (7 jours)
- ✅ CORS configuré
- ✅ Input validation avec Pydantic
- ✅ Safety pre/post-check sur l'IA
- ⚠️ Demo mode - Ne pas utiliser en production sans configuration

## � License

MIT License - Voir LICENSE file pour détails

## 🤝 Contribution

Contributions bienvenues! Ouvrez une issue ou un PR.

## � Contact

Pour le support ou questions, contactez l'équipe Balance AI.

---

**Créé avec ❤️ pour les étudiantes tunisiennes**

*Balance AI - Votre Compagnon de Bien-être Intelligent*
