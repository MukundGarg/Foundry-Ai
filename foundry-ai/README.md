# 🔥 Foundry AI

> A meta-AI platform where multiple AI models collaborate as a council to plan and build MVPs.

## Architecture

```
User Idea → AI Council (Claude + GPT + Gemini + Groq) → Agent Task Plan → Execution Agents → MVP
```

**Council Layer** — Strategic planning via 4 AI models through LiteLLM  
**Agent Layer** — Specialized execution agents (Database, Backend, Frontend, DevOps, Integration)  
**Workflow Engine** — Temporal.io for durable orchestration  

## Quick Start

```bash
# 1. Copy env file and add your API keys
cp .env.example .env

# 2. Start all services
docker-compose up -d

# 3. Open the app
open http://localhost:3000
```

## Manual Development Setup

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev

# Temporal (requires Docker)
docker-compose up temporal temporal-admin-tools -d
```

## Project Structure

```
/foundry-ai
  /frontend     → Next.js + React + Tailwind
  /backend      → FastAPI application
  /council      → AI Council engine (LiteLLM)
  /agents       → Execution agents
  /workflows    → Temporal workflow definitions
  /schemas      → Data contract templates
  /infra        → Dockerfiles & deployment
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js, React, TailwindCSS |
| Backend | FastAPI, Python 3.11+ |
| LLM Gateway | LiteLLM |
| Workflow | Temporal.io |
| Database | PostgreSQL |
| Container | Docker |

## License

MIT
