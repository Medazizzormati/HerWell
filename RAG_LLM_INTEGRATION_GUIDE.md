# HERwell AI - RAG and LLM Integration Complete Guide

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [LLM Integration](#llm-integration)
3. [RAG Pipeline](#rag-pipeline)
4. [Database Setup](#database-setup)
5. [Document Ingestion](#document-ingestion)
6. [Deployment](#deployment)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

### Component Diagram

```
┌─────────────┐
│   Frontend  │ (React + Vite, Port 5173)
│   Browser   │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────────┐
│  Spring Boot    │ (Port 8080)
│  Application   │
│  Backend       │
│                 │
│  - Auth         │
│  - Data Mgmt    │
│  - API Gateway  │
└──────┬──────────┘
       │ HTTP
       ▼
┌─────────────────┐
│   AI Service    │ (FastAPI, Port 8000)
│   (Python)      │
│                 │
│  - LLM Inference│
│  - Embeddings   │
│  - RAG Search   │
└──────┬──────────┘
       │ HTTP
       ▼
┌─────────────────┐
│  llama.cpp      │ (Port 8081)
│  Server         │
│                 │
│  - Quantized    │
│    LLM          │
└─────────────────┘
       │
       ▼
┌─────────────────┐
│  PostgreSQL     │
│  + pgvector     │
│                 │
│  - User Data    │
│  - Resources   │
│  - Embeddings   │
└─────────────────┘
```

### Data Flow

1. **User Query** → Frontend
2. **HTTP Request** → Spring Boot Backend
3. **AI Service Call** → AI Service (FastAPI)
4. **RAG Retrieval** → PostgreSQL + pgvector
5. **Context Assembly** → AI Service
6. **LLM Generation** → llama.cpp Server
7. **Response** → Spring Boot → Frontend → User

---

## LLM Integration

### Model Selection

**Primary Choice: Llama 3.2 3B Instruct (Q4_K_M)**
- Size: ~2GB quantized
- Context: 8K tokens
- Multilingual: Good for French/English/Arabic
- Hardware: 2GB RAM minimum

**Alternative: Phi-3 Mini 4K Instruct**
- Size: ~2.3GB quantized
- Context: 4K tokens
- Faster inference
- Smaller context window

### Step 1: Install llama.cpp

```bash
# Clone llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp

# Build (requires CMake and a C++ compiler)
cmake -B build
cmake --build build -j

# On Windows with Visual Studio:
cmake -B build -G "Visual Studio 17 2022"
cmake --build build --config Release
```

### Step 2: Download Quantized Model

```bash
# Llama 3.2 3B Instruct (Q4_K_M)
wget https://huggingface.co/MaziyarPanahi/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf

# Or Phi-3 Mini (smaller)
wget https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf
```

### Step 3: Start llama.cpp Server

```bash
# Navigate to llama.cpp directory
cd llama.cpp

# Start server with your model
./build/bin/server \
  --model /path/to/Llama-3.2-3B-Instruct-Q4_K_M.gguf \
  --port 8081 \
  --host 0.0.0.0 \
  --ctx-size 8192 \
  --n-gpu-layers 0 \
  --threads 4
```

**Server Options:**
- `--model`: Path to GGUF file
- `--port`: Server port (default 8081)
- `--host`: Bind address (0.0.0.0 for all interfaces)
- `--ctx-size`: Context window size
- `--n-gpu-layers`: Number of GPU layers (0 for CPU-only)
- `--threads`: Number of CPU threads

### Step 4: Verify Server

```bash
# Check server health
curl http://localhost:8081/health

# Test completion endpoint
curl -X POST http://localhost:8081/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.2-3b-instruct",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 100
  }'
```

### Step 5: Configure AI Service

Create `.env` file in `ai-service/`:

```bash
DATABASE_URL=postgresql://herwell:password@localhost:5432/herwell
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
LLM_PROVIDER=llamacpp
LLM_BASE_URL=http://localhost:8081
LLM_MODEL=llama-3.2-3b-instruct
LLM_TIMEOUT=120
LLM_MAX_TOKENS=800
CORS_ORIGINS=http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:5176
```

### Step 6: Test LLM Integration

```bash
cd ai-service

# Activate virtual environment
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Start AI service
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Test chat endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Comment gérer le stress pendant les examens?"}'
```

---

## RAG Pipeline

### Architecture

```
Document → Chunking → Embedding → PostgreSQL (pgvector)
                                                    ↓
Query → Embedding → Vector Search → Top-K Chunks
                                            ↓
Context Construction → LLM Generation → Response
```

### Step 1: Enable pgvector Extension

```sql
-- Connect to PostgreSQL
psql -U herwell -d herwell

-- Enable extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### Step 2: Create Tables

```sql
-- Resources table (metadata)
CREATE TABLE IF NOT EXISTS resources (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    source_label VARCHAR(255),
    source_url TEXT,
    language VARCHAR(10),
    verification_status VARCHAR(50)
);

-- Resource chunks with embeddings
CREATE TABLE IF NOT EXISTS resource_chunks (
    id SERIAL PRIMARY KEY,
    resource_id INTEGER NOT NULL REFERENCES resources(id),
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(384),  -- Adjust dimension based on model
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create vector index for fast similarity search
CREATE INDEX resource_chunks_embedding_idx 
ON resource_chunks USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### Step 3: Ingest Documents

**Option A: Python Script**

```python
from ai_service.app.rag import RAGPipeline
from ai_service.app.config import settings

# Initialize RAG
rag = RAGPipeline(settings.database_url, settings.embedding_model)
rag.create_pgvector_tables()
rag.load_model()

# Ingest a document
document_content = """
Menstrual health is a normal part of life for women and people who menstruate.
It involves the monthly shedding of the uterine lining.
"""

rag.ingest_document(
    resource_id=1,
    title="Menstrual Health Basics",
    content=document_content,
    chunk_size=500,
    overlap=50
)
```

**Option B: API Endpoint**

```bash
curl -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "resource_id": 1,
    "title": "Menstrual Health Basics",
    "content": "Full document text here..."
  }'
```

### Step 4: Semantic Search

```bash
# Search for relevant documents
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Comment gérer les crampes menstruelles?",
    "limit": 5
  }'
```

Response:
```json
{
  "results": [
    {
      "chunk_id": 5,
      "resource_id": 1,
      "chunk_index": 2,
      "content": "Crampes are caused by uterine contractions...",
      "resource_title": "Menstrual Health Basics",
      "resource_category": "wellbeing",
      "source_label": "WHO",
      "source_url": "https://who.int/...",
      "similarity": 0.85
    }
  ],
  "count": 1
}
```

### Step 5: Chat with RAG

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Quels sont les symptômes du SPM?",
    "use_rag": true
  }'
```

The AI service will:
1. Generate query embedding
2. Search pgvector for similar chunks
3. Retrieve top-K results
4. Build context from retrieved chunks
5. Send context + query to LLM
6. Return grounded response with citations

---

## Database Setup

### PostgreSQL Installation

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install postgresql-14 postgresql-14-pgvector
```

**macOS (Homebrew):**
```bash
brew install postgresql@14
brew install pgvector
```

**Windows:**
- Download PostgreSQL installer from postgresql.org
- Download pgvector source and compile

### Database Initialization

```bash
# Create database
createdb herwell

# Create user
psql -d postgres
CREATE USER herwell WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE herwell TO herwell;
\q

# Enable pgvector
psql -d herwell -U herwell
CREATE EXTENSION vector;
\q
```

### Connection String

**For Spring Boot:**
```
jdbc:postgresql://localhost:5432/herwell
```

**For AI Service (Python):**
```
postgresql://herwell:your_password@localhost:5432/herwell
```

---

## Document Ingestion

### Source Documents

**Women's Health:**
- WHO: https://www.who.int/health-topics/menstrual-health
- NHS: https://www.nhs.uk/conditions/periods/
- ACOG: https://www.acog.org/womens-health

**Technical Documentation:**
- Python: https://docs.python.org/3/
- React: https://react.dev/
- FastAPI: https://fastapi.tiangolo.com/
- Spring Boot: https://docs.spring.io/spring-boot/index.html

### Ingestion Script

Create `ai-service/scripts/ingest.py`:

```python
import sys
sys.path.append('..')
from app.rag import RAGPipeline
from app.config import settings
import requests
from bs4 import BeautifulSoup
import PyPDF2

rag = RAGPipeline(settings.database_url, settings.embedding_model)
rag.create_pgvector_tables()
rag.load_model()

def ingest_url(url, title, category):
    """Ingest content from a URL."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract text from main content
    text = soup.get_text(separator=' ', strip=True)
    
    # Save to database first
    # Then ingest chunks
    rag.ingest_document(
        resource_id=1,  # Inserted resource ID
        title=title,
        content=text,
        chunk_size=500,
        overlap=50
    )

def ingest_pdf(path, title, category):
    """Ingest content from a PDF file."""
    with open(path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    
    rag.ingest_document(
        resource_id=2,
        title=title,
        content=text,
        chunk_size=500,
        overlap=50
    )

# Ingest sources
ingest_url("https://www.who.int/health-topics/menstrual-health", 
           "WHO Menstrual Health", "wellbeing")
ingest_pdf("/path/to/python-docs.pdf", 
          "Python Documentation", "technical")
```

### Batch Ingestion

```bash
cd ai-service
python scripts/ingest.py
```

---

## Deployment

### Render Deployment

**Spring Boot on Render:**

Create `render.yaml` in `springboot-backend/`:

```yaml
services:
  - type: web
    name: herwell-backend
    env: node
    buildCommand: mvn clean package
    startCommand: java -jar target/herwell-backend-1.0.0.jar
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: herwell-db
          property: connectionString
      - key: AI_SERVICE_URL
        value: https://herwell-ai-service.onrender.com
      - key: JWT_SECRET
        generateValue: true
      - key: CORS_ORIGINS
        value: https://herwell-frontend.onrender.com

databases:
  - name: herwell-db
    databaseName: herwell
    user: herwell
```

**AI Service on Render:**

Create `render.yaml` in `ai-service/`:

```yaml
services:
  - type: web
    name: herwell-ai-service
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: herwell-db
          property: connectionString
      - key: LLM_BASE_URL
        value: https://herwell-llama-service.onrender.com
      - key: EMBEDDING_MODEL
        value: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

**Model Server:**

Due to resource constraints, consider:
- Railway (better for CPU-intensive workloads)
- Fly.io (supports custom runtimes)
- Self-hosted VPS (DigitalOcean, Linode)

### Environment Variables Summary

| Variable | Spring Boot | AI Service | Description |
|----------|--------------|------------|-------------|
| DATABASE_URL | ✅ | ✅ | PostgreSQL connection |
| AI_SERVICE_URL | ✅ | ❌ | AI service URL |
| LLM_BASE_URL | ❌ | ✅ | llama.cpp server URL |
| EMBEDDING_MODEL | ❌ | ✅ | Embedding model name |
| JWT_SECRET | ✅ | ❌ | JWT signing key |
| CORS_ORIGINS | ✅ | ✅ | Allowed origins |

---

## Testing

### Unit Tests

**Spring Boot:**

```bash
cd springboot-backend
mvn test
```

**AI Service:**

```bash
cd ai-service
pytest tests/
```

### Integration Tests

```bash
# Test full pipeline
curl http://localhost:8080/api/health
curl http://localhost:8000/health
curl http://localhost:8081/health

# Test chat through full stack
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Test query"}'
```

### RAG Quality Tests

```python
# Test retrieval quality
test_queries = [
    "Comment gérer le stress?",
    "Quels sont les symptômes du SPM?",
    "Comment utiliser React hooks?",
]

for query in test_queries:
    results = rag_pipeline.retrieve_with_metadata(query, limit=3)
    print(f"Query: {query}")
    print(f"Results: {len(results)} chunks retrieved")
    for r in results:
        print(f"  - {r['resource_title']} (similarity: {r['similarity']:.2f})")
```

---

## Troubleshooting

### LLM Server Issues

**Problem:** Server won't start
```bash
# Check if port is in use
netstat -an | grep 8081

# Try different port
./build/bin/server --model model.gguf --port 8082
```

**Problem:** Out of memory
```bash
# Reduce context size
--ctx-size 4096

# Use smaller model
# Switch to Phi-3 Mini instead of Llama 3.2
```

### pgvector Issues

**Problem:** Extension not found
```sql
-- Check installation
SELECT * FROM pg_available_extensions WHERE name = 'vector';

-- Install manually (if you have superuser)
CREATE EXTENSION vector;
```

**Problem:** Index creation fails
```sql
-- Check vector dimension
SELECT embedding FROM resource_chunks LIMIT 1;

-- Recreate with correct dimension
DROP INDEX resource_chunks_embedding_idx;
CREATE INDEX resource_chunks_embedding_idx 
ON resource_chunks USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### RAG Issues

**Problem:** No results returned
```python
# Check if embeddings exist
import psycopg2
conn = psycopg2.connect(database_url)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM resource_chunks")
print(f"Chunks in database: {cursor.fetchone()[0]}")
```

**Problem:** Poor similarity scores
```python
# Test embedding generation
test_embedding = rag_pipeline.generate_embedding("test")
print(f"Embedding dimension: {len(test_embedding)}")

# Adjust similarity threshold
results = rag_pipeline.search(query, similarity_threshold=0.2)
```

### Performance Issues

**Problem:** Slow search
```sql
-- Check index usage
EXPLAIN ANALYZE SELECT * FROM resource_chunks 
ORDER BY embedding <=> query_embedding::vector LIMIT 5;

-- Rebuild index if needed
REINDEX INDEX resource_chunks_embedding_idx;
```

**Problem:** Slow LLM generation
```bash
# Reduce max tokens
LLM_MAX_TOKENS=400

# Use faster model
# Switch to Q2_K quantization (faster, less accurate)
```

---

## Best Practices

### Security

1. **Never commit API keys** to repository
2. **Use environment variables** for all secrets
3. **Enable authentication** in production
4. **Rate limit** AI service endpoints
5. **Validate inputs** at all layers

### Performance

1. **Cache embeddings** for frequently used documents
2. **Batch ingest** documents in chunks
3. **Use connection pooling** for database
4. **Monitor memory usage** of LLM server
5. **Set appropriate timeouts** for HTTP requests

### Quality

1. **Test retrieval** with domain-specific queries
2. **Validate citations** match retrieved content
3. **Monitor similarity scores** to ensure quality
4. **Regularly update** embedding models
5. **A/B test** different chunk sizes

---

## Monitoring

### Health Check Endpoints

```bash
# Spring Boot
curl http://localhost:8080/api/health

# AI Service
curl http://localhost:8000/health

# LLM Server
curl http://localhost:8081/health
```

### Metrics to Monitor

- LLM server response time
- RAG retrieval latency
- Database query performance
- Memory usage of each component
- Error rates by endpoint

---

## Next Steps

1. Set up PostgreSQL with pgvector locally
2. Download and run llama.cpp server
3. Ingest initial documents
4. Test full pipeline end-to-end
5. Deploy to Render or similar platform
6. Monitor and optimize performance
7. Add authentication for production use
