# LibreReserva

Minimal reservation API for the course *Informática I: arquitectura de software moderna e IA*.

The domain core is independent of infrastructure. Adapters (HTTP, persistence, etc.) are added incrementally.

## Status

- [x] Pure domain model + unit tests
- [x] HTTP adapter (FastAPI)
- [x] Containerization
- [x] Persistence (PostgreSQL)
- [x] Local stack (docker-compose)
- [x] Basic architecture documentation (C4 + ADR)
- [x] HTTP contract tests

## Quick start (recommended)

```bash
docker compose up --build
```

API: http://127.0.0.1:8000  
Docs: http://127.0.0.1:8000/docs

Stop and clean:

```bash
docker compose down -v
```

## Architecture

- [C4 diagrams](docs/c4.md)
- [ADR 0001 – Pure domain with PostgreSQL](docs/adr/0001-pure-domain-with-postgres.md)

## Running tests

```bash
# Domain unit tests (no DB required)
python -m unittest discover -s tests -v

# Contract tests need a running PostgreSQL (or docker compose up)
pip install -r requirements-dev.txt
python -m unittest tests.test_api -v
```

## Running locally (without Docker)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

docker run --rm -d \
  --name librereserva-db \
  -e POSTGRES_USER=librereserva \
  -e POSTGRES_PASSWORD=librereserva \
  -e POSTGRES_DB=librereserva \
  -p 5432:5432 \
  postgres:16-alpine

uvicorn app.main:app --reload
```

## Manual checks

```bash
curl -fsS http://127.0.0.1:8000/salud/viva

curl -i -X POST http://127.0.0.1:8000/reservas \
  -H 'content-type: application/json' \
  -d '{"recurso":"A-101","inicio":"2026-08-10T08:00:00Z","fin":"2026-08-10T09:00:00Z"}'

curl -fsS http://127.0.0.1:8000/reservas
```

A second POST with the same interval must return **409**. An inverted interval must return **422**.
