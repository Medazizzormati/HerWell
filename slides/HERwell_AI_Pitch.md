# HERwell AI — Pitch deck (7 slides)

## Slide 1 — HERwell AI
**A supportive, AI-powered wellbeing companion for women students and early-career graduates in Tunisia.**
- Team: [Add team members]
- HERwin Hackathon — IEEE WIE / École Polytechnique de Sousse

Speaker note: Introduce the goal: make everyday support and planning easier without pretending to provide medical care.

## Slide 2 — The problem
- Exam and thesis stress
- Burnout and uncertainty at the start of a career
- Stigma can make it difficult to seek support
- Heavy workloads can disrupt sleep, habits and time management

Speaker note: These needs are stated in the hackathon specification. Avoid inventing statistics.

## Slide 3 — Our solution
- Optional mood check-in
- Supportive AI assistant for everyday stress and study routines
- Deterministic study planner
- Educational resource library with source labels
- Privacy-first, non-diagnostic framing

Speaker note: Demonstrate a simple, realistic user journey.

## Slide 4 — Where AI matters
- LangGraph orchestrates the workflow (implemented)
- Intent routing selects the relevant path (implemented)
- RAG retrieves relevant educational resources (implemented with semantic + keyword)
- LLM generates a contextual response when configured (mock/Gemini/OpenAI/Anthropic supported)
- Safety checks run before and after response generation (implemented)
- Document ingestion pipeline with multilingual embeddings (implemented)
- MCP server for external agent integration (implemented)
- Chainlit interface for conversational testing (implemented)

Speaker note: Semantic retrieval uses cosine similarity with keyword fallback. PostgreSQL/pgvector integration implemented but not tested in demo environment (PostgreSQL unavailable locally).

## Slide 5 — Architecture
**Frontend:** React + Vite + JSX (all routes implemented: dashboard, mood, assistant, planner, resources, privacy, settings, support)

**Backend:** FastAPI with modular services (all endpoints implemented: health, resources, chat, check-ins, tasks, plans, support)

**AI Workflow (LangGraph):**
- Safety pre-check → Intent classification → RAG retrieval (semantic + keyword) / Deterministic planning → LLM generation → Safety post-check → Response with citations

**Data Layer:**
- SQLAlchemy models: MoodCheckin, StudyTask, Resource, ResourceChunk
- PostgreSQL + pgvector for production (SQLite for local testing)
- Alembic migrations configured
- Document ingestion: PDF/Markdown/TXT with multilingual embeddings

**Integrations:**
- MCP server with 4 read-only tools
- Chainlit interface using shared workflow
- LLM adapter: mock/Gemini/OpenAI/Anthropic

Speaker note: Show the live `/health` endpoint and the running UI. PostgreSQL/pgvector tested with SQLite fallback; real vector search requires PostgreSQL installation.

## Slide 6 — Impact, safety and privacy
- Practical next steps, not diagnosis
- Optional mood tracking
- No invented local support contacts
- Demo data only; production needs authentication, authorization and privacy review
- Future: verified local resources, multilingual evaluation and user testing

Speaker note: Be honest about limits and how feedback would improve the product.

## Slide 7 — Live demo and next steps
Demo sequence (3 minutes):
1. Open dashboard and show backend status.
2. Submit a mood check-in.
3. Add two tasks and generate a deterministic plan.
4. Ask the assistant about exam stress; show resource labels and demo/LLM status.
5. Show privacy/safety page.

Close: HERwell AI makes everyday wellbeing support more accessible while keeping human support and user safety central.

## Timing
- Presentation: 5 minutes
- Live demo: 3 minutes
- Q&A: 2 minutes
