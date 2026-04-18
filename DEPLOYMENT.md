# Foundry AI — Deployment Guide

## Architecture

```
┌─────────────────────┐        ┌──────────────────────────┐
│   Frontend          │  HTTP  │   Backend                │
│   Next.js 14        │───────▶│   FastAPI + Gunicorn     │
│   Vercel / Docker   │        │   Railway / Render / Docker│
└─────────────────────┘        └──────────────────────────┘
```

---

## Option A — Docker Compose (self-hosted / VPS)

### Prerequisites
- Docker ≥ 24
- Docker Compose ≥ 2.20

### Steps

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd foundry-ai

# 2. Create root .env from template
cp .env.example .env

# 3. Edit .env — set CORS_ORIGINS to your domain
#    e.g. CORS_ORIGINS=https://yourdomain.com
nano .env

# 4. Build images
docker compose build

# 5. Start services
docker compose up -d

# 6. Verify
curl http://localhost:8000/api/health
curl http://localhost:3000
```

### Updating

```bash
git pull
docker compose build
docker compose up -d
```

### Logs

```bash
docker compose logs -f backend
docker compose logs -f frontend
```

---

## Option B — Vercel (frontend) + Railway (backend)

### Backend on Railway

1. Install Railway CLI:
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. Create a new project and deploy:
   ```bash
   cd backend
   railway init
   railway up
   ```

3. Set environment variables in the Railway dashboard:
   | Variable | Value |
   |----------|-------|
   | `APP_ENV` | `production` |
   | `APP_HOST` | `0.0.0.0` |
   | `APP_PORT` | `8000` |
   | `WORKERS` | `2` |
   | `CORS_ORIGINS` | `https://your-app.vercel.app` |
   | `OPENAI_API_KEY` | *(optional fallback)* |
   | `ANTHROPIC_API_KEY` | *(optional fallback)* |
   | `GOOGLE_API_KEY` | *(optional fallback)* |
   | `GROQ_API_KEY` | *(optional fallback)* |

4. Note your Railway backend URL (e.g. `https://foundry-ai-backend.up.railway.app`)

### Frontend on Vercel

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Deploy:
   ```bash
   cd frontend
   vercel --prod
   ```

3. Set environment variable in Vercel dashboard:
   | Variable | Value |
   |----------|-------|
   | `NEXT_PUBLIC_API_URL` | `https://foundry-ai-backend.up.railway.app` |

   > **Important:** After setting this variable, redeploy the frontend:
   > ```bash
   > vercel --prod
   > ```

---

## Option C — Vercel (frontend) + Render (backend)

### Backend on Render

1. Push your code to GitHub.

2. Go to [render.com](https://render.com) → New → Web Service.

3. Connect your GitHub repo, set:
   - **Root Directory**: `backend`
   - **Dockerfile Path**: `Dockerfile`
   - **Health Check Path**: `/api/health`

4. Add environment variables (same as Railway table above).

5. Note your Render URL (e.g. `https://foundry-ai-backend.onrender.com`)

### Frontend on Vercel

Same as Option B — set `NEXT_PUBLIC_API_URL` to your Render URL.

---

## Environment Variables Reference

### Backend

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `APP_ENV` | `development` | Yes | `development` or `production` |
| `APP_HOST` | `0.0.0.0` | No | Bind host |
| `APP_PORT` | `8000` | No | Bind port |
| `WORKERS` | `0` (auto) | No | Gunicorn worker count |
| `LOG_LEVEL` | `info` | No | `debug/info/warning/error` |
| `CORS_ORIGINS` | `http://localhost:3000` | Yes (prod) | Comma-separated allowed origins |
| `OPENAI_API_KEY` | `` | No | Server-side fallback key |
| `ANTHROPIC_API_KEY` | `` | No | Server-side fallback key |
| `GOOGLE_API_KEY` | `` | No | Server-side fallback key |
| `GROQ_API_KEY` | `` | No | Server-side fallback key |

### Frontend

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Yes (prod) | Backend API URL |

---

## Health Checks

| Endpoint | Purpose |
|----------|---------|
| `GET /api/health` | Liveness — is the process alive? |
| `GET /api/ready` | Readiness — is the app ready to serve? |

---

## Security Checklist

- [x] API keys never stored on disk — in-memory session store only
- [x] `.env` files excluded from git via `.gitignore`
- [x] Non-root user in Docker containers
- [x] Security headers on all responses (X-Frame-Options, X-Content-Type-Options)
- [x] CORS restricted to configured origins
- [ ] **TODO (production):** Add Redis for session key persistence across restarts
- [ ] **TODO (production):** Add rate limiting per IP on `/api/workflow/run`
- [ ] **TODO (production):** Set up HTTPS (handled by Vercel/Railway/Render automatically)

---

## Local Development

```bash
# Backend
make install-backend
make dev-backend          # runs on http://localhost:8000

# Frontend (new terminal)
make install-frontend
make dev-frontend         # runs on http://localhost:3000

# Or with Docker
make docker-build
make docker-up
make docker-logs
```
