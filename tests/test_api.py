from datetime import UTC, datetime, timedelta
import unittest

from fastapi.testclient import TestClient

from app.main import app
from app.persistence import PostgresAgenda


class ApiContractTest(unittest.TestCase):
    """HTTP contract tests.

    These tests assume a running PostgreSQL instance is available
    (the same default used by the application).
    For a fully isolated suite, replace PostgresAgenda with a fake
    or use Testcontainers in a later iteration.
    """

    def setUp(self) -> None:
        self.client = TestClient(app)
        # Clean state if the DB is reachable
        try:
            agenda = PostgresAgenda()
            agenda.limpiar()
        except Exception:
            self.skipTest("PostgreSQL not available for contract tests")

    def test_salud(self) -> None:
        r = self.client.get("/salud/viva")
        self.assertEqual(200, r.status_code)
        self.assertEqual({"estado": "viva"}, r.json())

    def test_crear_y_listar(self) -> None:
        inicio = datetime(2026, 8, 10, 8, tzinfo=UTC)
        fin = inicio + timedelta(hours=1)
        payload = {
            "recurso": "A-101",
            "inicio": inicio.isoformat().replace("+00:00", "Z"),
            "fin": fin.isoformat().replace("+00:00", "Z"),
        }

        r = self.client.post("/reservas", json=payload)
        self.assertEqual(201, r.status_code)
        body = r.json()
        self.assertEqual("A-101", body["recurso"])
        self.assertIn("id", body)

        r = self.client.get("/reservas")
        self.assertEqual(200, r.status_code)
        self.assertEqual(1, len(r.json()))

    def test_rechaza_solapamiento(self) -> None:
        inicio = datetime(2026, 8, 10, 8, tzinfo=UTC)
        fin = inicio + timedelta(hours=1)
        payload = {
            "recurso": "A-101",
            "inicio": inicio.isoformat().replace("+00:00", "Z"),
            "fin": fin.isoformat().replace("+00:00", "Z"),
        }
        self.client.post("/reservas", json=payload)

        r = self.client.post("/reservas", json=payload)
        self.assertEqual(409, r.status_code)

    def test_rechaza_intervalo_invalido(self) -> None:
        inicio = datetime(2026, 8, 10, 8, tzinfo=UTC)
        payload = {
            "recurso": "A-101",
            "inicio": inicio.isoformat().replace("+00:00", "Z"),
            "fin": inicio.isoformat().replace("+00:00", "Z"),
        }
        r = self.client.post("/reservas", json=payload)
        self.assertEqual(422, r.status_code)
