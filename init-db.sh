#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE edupulse_db;
    -- Keycloak expects a database named 'keycloak' (not 'keycloak_db'), create both to be safe
    CREATE DATABASE keycloak;
    CREATE DATABASE keycloak_db;
    GRANT ALL PRIVILEGES ON DATABASE edupulse_db TO postgres;
    GRANT ALL PRIVILEGES ON DATABASE keycloak TO postgres;
    GRANT ALL PRIVILEGES ON DATABASE keycloak_db TO postgres;
EOSQL
