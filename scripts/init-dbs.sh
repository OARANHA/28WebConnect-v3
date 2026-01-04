#!/bin/bash
set -e

# This script runs inside the official postgres image during first-time initialization
# It creates the databases if they do not already exist.

function create_db_if_not_exists() {
  local dbname="$1"
  echo "[initdb] Ensuring database '$dbname' exists..."
  psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres -tc "SELECT 1 FROM pg_database WHERE datname = '${dbname}'" | grep -q 1 || \
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres -c "CREATE DATABASE \"${dbname}\";"
}

create_db_if_not_exists "evo_ai"
create_db_if_not_exists "evolution_db"

echo "[initdb] Databases ensured."
