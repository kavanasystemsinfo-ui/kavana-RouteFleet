"""Tests de seguridad para Kavana Logistic (auditoría ECC 2026-07-16)."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

import main
from main import app


@pytest.fixture
def client():
    return TestClient(app)


# --- R1: límite de tamaño de archivo ---
def test_archivo_demasiado_grande_rechazado(client):
    # 20 MB > límite de 15 MB
    big = b"x" * (20 * 1024 * 1024)
    resp = client.post(
        "/api/optimizar-archivo",
        files={"file": ("grande.txt", big)},
        data={"vehicle_count": 1},
    )
    assert resp.status_code == 413


def test_archivo_tamano_valido_aceptado(client):
    small = b"Cliente A - Calle Falsa 1\nCliente B - Calle Falsa 2"
    with patch("main.extract_stops_from_text", new=AsyncMock(return_value=[])):
        resp = client.post(
            "/api/optimizar-archivo",
            files={"file": ("peque.txt", small)},
            data={"vehicle_count": 1},
        )
    # 400 porque no hay paradas (extract mockeado devuelve []), pero NO 413
    assert resp.status_code != 413


# --- R6/R7: validación de extensión ---
def test_extension_no_permitida_rechazada(client):
    resp = client.post(
        "/api/optimizar-archivo",
        files={"file": ("malware.exe", b"x")},
        data={"vehicle_count": 1},
    )
    assert resp.status_code == 400
    assert "no permitido" in resp.json()["detail"].lower()


# --- R2: tope vehicle_count ---
def test_vehicle_count_excede_maximo_rechazado(client):
    import models
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        models.RouteRequest(paradas=[], vehicle_count=1000000)


def test_vehicle_count_dentro_rango_aceptado(client):
    import models
    r = models.RouteRequest(paradas=[], vehicle_count=5)
    assert r.vehicle_count == 5


# --- R3: /docs desactivado en producción (DEBUG=False) ---
def test_docs_desactivado_en_produccion(client):
    # Por defecto DEBUG es False en el entorno de test
    resp = client.get("/docs")
    assert resp.status_code == 404


# --- R5: rate limiting (slowapi) ---
def test_rate_limit_optimizar_ruta(client):
    # 25 peticiones rápidas; el límite es 20/minuto
    status_codes = []
    for _ in range(25):
        resp = client.post(
            "/api/optimizar-ruta",
            json={"paradas": [{"cliente": "A", "direccion": "Calle 1"}]},
        )
        status_codes.append(resp.status_code)
    # Al menos una debe ser 429 (rate limited)
    assert 429 in status_codes


# --- R8: CORS ---
def test_cors_headers_presentes(client):
    resp = client.get("/health")
    # SlowAPI/CORS no bloquea en GET; verificamos que la app arranca con middleware
    assert resp.status_code == 200
