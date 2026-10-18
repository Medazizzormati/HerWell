# HERwell AI - Production Implementation Plan

## Repository Audit Summary

### Current State
- **Frontend**: React + Vite, fully functional, deployed-ready
- **Backend**: FastAPI with mock LLM, SQLite database
- **Database**: SQLite (in-memory, not production-ready)
- **LLM**: Mock responses only
- **RAG**: Keyword retrieval only, semantic disabled
- **Authentication**: None
- **Vector DB**: None

### Critical Gaps
1. No Spring Boot backend
2. No separate AI service
3. No real LLM serving
4. No persistent vector database
5. No authentication/authorization
6. No production deployment config

## Target Architecture

### Component Separation

**A. Spring Boot Application Backend (Render)**
- Public REST API
- Request validation
- Authentication/authorization
- User/project/wellbeing data
- Persistent application database (PostgreSQL)
- Chat orchestration
- Calls to AI service
- Privacy controls
- Health checks

**B. Separate AI Service (deployable)**
- Python + FastAPI (reuse existing code)
- Real LLM inference (llama.cpp/GGUF)
- Embedding generation
- Document ingestion/indexing
- Semantic retrieval
- Context assembly
- Grounded response generation
- Source citation validation
- Health checks

**C. Persistent Vector Database**
- PostgreSQL with pgvector extension
- Stores both application data and vectors
- Single database for simplicity

**D. Model Serving**
- Quantized GGUF model (e.g., Llama 3.2 3B Instruct)
- Served by llama.cpp server
- Separate embedding model (e.g., multilingual-e5)
- Local development: Ollama
- Production: Separate model server

## Implementation Steps

### Phase 1: Spring Boot Backend Structure (In Progress)
- [x] Create pom.xml with all dependencies
- [ ] Create main application class
- [ ] Create application.properties with profiles
- [ ] Create package structure (controller, service, repository, model, config)
- [ ] Implement health endpoint
- [ ] Implement CORS configuration
- [ ] Create JPA entities (User, Task, Checkin, Project, etc.)
- [ ] Create repositories
- [ ] Create basic CRUD endpoints

### Phase 2: Database Configuration
- [ ] Configure PostgreSQL connection
- [ ] Set up Flyway/Liquibase migrations
- [ ] Create schema for application data
- [ ] Create schema for pgvector
- [ ] Configure connection pooling

### Phase 3: Authentication & Security
- [ ] Implement JWT token generation
- [ ] Implement JWT filter
- [ ] Create SecurityConfig
- [ ] Implement login/registration endpoints
- [ ] Add role-based access control
- [ ] Secure private endpoints

### Phase 4: AI Service Integration
- [ ] Create HTTP client for AI service calls
- [ ] Implement chat endpoint that calls AI service
- [ ] Handle AI service failures gracefully
- [ ] Add request/response timeouts
- [ ] Implement retry logic with backoff

### Phase 5: Separate AI Service
- [ ] Create ai-service directory
- [ ] Set up FastAPI project structure
- [ ] Implement real LLM provider interface
- [ ] Integrate llama.cpp server connection
- [ ] Implement embedding generation
- [ ] Implement RAG retrieval with pgvector
- [ ] Implement document ingestion
- [ ] Add health checks

### Phase 6: Document Ingestion
- [ ] Create ingestion scripts
- [ ] Ingest WHO menstrual health docs
- [ ] Ingest NHS periods docs
- [ ] Ingest ACOG women's health docs
- [ ] Ingest Python docs
- [ ] Ingest React docs
- [ ] Ingest FastAPI docs
- [ ] Ingest Spring Boot docs
- [ ] Ingest PostgreSQL docs
- [ ] Test retrieval quality

### Phase 7: Frontend Compatibility
- [ ] Update API base URL for production
- [ ] Add authentication token handling
- [ ] Update API methods for new endpoints
- [ ] Test all pages with new backend

### Phase 8: Testing
- [ ] Write unit tests for Spring Boot
- [ ] Write integration tests
- [ ] Test LLM inference
- [ ] Test RAG retrieval
- [ ] Test authentication flow
- [ ] Load testing

### Phase 9: Render Deployment
- [ ] Create render.yaml for Spring Boot
- [ ] Create render.yaml for AI service
- [ ] Configure environment variables
- [ ] Set up PostgreSQL on Render
- [ ] Configure build commands
- [ ] Set up health checks
- [ ] Test deployment

### Phase 10: Documentation
- [ ] Update README with deployment instructions
- [ ] Document environment variables
- [ ] Document API endpoints
- [ ] Document ingestion process
- [ ] Document model serving
- [ ] Create troubleshooting guide

## Model Selection

### LLM Model
**Primary Choice**: Llama 3.2 3B Instruct (quantized GGUF)
- Small enough for resource-constrained environments
- Good multilingual support
- Instruction-tuned
- Approx 2GB in Q4_K_M quantization

**Alternative**: Phi-3 Mini 4K Instruct
- Even smaller (2.3GB)
- Good performance
- Limited context window

### Embedding Model
**Primary Choice**: intfloat/multilingual-e5-large
- Supports French, English, Arabic
- 1024 dimensions
- Good performance for semantic search

**Alternative**: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- Smaller (420MB)
- Faster inference
- Good enough for basic retrieval

## Hosting Considerations

### Render Free Tier Limitations
- RAM: 512MB (insufficient for LLM)
- CPU: 0.1 CPU (insufficient for inference)
- No GPU

### Recommended Approach
1. **Spring Boot on Render**: Deploy on free or starter tier
2. **AI Service**: Requires separate hosting with:
   - At least 2GB RAM
   - At least 1 CPU
   - Persistent storage for model
   - Options: Render Pro ($7/mo), Railway, Fly.io, or self-hosted VPS
3. **PostgreSQL**: Render PostgreSQL (free tier available)
4. **Model Server**: Can be collocated with AI service if resources allow

## Estimated Timeline
- Phase 1-2: 2-3 hours
- Phase 3: 2 hours
- Phase 4: 1 hour
- Phase 5: 4-6 hours
- Phase 6: 2-3 hours
- Phase 7: 1 hour
- Phase 8: 2-3 hours
- Phase 9: 2-3 hours
- Phase 10: 1 hour

**Total**: 17-22 hours of focused work

## Current Status
- [x] CORS fixed
- [x] Frontend working
- [x] Spring Boot pom.xml created
- [ ] Spring Boot structure in progress
- [ ] AI service not started
- [ ] LLM integration not started
- [ ] PostgreSQL not configured
- [ ] Document ingestion not started

## Next Immediate Steps
1. Complete Spring Boot basic structure
2. Set up PostgreSQL locally for testing
3. Create basic CRUD endpoints
4. Implement authentication
5. Set up separate AI service directory
6. Implement real LLM provider

## Notes
- This is a substantial refactor requiring careful testing
- The existing FastAPI backend can serve as the AI service with enhancements
- Frontend changes should be minimal if API contract is preserved
- Authentication will require frontend updates for token handling
