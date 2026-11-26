"""FastAPI HTTP adapter for LibreReserva."""

import logging
from datetime import datetime

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict

from .domain import Intervalo, IntervaloInvalido, IntervaloOcupado
from .persistence import PostgresAgenda

logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}',
)
logger = logging.getLogger("librereserva")

app = FastAPI(title="LibreReserva", version="0.3.0")
agenda = PostgresAgenda()


class ReservaEntrada(BaseModel):
    recurso: str
    inicio: datetime
    fin: datetime


class ReservaSalida(ReservaEntrada):
    model_config = ConfigDict(from_attributes=True)
    id: int


@app.get("/salud/viva")
def viva() -> dict[str, str]:
    return {"estado": "viva"}


@app.get("/salud/lista")
def lista() -> dict[str, str]:
    try:
        agenda.listar()
        return {"estado": "lista", "base_datos": "ok"}
    except Exception as exc:
        logger.error("database health check failed: %s", exc)
        raise HTTPException(status_code=503, detail="database unavailable") from exc


@app.get("/reservas", response_model=list[ReservaSalida])
def listar_reservas() -> list[ReservaSalida]:
    return [
        ReservaSalida(
            id=reserva.id,
            recurso=reserva.recurso,
            inicio=reserva.intervalo.inicio,
            fin=reserva.intervalo.fin,
        )
        for reserva in agenda.listar()
    ]


@app.post(
    "/reservas",
    response_model=ReservaSalida,
    status_code=status.HTTP_201_CREATED,
)
def crear_reserva(entrada: ReservaEntrada) -> ReservaSalida:
    try:
        reserva = agenda.crear(
            entrada.recurso,
            Intervalo(entrada.inicio, entrada.fin),
        )
        logger.info(
            "reservation created id=%s resource=%s",
            reserva.id,
            reserva.recurso,
        )
    except IntervaloInvalido as exc:
        logger.warning("invalid interval: %s", exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except IntervaloOcupado as exc:
        logger.warning("conflict: %s", exc)
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return ReservaSalida(
        id=reserva.id,
        recurso=reserva.recurso,
        inicio=reserva.intervalo.inicio,
        fin=reserva.intervalo.fin,
    )
