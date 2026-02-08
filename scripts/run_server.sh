#!/usr/bin/env bash
# Start the local API server (FastAPI via uvicorn)
# Activate virtualenv if present
if [ -f .venv/bin/activate ]; then
  source .venv/bin/activate
fi

# Run uvicorn
uvicorn mcp_redactionnel.api:app --reload --host 127.0.0.1 --port 8000
