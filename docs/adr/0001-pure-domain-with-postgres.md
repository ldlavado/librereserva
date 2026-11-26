# ADR 0001: Keep the domain pure and use PostgreSQL for persistence

## Status

Accepted

## Context

LibreReserva started as a minimal vertical slice with an in-memory `Agenda`.  
The course requires evolving the system with real persistence while keeping the domain independent of infrastructure (hexagonal / ports & adapters style).

## Decision

- Keep `Intervalo`, `Reserva` and the business rules (overlap detection) inside the pure domain.
- Introduce a `PostgresAgenda` adapter that implements the same operations.
- Inject the adapter in the FastAPI application.
- Create the schema on startup for simplicity of the local development experience.

## Consequences

**Positive**
- Domain can still be unit-tested without a database.
- Easy to swap the persistence adapter later (e.g. for testing or another store).
- Aligns with the course emphasis on modularity and hexagonal architecture.

**Negative / Trade-offs**
- Schema creation on startup is convenient for local work but not ideal for production migrations.
- Overlap check is currently a simple query; concurrent inserts could still race without a unique constraint or transaction isolation strategy.

## Alternatives considered

- Keep the in-memory store for the whole project → rejected (does not meet the persistence learning goal).
- Put SQL directly in the domain → rejected (violates the independence principle).
