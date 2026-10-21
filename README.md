# Enterprise Migration Platform

## Phase 8 — Connected Migration Console

The React frontend is now connected to the FastAPI backend.

### UI workflow

1. Enter source DB2 connection.
2. Enter target PostgreSQL connection.
3. Test the source.
4. Discover schemas.
5. Select a schema.
6. Discover tables.
7. Build a dependency-aware plan.
8. Select tables.
9. Configure batch size and workers.
10. Start migration.
11. Poll live job status.
12. View migration audit events.

### Run backend

```bash
cd infrastructure
docker compose up -d

cd ../backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Run frontend

```bash
cd frontend
npm install
npm run dev
```

Optional API URL:

```bash
VITE_API_URL=http://localhost:8000/api
```

### Current limitations

- Passwords are currently entered into the UI and sent to the API; production secret storage is Phase 10.
- The migration runner is still an MVP background worker.
- Durable PK-based resume is not fully implemented.
- Constraints/indexes are discovered but not yet automatically deployed by the runner.
- CDC/cutover is not implemented.

### Remaining roadmap

Phase 9 — Production reliability and resumability

Phase 10 — Security and enterprise operations

Phase 11 — CDC and zero-downtime cutover

Phase 12 — Multi-database connectors

Phase 13 — AI Migration Advisor
