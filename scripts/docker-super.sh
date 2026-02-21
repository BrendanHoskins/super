#!/usr/bin/env bash
set -e

# .env at repo root (required for compose server env_file). Create from .env.example if missing.
if [ ! -f .env ] && [ -f .env.example ]; then
  cp .env.example .env
  echo "Created .env from .env.example — edit .env with your secrets."
fi
if [ -f .env ]; then
  set -a
  # shellcheck source=/dev/null
  . .env
  set +a
fi

find_open_port() {
  local port=$1
  while lsof -i :"$port" >/dev/null 2>&1; do
    port=$((port + 1))
  done
  echo "$port"
}

BACKEND_PORT=$(find_open_port 5000)
FRONTEND_PORT=$(find_open_port 3000)
MONGO_PORT=$(find_open_port 27017)
export BACKEND_PORT FRONTEND_PORT MONGO_PORT

# Free tier: one static domain (e.g. your-name.ngrok-free.app). User sets NGROK_URL and NGROK_AUTHTOKEN in .env at repo root.
if [ -n "$NGROK_AUTHTOKEN" ] && [ -n "$NGROK_URL" ]; then
  export NGROK_AUTHTOKEN NGROK_URL
  export COMPOSE_PROFILES="${COMPOSE_PROFILES:+$COMPOSE_PROFILES,}ngrok"
  NGROK_DISPLAY=$NGROK_URL
  [[ $NGROK_DISPLAY != http* ]] && NGROK_DISPLAY="https://$NGROK_DISPLAY"
  echo "Ngrok:        $NGROK_DISPLAY -> backend"
fi

echo "App URL:      http://localhost:$FRONTEND_PORT"
echo "Backend API:  http://localhost:$BACKEND_PORT/api"
echo "Mongo:        localhost:$MONGO_PORT"
echo ""

exec docker compose up --build "$@"
