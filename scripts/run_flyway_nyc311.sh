#!/usr/bin/env bash
set -euo pipefail

NET="${COMPOSE_PROJECT_NAME:-prog8850flyway}_default"

# Use Windows path on Git Bash; normal path elsewhere
if command -v pwd -W >/dev/null 2>&1; then
  HOST_PWD="$(pwd -W)"
else
  HOST_PWD="$(pwd)"
fi

echo "Using network: $NET"
# Ensure DB exists
docker exec -i $(docker compose ps -q db) \
  mysql -uroot -p${MYSQL_ROOT_PASSWORD:-Secret5555} \
  -e "CREATE DATABASE IF NOT EXISTS nyc311;"

docker run --rm --network "$NET" \
  -v "${HOST_PWD}/nyc311/migrations:/flyway/sql" redgate/flyway \
  -locations=filesystem:/flyway/sql \
  -user=root -password="${MYSQL_ROOT_PASSWORD:-Secret5555}" \
  -url=jdbc:mysql://db:3306/nyc311 migrate
