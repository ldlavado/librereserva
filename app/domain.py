"""Pure domain model for LibreReserva.

No infrastructure dependencies. The core can be tested and reused
independently of FastAPI, databases or any other adapter.
"""

from dataclasses import dataclass
from datetime import datetime


class IntervaloInvalido(ValueError):
    """Raised when the end of an interval is not after the start."""


class IntervaloOcupado(RuntimeError):
    """Raised when a reservation overlaps an existing one for the same resource."""


@dataclass(frozen=True, slots=True)
class Intervalo:
    inicio: datetime
    fin: datetime

    def __post_init__(self) -> None:
        if self.fin <= self.inicio:
            raise IntervaloInvalido("fin must be after inicio")

    def se_solapa(self, otro: "Intervalo") -> bool:
        return self.inicio < otro.fin and otro.inicio < self.fin


@dataclass(frozen=True, slots=True)
class Reserva:
    id: int
    recurso: str
    intervalo: Intervalo


class Agenda:
    """In-memory repository used for the first vertical slice."""

    def __init__(self) -> None:
        self._reservas: list[Reserva] = []

    def crear(self, recurso: str, intervalo: Intervalo) -> Reserva:
        if any(
            reserva.recurso == recurso and reserva.intervalo.se_solapa(intervalo)
            for reserva in self._reservas
        ):
            raise IntervaloOcupado(f"{recurso} is already reserved")
        reserva = Reserva(len(self._reservas) + 1, recurso, intervalo)
        self._reservas.append(reserva)
        return reserva

    def listar(self) -> tuple[Reserva, ...]:
        return tuple(self._reservas)

    def limpiar(self) -> None:
        self._reservas.clear()
