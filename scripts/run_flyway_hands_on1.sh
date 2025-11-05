#!/usr/bin/env bash
set -euo pipefail

# Pick a Docker network name that matches docker compose
NET="${COMPOSE_PROJECT_NAME:-prog8850flyway}_default"

# On Windows Git Bash, pwd -W gives a Windows-style path (D:\...)
if command -v pwd -W >/dev/null 2>&1; then
  HOST_PWD="$(pwd -W)"
else
  HOST_PWD="$(pwd)"
fi

echo "Using network: $NET"
echo "Host project dir: $HOST_PWD"

docker run --rm --network "$NET" \
  -v "${HOST_PWD}/migrations:/flyway/sql" redgate/flyway \
  -locations=filesystem:/flyway/sql \
  -user=root -password="${MYSQL_ROOT_PASSWORD:-Secret5555}" \
  -url=jdbc:mysql://db:3306/flyway_test migrate
