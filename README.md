# LibreReserva

Minimal reservation API for the course *Informática I: arquitectura de software moderna e IA*.

The domain core is independent of infrastructure. Adapters (HTTP, persistence, etc.) are added incrementally.

## Status

- [x] Pure domain model + unit tests
- [x] HTTP adapter (FastAPI)
- [x] Containerization
- [ ] Persistence (PostgreSQL)
- [ ] Local stack (docker-compose)

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Run tests
python -m unittest discover -s tests -v

# Start the API
uvicorn app.main:app --reload
```

API: http://127.0.0.1:8000  
Docs: http://127.0.0.1:8000/docs

## Running with Docker

```bash
docker build -t librereserva .
docker run --rm -p 8000:8000 librereserva
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
