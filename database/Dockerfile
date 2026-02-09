FROM postgres:16-alpine

# Copy schema files
COPY final-schema.sql /docker-entrypoint-initdb.d/01-schema.sql

# Set proper permissions
RUN chmod 755 /docker-entrypoint-initdb.d/01-schema.sql
