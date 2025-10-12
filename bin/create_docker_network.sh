#!/usr/bin/env bash
set -euo pipefail

docker_network="network_project"

if docker network inspect "$docker_network" >/dev/null 2>&1; then
    echo "Docker network \"$docker_network\" already exists."
else
    docker network create -d bridge "$docker_network"
    echo "Docker network \"$docker_network\" created."
fi
