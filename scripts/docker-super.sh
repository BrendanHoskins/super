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
fi

# Start all containers in background; stream logs and print summary once backend + frontend have logged "ready".
docker compose up --build -d "$@"

BACKEND_URL="http://localhost:$BACKEND_PORT/api"
FRONTEND_URL="http://localhost:$FRONTEND_PORT"
DATABASE_URL="mongodb://localhost:$MONGO_PORT"
if [ -n "$NGROK_AUTHTOKEN" ] && [ -n "$NGROK_URL" ]; then
  NGROK_DISPLAY=$NGROK_URL
  [[ $NGROK_DISPLAY != http* ]] && NGROK_DISPLAY="https://$NGROK_DISPLAY"
else
  NGROK_DISPLAY=
fi
export BACKEND_URL FRONTEND_URL DATABASE_URL NGROK_DISPLAY

# Stream logs; when we see both server "Backend URL (from your machine)" and client "Local:" (Vite ready), print summary once.
print_summary() {
  echo ""
  [ -n "$NGROK_DISPLAY" ] && echo "Ngrok:        $NGROK_DISPLAY -> $BACKEND_URL"
  echo "Frontend URL: $FRONTEND_URL"
  echo "Backend URL:  $BACKEND_URL"
  echo "Database:     $DATABASE_URL"
  echo ""
}
export -f print_summary

backend_ready=0
frontend_ready=0
summary_done=0

if [ -n "$NGROK_AUTHTOKEN" ] && [ -n "$NGROK_URL" ]; then
  log_services="server client ngrok"
else
  log_services="server client"
fi

docker compose logs -f $log_services 2>/dev/null | while IFS= read -r line; do
  echo "$line"
  # Backend ready when Flask has finished startup ("Serving Flask app" + "Debug mode")
  [[ "$line" == *"super-server"* ]] && [[ "$line" == *"Debug mode"* ]] && backend_ready=1
  [[ "$line" == *"super-client"* ]] && [[ "$line" == *"Local:"* ]] && frontend_ready=1
  if [ "$backend_ready" -eq 1 ] && [ "$frontend_ready" -eq 1 ] && [ "$summary_done" -eq 0 ]; then
    summary_done=1
    print_summary
  fi
done
