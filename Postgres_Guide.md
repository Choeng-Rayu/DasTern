
**Postgres Connection Guide**

- **Purpose:** quick commands to connect to the Postgres instance used by this project. The project `.env` contains these values:

- `DB_USER=dastern`
- `DB_PASSWORD=dastern_capstone_2`
- `DB_NAME=dastern`
- `DB_PORT=5432`
- `DATABASE_URL=postgresql://dastern:dastern_capstone_2@postgres:5432/dastern`

Use the snippet that matches where you run the client (host machine vs inside Docker).

**Connect from host (PSQL on your machine)**

If the container maps port 5432 to the host (common docker-compose setup):

```bash
# interactive (prompts for password)
psql -h localhost -p 5432 -U dastern -d dastern

# provide password via env (safer than inline password in the command)
PGPASSWORD='dastern_capstone_2' psql -h localhost -p 5432 -U dastern -d dastern

# using full connection URI
PGPASSWORD='dastern_capstone_2' psql "postgresql://dastern:dastern_capstone_2@localhost:5432/dastern"
```

To run the schema file from the repo:

```bash
# from project root
psql -h localhost -p 5432 -U dastern -d dastern -f database/final-schema.sql

# or using DATABASE_URL (if it resolves to localhost)
PGPASSWORD='dastern_capstone_2' psql "$DATABASE_URL" -f database/final-schema.sql
```

**Run psql inside the Postgres container (recommended if host can't resolve `postgres`)**

```bash
# list containers and find postgres container name
docker ps

# run a shell and then psql (replace <container_name>)
docker exec -it <container_name> psql -U dastern -d dastern

# with docker-compose (service name often 'postgres' — replace if different)
docker-compose exec postgres psql -U dastern -d dastern
```

**Run a temporary psql client on the Docker network**

If other containers refer to the DB host as `postgres`, run a client in the same network:

```bash
# replace <network_name> with your compose network (usually <project>_default)
docker run --rm -it --network <network_name> postgres \
	psql "postgresql://dastern:dastern_capstone_2@postgres:5432/dastern"
```

**Connect from another service container (useful in compose)**

```bash
docker-compose exec your_service_name bash
# then inside container
psql "$DATABASE_URL"
```

**Troubleshooting & tips**

- If connecting from host fails, check `docker ps` to confirm port mapping shows something like `0.0.0.0:5432->5432/tcp`.
- If host cannot resolve `postgres`, use `localhost` or connect from a container on the same network.
- Use `docker logs <container>` to inspect Postgres start errors.
- Avoid placing passwords on the shell command line in production; prefer `.pgpass`, environment variables, or Docker secrets.
- Useful psql commands: `\l` (list DBs), `\c dbname` (connect), `\dt` (list tables), `\i path/to/file.sql` (run file from psql), `\q` (quit).

If you want, I can detect your running Postgres container now and show the exact `docker exec` or `psql` command to run.

