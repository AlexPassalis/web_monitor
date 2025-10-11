#!/usr/bin/env bash
set -euo pipefail

docker_network="network-motowear"

if docker network inspect "$docker_network" >/dev/null; then
    echo "Docker network \"$docker_network\" already exists."
else
    docker network create -d overlay "$docker_network"
    echo "Creating Docker network \"$docker_network\"."
fi
