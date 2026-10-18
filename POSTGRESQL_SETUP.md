# PostgreSQL Setup Guide for HERwell AI

## Quick Setup (Local Development)

### Option 1: Docker (Recommended)

```bash
# Create docker-compose.yml
version: '3.8'
services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: herwell
      POSTGRES_USER: herwell
      POSTGRES_PASSWORD: herwell_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U herwell"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

Run:
```bash
docker-compose up -d
```

### Option 2: Native Installation

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install postgresql-14 postgresql-14-pgvector
sudo service postgresql start
```

**macOS (Homebrew):**
```bash
brew install postgresql@14
brew install pgvector
brew services start postgresql@14
```

**Windows:**
1. Download PostgreSQL installer: https://www.postgresql.org/download/windows/
2. Download pgvector: https://github.com/pgvector/pgvector
3. Follow installation instructions

## Database Initialization

```bash
# Create database
createdb herwell

# Create user
psql -d postgres
CREATE USER herwell WITH PASSWORD 'your_secure_password';
ALTER USER herwell WITH SUPERUSER;
GRANT ALL PRIVILEGES ON DATABASE herwell TO herwell;
\q

# Connect to database
psql -d herwell -U herwell

# Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

# Verify extension
SELECT * FROM pg_extension WHERE extname = 'vector';

# Create tables
\i springboot-backend/src/main/resources/schema.sql

# Exit
\q
```

## Schema SQL

Create `springboot-backend/src/main/resources/schema.sql`:

```sql
-- Resources table
CREATE TABLE IF NOT EXISTS resources (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    source_label VARCHAR(255),
    source_url TEXT,
    language VARCHAR(10),
    verification_status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Resource chunks with pgvector
CREATE TABLE IF NOT EXISTS resource_chunks (
    id SERIAL PRIMARY KEY,
    resource_id INTEGER NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(384),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create vector index
CREATE INDEX IF NOT EXISTS resource_chunks_embedding_idx 
ON resource_chunks USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Mood checkins
CREATE TABLE IF NOT EXISTS mood_checkins (
    id SERIAL PRIMARY KEY,
    mood VARCHAR(50) NOT NULL,
    stress INTEGER NOT NULL,
    energy INTEGER NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Study tasks
CREATE TABLE IF NOT EXISTS study_tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    subject VARCHAR(100),
    duration_minutes INTEGER,
    priority VARCHAR(50),
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Projects
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    technologies VARCHAR(255),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Project documents
CREATE TABLE IF NOT EXISTS project_documents (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    file_type VARCHAR(50),
    source_type VARCHAR(50),
    language VARCHAR(10),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cycle tracking
CREATE TABLE IF NOT EXISTS cycle_tracking (
    id SERIAL PRIMARY KEY,
    period_start_date DATE NOT NULL,
    cycle_length_days INTEGER,
    notes TEXT,
    tracking_enabled BOOLEAN DEFAULT FALSE
);

-- Symptom logs
CREATE TABLE IF NOT EXISTS symptom_logs (
    id SERIAL PRIMARY KEY,
    log_date DATE NOT NULL,
    physical_symptoms TEXT,
    mood TEXT,
    energy INTEGER,
    pain_level INTEGER,
    notes TEXT,
    tracking_enabled BOOLEAN DEFAULT FALSE
);
```

## Connection Strings

**Spring Boot (application.properties):**
```properties
spring.datasource.url=jdbc:postgresql://localhost:5432/herwell
spring.datasource.username=herwell
spring.datasource.password=herwell_password
```

**AI Service (.env):**
```bash
DATABASE_URL=postgresql://herwell:herwell_password@localhost:5432/herwell
```

## Verify Setup

```bash
# Test connection
psql -d herwell -U herwell -c "SELECT version();"

# Check tables
psql -d herwell -U herwell -c "\dt"

# Check pgvector
psql -d herwell -U herwell -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

## Backup and Restore

**Backup:**
```bash
pg_dump -U herwell herwell > backup.sql
```

**Restore:**
```bash
psql -U herwell herwell < backup.sql
```
