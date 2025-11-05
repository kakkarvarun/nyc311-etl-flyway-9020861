#!/usr/bin/env bash
set -euo pipefail

NET="${COMPOSE_PROJECT_NAME:-prog8850flyway}_default"

echo "Using network: $NET"
# Ensure DB exists
docker exec -i $(docker compose ps -q db) mysql -uroot -p${MYSQL_ROOT_PASSWORD:-Secret5555} -e "CREATE DATABASE IF NOT EXISTS nyc311;"

docker run --rm --network "$NET" -v "$PWD/nyc311/migrations:/flyway/sql" redgate/flyway   -locations=filesystem:/flyway/sql   -user=root -password=${MYSQL_ROOT_PASSWORD:-Secret5555}   -url=jdbc:mysql://db:3306/nyc311 migrate