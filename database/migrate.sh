#!/bin/bash
# Database Migration Script for DasTern
# Usage: ./database/migrate.sh [migration_file.sql]

set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Default values
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_USER=${DB_USER:-dastern}
DB_PASSWORD=${DB_PASSWORD:-dastern_secure_password_2026}
DB_NAME=${DB_NAME:-dastern}

# Check if migration file is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <migration_file.sql>"
    echo "Example: $0 database/migrations/004_new_feature.sql"
    exit 1
fi

MIGRATION_FILE=$1

if [ ! -f "$MIGRATION_FILE" ]; then
    echo "Error: Migration file '$MIGRATION_FILE' not found!"
    exit 1
fi

echo "=========================================="
echo "DasTern Database Migration"
echo "=========================================="
echo "Host: $DB_HOST:$DB_PORT"
echo "Database: $DB_NAME"
echo "Migration: $MIGRATION_FILE"
echo "=========================================="
echo ""

# Check if using Docker container
if docker ps --format '{{.Names}}' | grep -q "dastern-postgres"; then
    echo "✓ Detected running Docker container"
    echo "Applying migration via Docker..."
    docker exec -i dastern-postgres psql -U "$DB_USER" -d "$DB_NAME" < "$MIGRATION_FILE"
else
    echo "✓ Applying migration via direct connection..."
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$MIGRATION_FILE"
fi

echo ""
echo "=========================================="
echo "✓ Migration completed successfully!"
echo "=========================================="
