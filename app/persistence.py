"""PostgreSQL persistence adapter for LibreReserva."""

import os
from datetime import datetime

import psycopg
from psycopg.rows import dict_row

from .domain import Intervalo, Reserva, IntervaloOcupado


class PostgresAgenda:
    """PostgreSQL-backed repository."""

    def __init__(self, dsn: str | None = None) -> None:
        self.dsn = dsn or os.getenv(
            "DATABASE_URL",
            "postgresql://librereserva:librereserva@localhost:5432/librereserva",
        )
        self._ensure_schema()

    def _connect(self):
        return psycopg.connect(self.dsn, row_factory=dict_row)

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS reservas (
                        id SERIAL PRIMARY KEY,
                        recurso TEXT NOT NULL,
                        inicio TIMESTAMPTZ NOT NULL,
                        fin TIMESTAMPTZ NOT NULL
                    );
                    CREATE INDEX IF NOT EXISTS idx_reservas_recurso
                        ON reservas (recurso);
                    """
                )
            conn.commit()

    def crear(self, recurso: str, intervalo: Intervalo) -> Reserva:
        with self._connect() as conn:
            with conn.cursor() as cur:
                # Check for overlap
                cur.execute(
                    """
                    SELECT id FROM reservas
                    WHERE recurso = %s
                      AND inicio < %s
                      AND fin > %s
                    LIMIT 1
                    """,
                    (recurso, intervalo.fin, intervalo.inicio),
                )
                if cur.fetchone():
                    raise IntervaloOcupado(f"{recurso} is already reserved")

                cur.execute(
                    """
                    INSERT INTO reservas (recurso, inicio, fin)
                    VALUES (%s, %s, %s)
                    RETURNING id
                    """,
                    (recurso, intervalo.inicio, intervalo.fin),
                )
                row = cur.fetchone()
                conn.commit()
                return Reserva(row["id"], recurso, intervalo)

    def listar(self) -> tuple[Reserva, ...]:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, recurso, inicio, fin
                    FROM reservas
                    ORDER BY id
                    """
                )
                rows = cur.fetchall()
                return tuple(
                    Reserva(
                        r["id"],
                        r["recurso"],
                        Intervalo(r["inicio"], r["fin"]),
                    )
                    for r in rows
                )

    def limpiar(self) -> None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("TRUNCATE TABLE reservas RESTART IDENTITY")
            conn.commit()
