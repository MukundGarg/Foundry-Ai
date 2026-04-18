# Foundry AI — Workflow Builder

An AI-powered platform that turns any project idea into a structured, executed workflow using multiple AI agents.

## How it works

1. **You describe an idea** — e.g. "Build a stock market AI analyst"
2. **Idea Interpreter** extracts the domain, goals, and complexity
3. **Task Planner** breaks it into concrete tasks (research, coding, analysis, etc.)
4. **Agent Router** assigns the best agent type to each task
5. **Prompt Generator** creates optimized prompts per task
6. **Execution Engine** runs tasks in parallel where possible
7. **Result Aggregator** synthesizes all outputs into a final deliverable
8. **Workflow Viewer** shows the task graph with status

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI |
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| AI Providers | OpenAI, Anthropic, Google Gemini, Groq |
| Workflow Graph | React Flow |

## Project Structure

```
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Settings (pydantic-settings)
│   ├── api/routes/              # HTTP route handlers
│   │   ├── health.py
│   │   ├── keys.py              # API key management
│   │   └── workflow.py          # Workflow run/plan endpoints
│   ├── services/                # AI provider adapters
│   │   ├── base.py              # Abstract interface
│   │   ├── openai_service.py
│   │   ├── anthropic_service.py
│   │   ├── google_service.py
│   │   ├── groq_service.py
│   │   └── provider_factory.py  # Provider selection logic
│   ├── agents/                  # Agent implementations
│   │   ├── base_agent.py
│   │   ├── specialized.py       # Researcher, Coder, Analyst, etc.
│   │   └── registry.py
│   ├── workflows/               # Orchestration engine
│   │   ├── planner.py           # Idea → tasks → agent routing
│   │   ├── executor.py          # Parallel task execution
│   │   ├── aggregator.py        # Result synthesis
│   │   └── engine.py            # Top-level WorkflowEngine
│   ├── prompts/                 # Prompt templates + builder
│   │   ├── system_prompts.py
│   │   └── prompt_builder.py
│   └── utils/
│       ├── key_store.py         # In-memory session key store
│       ├── logger.py
│       └── text.py              # JSON extraction, text utils
│
└── frontend/
    └── src/
        ├── app/                 # Next.js App Router
        │   ├── layout.tsx
        │   ├── page.tsx         # Main page
        │   └── globals.css
        ├── components/
        │   ├── ui/              # Button, Badge, Card
        │   ├── ApiKeyModal.tsx
        │   ├── IdeaInput.tsx
        │   ├── WorkflowGraph.tsx
        │   ├── TaskCard.tsx
        │   ├── PlanPreview.tsx
        │   └── ResultPanel.tsx
        ├── lib/
        │   ├── api.ts           # Backend API client
        │   ├── session.ts       # Session ID management
        │   └── utils.ts
        └── types/
            └── workflow.ts      # TypeScript types
```

## Getting Started

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

The API runs at `http://localhost:8000`. Docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

The UI runs at `http://localhost:3000`.

### API Keys

You can either:
- Set server-side fallback keys in `backend/.env`
- Enter keys per-session via the UI (recommended — keys stay in memory only)

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/keys/set` | Store session API keys |
| GET | `/api/keys/providers/{session_id}` | List configured providers |
| DELETE | `/api/keys/clear/{session_id}` | Clear session keys |
| POST | `/api/workflow/run` | Run full workflow |
| POST | `/api/workflow/plan` | Preview plan without executing |
