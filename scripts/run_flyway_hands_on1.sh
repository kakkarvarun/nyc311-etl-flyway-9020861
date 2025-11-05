#!/usr/bin/env bash
set -euo pipefail

# Network will be ${COMPOSE_PROJECT_NAME}_default (prog8850flyway_default)
NET="${COMPOSE_PROJECT_NAME:-prog8850flyway}_default"

echo "Using network: $NET"
docker run --rm --network "$NET" -v "$PWD/migrations:/flyway/sql" redgate/flyway   -locations=filesystem:/flyway/sql   -user=root -password=${MYSQL_ROOT_PASSWORD:-Secret5555}   -url=jdbc:mysql://db:3306/flyway_test migrate