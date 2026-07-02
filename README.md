# Kavana Logistic

Módulo para optimización de rutas de reparto dentro del ecosistema Kavana.

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecución

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Endpoints

- `GET /` - Mensaje de bienvenida
- `GET /health` - Health check
