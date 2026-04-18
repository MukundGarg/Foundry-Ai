# ── Stage 1: dependency install ───────────────────────────────────────────────
FROM python:3.12-slim AS deps

WORKDIR /app

# Install build tools needed by some packages (e.g. grpcio)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ── Stage 2: runtime image ────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

# Non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Copy installed packages from deps stage
COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Ensure the app user owns the files
RUN chown -R appuser:appgroup /app

USER appuser

# Expose port (overridable via APP_PORT env var)
EXPOSE 8000

# Health check — Docker will mark container unhealthy if this fails
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"

# Production: gunicorn with uvicorn workers
# Development override: python main.py
CMD ["gunicorn", "-c", "gunicorn.conf.py", "main:app"]
