# HERwell AI - 3-Minute Live Demo Script

## Pre-Demo Setup (Before Presentation)

1. **Start Backend:**
   ```bash
   cd backend
   .venv/Scripts/activate  # Windows
   uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```
   Verify: `curl http://127.0.0.1:8000/health` should return `{"status":"ok","service":"herwell-ai","llm_provider":"mock"}`

2. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```
   Access: http://localhost:5173

3. **Verify Database:**
   ```bash
   cd backend
   alembic upgrade head
   ```

4. **Open Browser:**
   - Backend docs: http://127.0.0.1:8000/docs
   - Frontend: http://localhost:5173

---

## Demo Script (3 Minutes)

### Introduction (15 seconds)
- "I'll now demonstrate HERwell AI, our wellbeing and study-support application for women university students in Tunisia."
- "The app runs on a React frontend and FastAPI backend with AI-powered features."

### Feature 1: Dashboard (20 seconds)
- Navigate to `/dashboard`
- "This is the personalized dashboard showing recent mood check-ins, upcoming tasks, and quick access to main features."
- "The UI uses a calm lavender and sage palette designed for wellbeing."

### Feature 2: Mood Check-in (25 seconds)
- Navigate to `/mood`
- "Let me record a mood check-in."
- Select mood: "I'm feeling stressed" (mood: anxious)
- Stress level: 7/10
- Energy level: 3/10
- Note: "Exam preparation is overwhelming"
- Click "Save Check-in"
- "The check-in is saved and displayed in the history chart."
- "This helps students track their emotional patterns over time."

### Feature 3: Study Planner (30 seconds)
- Navigate to `/planner`
- "Now let me create a study task and generate a plan."
- Add task:
  - Title: "Prepare for Calculus Exam"
  - Subject: "Mathematics"
  - Deadline: "2024-12-15"
  - Duration: 90 minutes
  - Priority: "high"
- Click "Add Task"
- "The task is added to the list."
- Click "Generate Study Plan"
- "The deterministic planner calculates the optimal schedule based on available time, task duration, and priorities."
- "It breaks tasks into manageable blocks with breaks."
- "This is a deterministic algorithm, not AI-generated, ensuring reliable scheduling."

### Feature 4: AI Assistant (40 seconds)
- Navigate to `/assistant`
- "Now let me ask the AI assistant a question about stress management."
- Type: "Comment gérer le stress pendant les examens ?" (How to manage stress during exams?)
- Click "Send"
- "The assistant processes the query through our LangGraph workflow:"
  - "First, a safety pre-check to ensure no crisis expressions"
  - "Then, intent classification"
  - "RAG retrieval searches our educational resource corpus"
  - "The LLM generates a response grounded in retrieved content"
  - "Finally, a safety post-check ensures appropriate language"
- "The response appears here with source citations."
- "Notice the 'Sources' section showing which educational resources were used."
- "The provider status shows 'mock' mode for this demo, but it supports Gemini, OpenAI, and Anthropic with API keys."

### Feature 5: Resources (20 seconds)
- Navigate to `/resources`
- "Let me browse the educational resource library."
- "Resources are categorized and include source metadata like verification status and language."
- "Students can search for specific topics like stress management, study tips, or wellbeing."

### Feature 6: Safety & Privacy (15 seconds)
- Navigate to `/privacy`
- "I want to emphasize that HERwell AI is non-diagnostic."
- "We clearly state our limitations and that we do not replace professional care."
- "The safety layer detects crisis expressions and encourages seeking help from verified local contacts."
- "We do not invent emergency numbers - support resources must be verified before public deployment."

### Conclusion (15 seconds)
- "That concludes the demo of HERwell AI."
- "The application provides mood tracking, deterministic study planning, and AI-powered educational support."
- "All features are designed with safety, privacy, and accessibility in mind."
- "Thank you!"

---

## Alternative Demo Flow (If Time Permits)

### Demonstrating MCP Server (1 minute)

```bash
cd backend
python -m app.mcp.server search_resources '{"query": "stress", "limit": 2}'
```

- "The MCP server exposes read-only tools for external agents."
- "This allows other AI systems to search our educational resources safely."
- "We provide 4 tools: search_resources, get_resource_by_id, list_resource_categories, and get_resource_count."

### Demonstrating Document Ingestion (1 minute)

1. Create a test document in `backend/test_corpus/`
2. Run ingestion:
   ```bash
   python -m app.ai.ingestion backend/test_corpus
   ```
3. Verify chunks created in database

- "The ingestion pipeline processes PDF, Markdown, and TXT files."
- "It chunks documents, generates multilingual embeddings, and stores them with metadata."
- "This enables semantic search across our resource corpus."

---

## Troubleshooting

**Backend won't start:**
- Check if port 8000 is already in use
- Verify `.env` file exists
- Check `DATABASE_URL` is set correctly

**Frontend won't load:**
- Check if port 5173 is already in use
- Verify `VITE_API_BASE_URL` is set to `http://127.0.0.1:8000`
- Check backend is running

**Database errors:**
- Run `alembic upgrade head` to ensure migrations are applied
- Check `DATABASE_URL` in `.env`
- For SQLite, ensure write permissions on the database file

**API errors:**
- Check Swagger docs at http://127.0.0.1:8000/docs
- Verify CORS origins are configured correctly
- Check `LLM_PROVIDER` and `LLM_API_KEY` if using real LLM

---

## Judge Q&A Preparation

**Q: How does the safety layer work?**
A: We use rule-based pattern matching for crisis expressions in English, French, and Tunisian Arabic. It's a pre-check and post-check in the LangGraph workflow, not dependent on the LLM. We do not claim comprehensive crisis detection - that requires clinical validation.

**Q: Is the planner AI-generated?**
A: No, the planner is deterministic. It calculates task allocation based on available time, duration, priority, and deadlines using a fixed algorithm. The LLM can explain the plan but does not perform the scheduling calculations.

**Q: How do you ensure the AI doesn't fabricate sources?**
A: RAG retrieval only returns chunks from our verified corpus. The LLM is instructed to cite only retrieved sources. We do not allow the LLM to generate or fabricate citations.

**Q: What happens if the LLM provider fails?**
A: The system degrades gracefully to mock mode, returning deterministic results (planner, retrieved resources) with a clear degraded-mode notice. The user always knows when AI features are unavailable.

**Q: How do you handle user data privacy?**
A: Currently, this is a demo with no real user data. For production, we would implement authentication, data encryption, deletion/export mechanisms, and comply with GDPR/Tunisian data protection laws. The README documents these as production requirements.

**Q: Why use keyword fallback instead of only vector search?**
A: Keyword fallback ensures the system works even when embeddings are unavailable or when no semantic matches meet the threshold. It provides a robust retrieval experience across different deployment scenarios.

**Q: Can this work offline?**
A: Yes, with mock LLM mode and SQLite database, the core features (mood tracking, planner, keyword retrieval) work offline. For full semantic search, you'd need the embedding model downloaded locally.

**Q: What's the difference between Chainlit and the React frontend?**
A: Chainlit is a development-focused conversational interface for testing the AI workflow. The React frontend is the production user interface with full feature access. Both use the same shared LangGraph workflow.

**Q: How do you verify support resources?**
A: We do not invent emergency contacts. The support resources file is intentionally empty until verified local contacts are added. This prevents providing incorrect or outdated information.

**Q: What's next for production deployment?**
A: We need: real authentication/authorization, PostgreSQL with pgvector deployment, secret management, rate limiting, comprehensive testing, accessibility audit, privacy review, and verified local support contacts.
