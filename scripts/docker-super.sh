#!/usr/bin/env bash
set -e

# Load server/.env for NGROK_*, PUBLIC_URL_FOR_OAUTH_CALLBACK, etc.
if [ -f server/.env ]; then
  set -a
  # shellcheck source=/dev/null
  . server/.env
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
export BACKEND_PORT FRONTEND_PORT

# Free tier: one static domain (e.g. your-name.ngrok-free.app). User sets NGROK_URL and NGROK_AUTHTOKEN in server/.env.
if [ -n "$NGROK_AUTHTOKEN" ] && [ -n "$NGROK_URL" ]; then
  export NGROK_AUTHTOKEN NGROK_URL
  export COMPOSE_PROFILES="${COMPOSE_PROFILES:+$COMPOSE_PROFILES,}ngrok"
  NGROK_DISPLAY=$NGROK_URL
  [[ $NGROK_DISPLAY != http* ]] && NGROK_DISPLAY="https://$NGROK_DISPLAY"
  echo "Ngrok:        $NGROK_DISPLAY -> backend"
fi

echo "App URL:      http://localhost:$FRONTEND_PORT"
echo "Backend API:  http://localhost:$BACKEND_PORT/api"
echo ""

exec docker compose up --build "$@"
