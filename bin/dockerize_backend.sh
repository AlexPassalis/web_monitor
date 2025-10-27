#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="backend"

if ! docker compose ps -q "$SERVICE_NAME" | grep -q .; then
    echo "\"$SERVICE_NAME\" service is not running."
    make start
fi

if tty -s; then
    USE_TTY="-it"
else
    USE_TTY="-T"
fi

BUILDKIT_PROGRESS=plain docker compose exec $USE_TTY "$SERVICE_NAME" "$@"
