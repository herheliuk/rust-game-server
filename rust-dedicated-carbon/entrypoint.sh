#!/usr/bin/env bash
set -e

SERVER_LOG_PREFIX="${SERVER_LOG_PREFIX:-ds_}"
SERVER_LOGS_FOLDER="${SERVER_LOGS_FOLDER:-./server/logs/}"
LAST_SERVER_LOG_NAME="${LAST_SERVER_LOG_NAME:-ds_last.log}"

SERVER_SEED_FILE="${SERVER_SEED_FILE:-./server/server.seed}"

RUST_SERVER_STEAM_APP_ID="${RUST_SERVER_STEAM_APP_ID:-258550}"
STEAM_SH_PATH="${STEAM_SH_PATH:-/home/steam/steamcmd/steamcmd.sh}"

SERVER_PORT="${SERVER_PORT:-28015}"
SERVER_QUERYPORT="${SERVER_QUERYPORT:-28016}"
APP_PORT="${APP_PORT:-28082}"
RCON_PORT="${RCON_PORT:-28017}"
RCON_PASSWORD=${RCON_PASSWORD:-$(openssl rand -base64 32)}


SERVER_LOGS_FILE="$SERVER_LOGS_FOLDER/$SERVER_LOG_PREFIX$(date +'%Y-%m-%d_%H-%M-%S').log"

mkdir -p "$SERVER_LOGS_FOLDER"

ln -sf "$SERVER_LOGS_FILE" "$SERVER_LOGS_FOLDER/$LAST_SERVER_LOG_NAME"
ln -sf "$SERVER_LOGS_FILE" "./$LAST_SERVER_LOG_NAME"

if [ -f "$SERVER_SEED_FILE" ]; then
  SERVER_SEED="$(cat "$SERVER_SEED_FILE")"
else # generate seed: 0..2147483647
  rand=$(od -An -N4 -tu4 /dev/urandom)
  SERVER_SEED=$(( rand & 0x7fffffff ))
  echo "$SERVER_SEED" > "$SERVER_SEED_FILE"
fi


"$STEAM_SH_PATH" \
  +force_install_dir "$(pwd)" \
  +login anonymous \
  +app_update "$RUST_SERVER_STEAM_APP_ID" \
  +quit

./carbon.sh -batchmode \
  "+server.seed" "$SERVER_SEED" \
\
  "+server.port" "$SERVER_PORT" \
  "+server.queryport" "$SERVER_QUERYPORT" \
  "+app.port" "$APP_PORT" \
\
  "+rcon.password" "${RCON_PASSWORD}" \
  "+rcon.port" "${RCON_PORT}" \
\
  "$@" \
\
  -logfile "$SERVER_LOGS_FILE" 2>&1
