#!/bin/bash
# Shut down the travel-planner backend and frontend started by run-all.sh.
# Scoped to this project's paths so it won't touch other uvicorn / next dev
# processes you may have running.

set -u

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

kill_matching() {
    local label="$1"
    local pattern="$2"
    local pids
    pids=$(pgrep -f "$pattern" || true)
    if [ -z "$pids" ]; then
        echo -e "${YELLOW}$label: not running${NC}"
        return
    fi
    echo -e "${GREEN}$label: stopping PIDs $pids${NC}"
    # shellcheck disable=SC2086
    kill $pids 2>/dev/null || true
    sleep 1
    # Force-kill anything that didn't exit cleanly
    pids=$(pgrep -f "$pattern" || true)
    if [ -n "$pids" ]; then
        # shellcheck disable=SC2086
        kill -9 $pids 2>/dev/null || true
    fi
}

echo -e "${RED}Stopping travel-planner services...${NC}"

# Backend — uvicorn bound to this project
kill_matching "Backend (uvicorn)" "uvicorn.*app.main:app"

# Frontend — next dev / next-server started from frontend/ dir
kill_matching "Frontend (next dev)"   "$PROJECT_ROOT/frontend.*next dev"
kill_matching "Frontend (next-server)" "next-server.*v16"

# Clear Next's dev lock so the next run doesn't fail on a stale file
rm -f "$PROJECT_ROOT/frontend/.next/dev/lock"

echo -e "${GREEN}Done.${NC}"
