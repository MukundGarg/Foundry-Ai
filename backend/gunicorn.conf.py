"""
Gunicorn configuration for production.

Usage:
    gunicorn -c gunicorn.conf.py main:app

Environment variables override these defaults:
    WORKERS   — number of worker processes (default: 2*CPU+1)
    APP_HOST  — bind host (default: 0.0.0.0)
    APP_PORT  — bind port (default: 8000)
"""

import multiprocessing
import os

# Server socket
host = os.getenv("APP_HOST", "0.0.0.0")
port = os.getenv("APP_PORT", "8000")
bind = f"{host}:{port}"

# Worker processes
_workers_env = int(os.getenv("WORKERS", "0"))
workers = _workers_env if _workers_env > 0 else (2 * multiprocessing.cpu_count() + 1)

# Use uvicorn workers for ASGI
worker_class = "uvicorn.workers.UvicornWorker"

# Timeouts — generous for long-running AI workflows
timeout = 300          # 5 minutes per request
graceful_timeout = 30
keepalive = 5

# Logging
accesslog = "-"   # stdout
errorlog = "-"    # stderr
loglevel = os.getenv("LOG_LEVEL", "info")

# Process naming
proc_name = "foundry-ai-backend"

# Restart workers after this many requests (prevents memory leaks)
max_requests = 1000
max_requests_jitter = 100
