# HERwell AI - Spring Boot & AI Service Setup

## Architecture Overview

### Components

1. **Spring Boot Backend** (`springboot-backend/`)
   - Application REST API
   - User data management
   - Authentication (JWT)
   - Calls AI service for LLM responses
   - Port: 8080

2. **AI Service** (`ai-service/`)
   - Python FastAPI
   - Real LLM inference (llama.cpp)
   - Embedding generation
   - RAG retrieval with pgvector
   - Port: 8000

3. **Frontend** (`frontend/`)
   - React + Vite
   - 3D avatar
   - Currently calls backend on port 8080

4. **Database**
   - PostgreSQL with pgvector extension
   - Stores application data and vector embeddings

## Quick Start

### Prerequisites

- Java 17+
- Maven 3.6+
- Python 3.9+
- PostgreSQL 14+ with pgvector extension
- llama.cpp server (for local LLM)

### 1. Database Setup

```bash
# Install PostgreSQL and pgvector
# On Ubuntu/Debian:
sudo apt-get install postgresql-14-pgvector

# Create database
createdb herwell

# Enable pgvector extension
psql herwell
CREATE EXTENSION vector;
```

### 2. Spring Boot Backend

```bash
cd springboot-backend

# Set environment variables
export DATABASE_URL="jdbc:postgresql://localhost:5432/herwell"
export DB_USERNAME="herwell"
export DB_PASSWORD="your_password"
export AI_SERVICE_URL="http://localhost:8000"

# Build and run
mvn clean install
mvn spring-boot:run
```

Backend will be available at http://localhost:8080

### 3. AI Service

```bash
cd ai-service

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://herwell:herwell_password@localhost:5432/herwell"
export LLM_BASE_URL="http://localhost:8081"

# Run
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

AI service will be available at http://localhost:8000

### 4. Frontend

```bash
cd frontend

# Set API base URL to Spring Boot
export VITE_API_BASE_URL="http://localhost:8080"

# Install and run
npm install
npm run dev
```

Frontend will be available at http://localhost:5173

## Model Serving (llama.cpp)

### Download Quantized Model

```bash
# Download Llama 3.2 3B Instruct (Q4_K_M quantization)
wget https://huggingface.co/MaziyarPanahi/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf

# Or use a smaller model if resources are limited
wget https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf
```

### Start llama.cpp Server

```bash
# Build llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
cmake -B build
cmake --build build -j

# Start server
./build/bin/server --model /path/to/model.gguf --port 8081 --host 0.0.0.0
```

Model server will be available at http://localhost:8081

## Environment Variables

### Spring Boot

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL JDBC URL | jdbc:postgresql://localhost:5432/herwell |
| DB_USERNAME | Database username | herwell |
| DB_PASSWORD | Database password | herwell_password |
| AI_SERVICE_URL | AI service URL | http://localhost:8000 |
| JWT_SECRET | JWT signing secret | herwell-secret-key |
| CORS_ORIGINS | Allowed CORS origins | localhost:5173,... |

### AI Service

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL URL | postgresql://herwell:herwell_password@localhost:5432/herwell |
| EMBEDDING_MODEL | Embedding model name | paraphrase-multilingual-MiniLM-L12-v2 |
| LLM_PROVIDER | LLM provider | llamacpp |
| LLM_BASE_URL | llama.cpp server URL | http://localhost:8081 |
| LLM_MODEL | Model name | llama-3.2-3b-instruct |
| LLM_TIMEOUT | Request timeout (seconds) | 120 |
| LLM_MAX_TOKENS | Max output tokens | 800 |

## Current Implementation Status

### ✅ Completed
- Spring Boot project structure
- Basic JPA entities (MoodCheckin, StudyTask)
- Repositories and CRUD controllers
- CORS configuration
- Health endpoints
- AI service FastAPI structure
- Configuration files

### ⏳ In Progress
- Authentication (JWT)
- Full API endpoint implementation
- Real LLM integration
- RAG pipeline with pgvector
- Document ingestion
- Frontend integration testing

### ❌ Not Started
- Real LLM provider implementation
- Embedding generation
- Vector database setup
- Document ingestion scripts
- Authentication flow
- Full endpoint parity with FastAPI backend

## Next Steps

1. **Set up PostgreSQL locally** for testing
2. **Start llama.cpp server** with a quantized model
3. **Implement real LLM provider** in AI service
4. **Add pgvector tables** to database schema
5. **Implement embedding generation**
6. **Implement RAG retrieval**
7. **Add document ingestion** for public health sources
8. **Implement authentication** in Spring Boot
9. **Test full pipeline**
10. **Deploy to Render**

## Testing

```bash
# Test Spring Boot health
curl http://localhost:8080/api/health

# Test AI service health
curl http://localhost:8000/health

# Test task creation
curl -X POST http://localhost:8080/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Test task","durationMinutes":30,"priority":"high"}'
```

## Troubleshooting

### Spring Boot won't start
- Check Java version (must be 17+)
- Check database connection
- Verify port 8080 is not in use

### AI Service won't start
- Check Python version (3.9+)
- Verify dependencies installed
- Check llama.cpp server is running

### Database connection errors
- Verify PostgreSQL is running
- Check pgvector extension is enabled
- Verify credentials in environment variables

### LLM not responding
- Verify llama.cpp server is running
- Check model file exists
- Verify LLM_BASE_URL is correct
