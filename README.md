# dicom-compare

Compare two DICOM scans (a prior and a current one) and get a difference map plus
measurements of what changed. A learning project built like an enterprise service:
FastAPI, PostgreSQL, React, Azure, and later a LangGraph agent.

> For learning and measurement only. Not a medical device, not for diagnosis.
> No patient data is stored.

## Run it locally (Windows / PowerShell)

Prerequisites: Python 3.12+, Docker Desktop (running), Git.

```powershell
# 1. Settings: copy the example and edit the password if you like
Copy-Item .env.example .env

# 2. Start Postgres in Docker
docker compose up -d
docker compose ps          # wait until "healthy"

# 3. Backend: virtual environment + dependencies
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"

# 4. Database tables, and your first admin user
alembic upgrade head
python -m app.scripts.create_user --email admin@example.com --role admin

# 5. Run the API (API docs at http://localhost:8000/docs)
uvicorn app.main:app --reload
```

In a second terminal, the frontend (Node.js 20+):

```powershell
cd frontend
npm install        # first time, and whenever package.json changes
npm run dev        # then open http://localhost:5173
```

The frontend calls `/api/...` on its own address; Vite forwards those requests
to the backend on port 8000, so both must be running.

## Quality checks

From `backend/`:

```powershell
pytest          # tests (needs Postgres running)
ruff check .    # lint
ruff format .   # auto-format
mypy app tests  # type check
alembic check   # models and migrations in sync
```

From `frontend/`:

```powershell
npm run lint       # ESLint
npm run typecheck  # TypeScript
npm run build      # production build into dist/
```

GitHub Actions runs all of these on every pull request (`.github/workflows/ci.yml`).

## Project layout

```text
backend/
  app/
    main.py        FastAPI app; plugs in the routers
    core/          settings, security (hashing, JWT), permissions
    db/            SQLAlchemy models and session
    schemas/       Pydantic request/response shapes
    services/      business rules (no HTTP)
    api/           routers (endpoints) and dependencies
    scripts/       command-line tools (create_user)
  alembic/         database migrations
  tests/           pytest tests
frontend/
  src/
    api/           the one place that calls the backend
    auth/          login state, token storage, route guard
    pages/         Login, Home, Users (admin)
    components/    shared layout
docker-compose.yml local Postgres
.env.example       every setting the app reads (copy to .env)
```
