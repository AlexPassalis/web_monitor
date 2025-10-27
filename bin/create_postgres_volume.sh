#!/usr/bin/env bash
set -euo pipefail

POSTGRES_DOCKER_VOLUME="volume_pjoject_postgres"

if docker volume inspect "$POSTGRES_DOCKER_VOLUME" >/dev/null 2>&1; then
    echo "Docker volume \"$POSTGRES_DOCKER_VOLUME\" already exists."
else
    docker volume create "$POSTGRES_DOCKER_VOLUME" >/dev/null
    echo "Docker volume \"$POSTGRES_DOCKER_VOLUME\" created."
fi
