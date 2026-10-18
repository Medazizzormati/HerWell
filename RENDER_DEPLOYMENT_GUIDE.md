# Render Deployment Guide for HERwell AI

## Quick Deployment (Recommended for Hackathon)

### Option 1: Deploy FastAPI Backend (Easiest)

#### 1. Backend Service

On Render Dashboard → New Web Service:

**Configuration:**
- **Name:** `herwell-backend`
- **GitHub Repository:** Medazizzormati/HerWell
- **Branch:** `main`
- **Root Directory:** `backend`
- **Runtime:** Docker
- **Dockerfile Path:** `./Dockerfile`
- **Region:** Frankfurt (EU Central) or Oregon (US West)
- **Plan:** Free (0.1 CPU, 512 MB RAM)

**Environment Variables:**
```
DATABASE_URL=postgresql://your_postgresql_url
CORS_ORIGINS=https://herwell-frontend.onrender.com
OPENAI_API_KEY=your_openai_key (optional)
GEMINI_API_KEY=your_gemini_key (optional)
```

**Wait for deployment** → Backend will be available at: `https://herwell-backend.onrender.com`

#### 2. Frontend Service

New Web Service:

**Configuration:**
- **Name:** `herwell-frontend`
- **GitHub Repository:** Medazizzormati/HerWell
- **Branch:** `main`
- **Root Directory:** `frontend`
- **Runtime:** Docker
- **Dockerfile Path:** `./Dockerfile`
- **Region:** Same as backend
- **Plan:** Free

**Environment Variables:**
```
VITE_API_BASE_URL=https://herwell-backend.onrender.com
```

**Wait for deployment** → Frontend will be available at: `https://herwell-frontend.onrender.com`

---

### Option 2: Deploy Spring Boot Backend (Production Architecture)

#### 1. Backend Service

**Configuration:**
- **Name:** `herwell-backend`
- **GitHub Repository:** Medazizzormati/HerWell
- **Branch:** `main`
- **Root Directory:** `springboot-backend`
- **Runtime:** Docker
- **Dockerfile Path:** `./Dockerfile`
- **Region:** Frankfurt or Oregon
- **Plan:** Standard ($7/month recommended for Java)

**Environment Variables:**
```
DATABASE_URL=jdbc:postgresql://your_postgresql_url
AI_SERVICE_URL=https://herwell-ai-service.onrender.com
JWT_SECRET=your_jwt_secret_here
CORS_ORIGINS=https://herwell-frontend.onrender.com
```

#### 2. AI Service (Optional - for full RAG)

**Configuration:**
- **Name:** `herwell-ai-service`
- **GitHub Repository:** Medazizzormati/HerWell
- **Branch:** `main`
- **Root Directory:** `ai-service`
- **Runtime:** Docker
- **Dockerfile Path:** `./Dockerfile`
- **Region:** Same as backend
- **Plan:** Standard ($7/month)

**Environment Variables:**
```
DATABASE_URL=postgresql://your_postgresql_url
LLM_BASE_URL=https://your_llama_server_url
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

#### 3. Frontend Service

Same as Option 1, but:
```
VITE_API_BASE_URL=https://herwell-backend.onrender.com
```

---

## PostgreSQL Setup

### Option A: Render PostgreSQL (Easiest)

1. On Render → New PostgreSQL
2. **Name:** `herwell-db`
3. **Database:** `herwell`
4. **User:** `herwell`
5. **Plan:** Free
6. Wait for database to be ready
7. Copy connection string from Render dashboard
8. Use as `DATABASE_URL` in backend env vars

### Option B: External PostgreSQL (Aiven, ElephantSQL, etc.)

1. Create free PostgreSQL account
2. Create database
3. Get connection string
4. Use as `DATABASE_URL` in backend env vars

### Option C: SQLite (Local Development Only)

For local testing, the FastAPI backend uses SQLite by default. No setup needed.

---

## LLM Configuration

### Option A: Use API Provider (Recommended for Hackathon)

**OpenAI:**
- Get API key from https://platform.openai.com/api-keys
- Add `OPENAI_API_KEY` to backend environment variables
- FastAPI backend will use OpenAI automatically

**Gemini:**
- Get API key from https://makersuite.google.com/app/apikey
- Add `GEMINI_API_KEY` to backend environment variables
- FastAPI backend will use Gemini automatically

**Anthropic:**
- Get API key from https://console.anthropic.com/
- Add `ANTHROPIC_API_KEY` to backend environment variables

### Option B: Use llama.cpp (Production)

Requires:
- Separate server for llama.cpp (not suitable for Render free tier)
- Configure `LLM_BASE_URL` to point to your llama.cpp server
- More complex setup, see RAG_LLM_INTEGRATION_GUIDE.md

---

## Deployment Steps Summary

### For Hackathon Demo (FastAPI + OpenAI/Gemini):

1. **Deploy PostgreSQL on Render** (5 minutes)
2. **Deploy FastAPI Backend on Render** (5 minutes)
   - Add DATABASE_URL
   - Add API key (OpenAI or Gemini)
3. **Deploy Frontend on Render** (5 minutes)
   - Add VITE_API_BASE_URL
4. **Test the application** (2 minutes)

**Total time:** ~17 minutes

### For Production (Spring Boot + AI Service + RAG):

1. **Deploy PostgreSQL** (5 minutes)
2. **Deploy llama.cpp server** (separate hosting required)
3. **Deploy AI Service** (10 minutes)
4. **Deploy Spring Boot Backend** (10 minutes)
5. **Deploy Frontend** (5 minutes)
6. **Ingest documents** (manual step)
7. **Test full pipeline** (10 minutes)

**Total time:** ~45 minutes

---

## Health Checks

After deployment, test endpoints:

**Backend Health:**
```bash
curl https://herwell-backend.onrender.com/health
```

**Frontend:**
```bash
curl https://herwell-frontend.onrender.com
```

**API Test:**
```bash
curl https://herwell-backend.onrender.com/api/resources
```

---

## Troubleshooting

### Deployment Fails

1. Check Render logs (Logs tab)
2. Common issues:
   - Missing environment variables
   - Database connection failed
   - Port conflicts
   - Docker build errors

### Frontend Shows Error

1. Check `VITE_API_BASE_URL` is correct
2. Check backend is running
3. Check CORS configuration

### API Calls Fail

1. Check backend logs
2. Check database connection
3. Check API key if using LLM provider

---

## Cost Estimate

**Free Tier (Hackathon):**
- Frontend: $0/month
- Backend: $0/month
- PostgreSQL: $0/month
- **Total: $0/month**

**Production (Recommended):**
- Frontend: $0/month
- Backend: $7/month (Standard)
- PostgreSQL: $7/month (Standard)
- AI Service: $7/month (if needed)
- **Total: $21/month**

---

## Monitoring

Render provides:
- Auto-scaling logs
- Error tracking
- Performance metrics
- Health checks

Access via Render Dashboard → Your Service → Metrics

---

## Next Steps

1. Deploy using FastAPI + API provider (fastest)
2. Test all features
3. If successful, consider migrating to Spring Boot for production
4. Set up custom domain (optional)
5. Configure SSL (automatic on Render)

---

**Repository:** https://github.com/Medazizzormati/HerWell
**Last Updated:** 2026-10-18
