#!/bin/bash
# Database Migration Script
# Run new migration files against PostgreSQL in Docker

set -e

MIGRATIONS_DIR="./database/migrations"
CONTAINER="dastern-postgres"
DB_USER="dastern"
DB_NAME="dastern"

echo "🔄 Running database migrations..."

# Check if container is running
if ! docker ps | grep -q "$CONTAINER"; then
    echo "❌ Error: $CONTAINER is not running"
    exit 1
fi

# Run each migration file
for migration in "$MIGRATIONS_DIR"/*.sql; do
    if [ -f "$migration" ]; then
        echo "📝 Applying: $(basename "$migration")"
        docker exec -i "$CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" < "$migration"
        echo "✅ Applied: $(basename "$migration")"
    fi
done

echo "✅ All migrations completed!"
