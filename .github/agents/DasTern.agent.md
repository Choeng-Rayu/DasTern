---
description: 'The AI agent must treat updates to sensitive configuration files—such as database schemas, environment variables, and initialization scripts—as high-risk changes. Any modification to these files requires validation against Docker configuration and a full container lifecycle update to ensure system consistency, stability, and correctness. The agent is responsible for ensuring that Docker containers, databases, and application services remain synchronized with the latest project configuration.'

tools: ['vscode', 'execute', 'read', 'edit', 'search', 'web',
 'copilot-container-tools/*', 'agent',
 'pylance-mcp-server/*',
 'ms-python.python/getPythonEnvironmentInfo',
 'ms-python.python/getPythonExecutableCommand',
 'ms-python.python/installPythonPackage',
 'ms-python.python/configurePythonEnvironment',
 'todo']

model: Claude Sonnet 4.5 (copilot)

---
AI AGENT RULES – DOCKER, DATABASE, AND FILE STRUCTURE SAFETY


Core Rules
==========

1. Sensitive File Awareness
---------------------------
Treat the following files and directories as sensitive and high-risk:

- Database schema files
  (SQL files, Prisma schema, migration files, ORM configurations)

- Environment variables
  (.env, .env.local, .env.production, .env.*)

- Secrets and credentials
  (API keys, database passwords, tokens)

- Database initialization scripts
  (init.sql, seed.sql, migration scripts)

Any detected change to these files MUST trigger a Docker consistency check
and container lifecycle validation.


2. Good Project File Structure Enforcement
------------------------------------------
The agent MUST enforce and maintain a clear, predictable project structure.

Recommended structure:

- docker/
  - db/
    - init.sql
    - seed.sql
    - migrations/
  - nginx/
  - scripts/

- backend/
  - src/
  - prisma/ OR migrations/
  - .env.example

- frontend/
  - src/
  - .env.example

- .env                (never committed)
- .env.example        (always committed)
- docker-compose.yml
- README.md

Rules:
- Sensitive files must NOT be scattered randomly.
- Database scripts must live under docker/db/ or a clearly defined folder.
- .env files must NEVER be hardcoded inside source code.
- .env.example must reflect all required environment variables.
- docker-compose.yml must reference correct paths and filenames.

If file placement is incorrect, the agent must suggest or apply restructuring.


3. Docker Compose Validation
----------------------------
After modifying any sensitive files, the agent MUST inspect docker-compose.yml
for the following:

- Environment variable mappings
- Database-related volume mounts
- Initialization scripts (docker-entrypoint-initdb.d)
- Database image versions
- Configuration overrides

If mismatches, missing references, or outdated paths are found,
the agent MUST update docker-compose.yml accordingly.


4. Container Lifecycle Enforcement
----------------------------------
When sensitive files are changed, the agent MUST enforce a full container
rebuild and restart:

- docker compose build
- docker compose down
- docker compose up -d

Skipping rebuilds is NOT allowed for:
- Database schema changes
- Migration updates
- .env or environment variable changes


5. Database State Verification
------------------------------
After containers restart, the agent MUST verify:

- Database schema matches the latest definitions
- All migrations executed successfully
- Database initialization scripts ran correctly
- No startup or runtime errors exist in container logs


6. Error Handling and Recovery
------------------------------
If any issue occurs (migration failure, env mismatch, container crash):

- Analyze container and application logs
- Identify the root cause
- Propose or apply fixes
- Rebuild and restart containers again
- Repeat verification until the system is stable


Expected Agent Behavior
======================

- Proactively warns when a change requires Docker rebuilds
- Never assumes .env or schema changes apply without restart
- Enforces clean and scalable file structure
- Keeps database, containers, and application configuration synchronized
- Prioritizes system stability over speed
- Clearly reports issues and applies fixes when possible

End of Rules
============
