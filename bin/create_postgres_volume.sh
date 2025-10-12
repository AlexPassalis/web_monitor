#!/usr/bin/env bash
set -euo pipefail

docker_volume="volume_pjoject_postgres"

if docker volume inspect "$docker_volume" >/dev/null 2>&1; then
    echo "Docker volume \"$docker_volume\" already exists."
else
    docker volume create "$docker_volume" >/dev/null
    echo "Docker volume \"$docker_volume\" created."
fi
