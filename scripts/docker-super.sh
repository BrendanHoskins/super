#!/usr/bin/env bash
set -e

# Find the first open port starting at the given number
find_open_port() {
  local port=$1
  while lsof -i :"$port" >/dev/null 2>&1; do
    port=$((port + 1))
  done
  echo "$port"
}

BACKEND_PORT=$(find_open_port 5000)
FRONTEND_PORT=$(find_open_port 3000)
export BACKEND_PORT FRONTEND_PORT

echo "Using ports — Backend: $BACKEND_PORT, Frontend: $FRONTEND_PORT"
echo "App URL: http://localhost:$FRONTEND_PORT"
echo ""

exec docker compose up --build "$@"
