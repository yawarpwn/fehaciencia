#!/bin/bash

# Colores para distinguir logs
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Función para matar ambos procesos al salir (Ctrl+C)
cleanup() {
  echo "Apagando servicios..."
  kill $PID_API $PID_WEB 2>/dev/null
  exit 0
}
trap cleanup SIGINT SIGTERM

echo "🚀 Levantando API (FastAPI)..."
cd api && uv run uvicorn app.main:app --reload --port 8000 &
PID_API=$!

echo "🌐 Levantando Web (SvelteKit)..."
cd web && pnpm dev &
PID_WEB=$!

echo ""
echo -e "${BLUE}API:${NC}     http://localhost:8000"
echo -e "${RED}Web:${NC}     http://localhost:5173"
echo -e "${BLUE}API Docs:${NC} http://localhost:8000/docs"
echo ""
echo "Ctrl+C para apagar todo"

wait
