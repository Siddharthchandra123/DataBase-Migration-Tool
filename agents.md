AGENTS.md — Db2 → PostgreSQL Migration Platform
Updated: 2026-10-22
Purpose: Durable engineering handoff and operating instructions for future AI-assisted work. Keep this file updated after each meaningful change.
Product goal
Build a reliable, observable IBM Db2 → PostgreSQL migration platform with schema discovery, dependency planning, visual workflow, data movement, relational integrity, validation, failure recovery, and reproducible deployment.
Repository map (verified from supplied archive)
- backend/app/api/: connections, discovery, migrations, schema mapping, validation, audit.
- backend/app/connectors/: Db2, Db2 catalog, PostgreSQL, connector factory.
- backend/app/discovery/dependencies.py: dependency analysis.
- backend/app/migration/: constraints, DDL, executor, loader, parallel, planner, runner, transformer.
- backend/app/schema/: DDL, models, type mapping.
- backend/app/validation/: checkpoints, checksum, validation service.
- backend/app/audit/service.py: audit service.
- backend/tests/: pytest tests.
- frontend/src/: React/Vite app.
- infrastructure/docker-compose.yml: container setup.
- README.md: user-facing documentation.
Known benchmark and development context
- Source test schema: MIGTEST, 13 tables, 68 rows, 22 foreign keys.
- Edge cases: self-referencing CATEGORIES FK; composite ORDER_ITEMS → INVENTORY FK.
- Prior reported result: rows migrated; PostgreSQL target foreign-key query returned zero. Reverify on a fresh test run.
- Development environment: Windows PowerShell, Docker, Python backend, React frontend.
- Previously used local endpoints: backend http://localhost:8000, frontend http://localhost:5173.
- Database container names reported previously: migration-db2, migration-target-db. Confirm actual environment rather than assuming.
- Do not include credentials, passwords, connection strings with secrets, or .env contents in this document.
Completion phases
1. Relational correctness: discover PK/unique/FK definitions with ordered composite columns; create tables, load data, apply constraints, validate all 22 FKs.
2. Data integrity: nullability, defaults, sequences/identity, row counts, deterministic checksums, mismatch reports.
3. Recovery: transactional batches, idempotent checkpoints, bounded retries, crash/resume tests.
4. Execution: dependency-aware parallelism, resource controls, cancellation, performance benchmarks.
5. API and UI: robust validation/errors, progress, logs, reports, automated tests.
6. Operations: Docker Compose, environment templates, secret handling, CI, reproducible E2E tests.
Mandatory engineering rules
- Inspect existing implementation and tests before editing; prefer small targeted changes over rewrites.
- Keep source/target schema mapping explicit; do not default silently to public.
- Never claim FK parity based on relationship visualization or row counts.
- Group Db2 composite FK columns by constraint identity and preserve ordinal position.
- Separate table creation, data load, and FK creation to support cycles/self-references.
- Avoid destructive operations on shared databases; scope test cleanup to dedicated disposable schemas.
- Use parameterized queries for data and safely quoted identifiers for dynamic SQL.
- Ensure migration retries cannot duplicate rows or silently skip partially written batches.
- Run relevant pytest tests and report exact pass/fail results. If no DB is accessible, label integration checks unverified.
- No secrets in code, logs, README, commits, ZIPs, or AGENTS.md.
Current state / next action (2026-10-22)
- Reported working: FastAPI backend starts and its Swagger UI opens; React/Vite frontend starts. Backend and frontend were both confirmed started by the user.
- Automated tests: user reports the full python -m pytest -v suite passed; exact test count/output was not supplied in this session.
- Metadata database: migration-metadata-db (PostgreSQL 16) mapped to Windows host port 5433. User confirmed SQLAlchemy metadata connection succeeded. Earlier password failures arose while a Windows PostgreSQL listener also occupied IPv4 5433; the precise resolution was not independently recorded. Never store the test password in this file.
- Db2 source: migration-db2 mapped to host port 50000. User confirmed Db2 checks succeeded; source schema MIGTEST benchmark remains 13 tables, 68 rows, 22 FKs (historical baseline, not revalidated today).
- PostgreSQL target: original migration-target-db failed to start on host port 5434 because Windows active IPv4 exclusion covers 5434-5533. No active listener was seen. Admin netsh ... delete excludedportrange returned Access denied, including with store=active. wsl --shutdown did not release the exclusion. Do not repeat disruptive network resets.
- Target replacement plan: user opted to create a fresh target using host port 15434, PostgreSQL internal port 5432, database migration_target, user target, and a distinct named volume migration-target-data-v2; prior instructions proposed renaming the old container to migration-target-db-old. Creation, actual target startup, and saved-connection update have not been confirmed. Inspect docker ps -a, docker volume ls, and the configured target connection before proceeding; do not assume the old container was deleted.
- Frontend build: npm run preview initially failed because dist was absent. npm run build launched Vite dev server instead of a build and hit Windows EACCES on ::1:5173. User was instructed to run npx vite build, set scripts.build=vite build using npm pkg set, and use npm run dev -- --host 127.0.0.1 --port 15173. User subsequently confirmed frontend started, but the exact script/port currently in use is not independently verified.
- Potential config edits: a bulk PowerShell port replacement (5434 -> 15434) was suggested for backend/frontend files; user did not provide resulting file-change output. Inspect source and saved metadata connection records rather than assuming the replacement ran. Metadata port 5433 must remain separate from target port.
- E2E migration remains BLOCKED / NOT VERIFIED until target is running and application can connect. Do not claim 13 tables / 68 rows / 22 FKs were migrated or validated in the new target.
Next exact actions
1. From project root run docker ps -a --filter "name=migration" and check which target container exists and is running.
2. If target was recreated on 15434, verify docker exec migration-target-db pg_isready -U target -d migration_target, then verify Windows-side TCP auth with Psycopg using the actual target credentials without printing them.
3. Locate and update any saved target connection in the app metadata store/UI to host 127.0.0.1, port 15434, db migration_target, user target; do not alter METADATA_DATABASE_URL (5433).
4. Verify frontend API requests reach FastAPI and test Db2 discovery for MIGTEST.
5. Run the end-to-end migration; query actual target row counts and foreign keys, including composite and self-referencing constraints. Capture logs and checkpoint evidence.
6. Update this document with observed commands/results; rotate temporary development passwords and keep secrets out of logs.
Change log
- 2026-10-21: Created persistent project handoff file and repository inventory; no runtime functionality changed.
- 2026-10-22: Documented user-reported passing pytest suite, operational backend/frontend and metadata/Db2 checks, Windows reserved-port conflict, proposed target replacement on 15434, and outstanding end-to-end validation. Documentation only; no repository source files modified by this update.
Session update template
At the end of each coding session update:
- Date:
- Files changed:
- Decisions / assumptions:
- Commands and test results:
- Known issues:
- Next exact action: