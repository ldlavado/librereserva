# LibreReserva

Minimal reservation API for the course *Informática I: arquitectura de software moderna e IA*.

The domain core is independent of infrastructure. Adapters (HTTP, persistence, etc.) are added incrementally.

## Status

- [x] Pure domain model + unit tests
- [ ] HTTP adapter (FastAPI)
- [ ] Containerization
- [ ] Persistence (PostgreSQL)
- [ ] Local stack (docker-compose)

## Running tests

```bash
python -m unittest discover -s tests -v
```
