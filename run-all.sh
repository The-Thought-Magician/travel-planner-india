#!/bin/bash
# Run both backend and frontend together

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to cleanup background processes
cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    jobs -p | xargs -r kill 2>/dev/null || true
    wait 2>/dev/null || true
    echo -e "${GREEN}All services stopped.${NC}"
    exit 0
}

# Trap SIGINT and SIGTERM
trap cleanup SIGINT SIGTERM

# Require uv
if ! command -v uv >/dev/null 2>&1; then
    echo -e "${RED}uv not found. Install from https://docs.astral.sh/uv/${NC}"
    exit 1
fi

# Require pnpm
if ! command -v pnpm >/dev/null 2>&1; then
    echo -e "${RED}pnpm not found. Install with: npm i -g pnpm${NC}"
    exit 1
fi

# Sync Python deps (idempotent)
export UV_PROJECT_ENVIRONMENT="$PROJECT_ROOT/.venv"
cd "$PROJECT_ROOT"
uv sync --quiet

# Sync frontend deps (idempotent)
if [ ! -d "$PROJECT_ROOT/frontend/node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    pnpm -C "$PROJECT_ROOT/frontend" install
fi

# Get the project root directory for the backend
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Travel Planner India - Dev Server${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}Backend:${NC}  http://localhost:8000"
echo -e "${GREEN}API Docs:${NC} http://localhost:8000/docs"
echo -e "${GREEN}Frontend:${NC} http://localhost:3000"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Start backend (FastAPI with uvicorn)
echo -e "${GREEN}Starting backend...${NC}"
cd "$PROJECT_ROOT"
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start frontend (Next.js)
echo -e "${GREEN}Starting frontend...${NC}"
pnpm -C "$PROJECT_ROOT/frontend" dev &
FRONTEND_PID=$!

echo -e "${GREEN}✓ All services started!${NC}"
echo ""

# Wait for any background process to exit
wait -n
EXIT_CODE=$?

# If any process exits, kill the others
cleanup
exit $EXIT_CODE
