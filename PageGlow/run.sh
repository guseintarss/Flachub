#!/bin/bash
# Universal run script — использует daphne (ASGI) для WebSocket + HTTP
cd "$(dirname "$0")"
source .venv/bin/activate
exec python -m daphne -b 0.0.0.0 -p 8000 PageGlow.asgi:application
