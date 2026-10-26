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

# 4. Run the API, then open http://localhost:8000/docs
uvicorn app.main:app --reload
```

## Quality checks (run from `backend/`)

```powershell
pytest          # tests
ruff check .    # lint
ruff format .   # auto-format
mypy app        # type check
```

## Project layout

```text
backend/
  app/
    main.py        FastAPI app; plugs in the routers
    core/          settings (and soon security: hashing, JWT)
    db/            SQLAlchemy base class and session
    api/           routers (endpoints)
  tests/           pytest tests
docker-compose.yml local Postgres
.env.example       every setting the app reads (copy to .env)
```
