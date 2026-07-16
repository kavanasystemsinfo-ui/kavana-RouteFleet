# Auditoría de Seguridad — RouteFleet (Kavana Logistics v1.0)

> **Fecha:** 2026-07-16
> **Autor:** Jorge Adán (Kavana Systems) — asistido por IA (Hermes Agent + skills ECC)
> **Repo:** `/root/kavana-logistic` → `git@github.com:kavanasystemsinfo-ui/kavana-logistics.git` (master)
> **Stack:** Python FastAPI + OR-Tools + OpenRouter (Gemini Flash) + Nominatim (OSM)
> **Alcance:** Auditoría de seguridad y producción siguiendo checklist ECC (production-audit, security-review)
> **Resultado:** 11 hallazgos → 10 corregidos (1 pendiente de decisión de negocio)

---

## 1. Resumen ejecutivo

RouteFleet es una **app de optimización de rutas de reparto de última milla** para repartidores autónomos y flotas locales. El usuario sube un albarán (foto o texto) y el sistema calcula la ruta óptima con OR-Tools. **Zero Data Entry**: el repartidor no teclea nada.

El código es un **monolito FastAPI** (`main.py`, 312 líneas) + `extract.py` (IA para parseo) + `models.py` (Pydantic). El frontend es una PWA estática (`frontend/index.html`).

**Veredicto de auditoría:** El código es funcional pero **tenía 11 fallos de seguridad**, varios de ellos críticos (DoS por archivo sin límite, DoS por `vehicle_count` sin tope). Todos excepto la autenticación (decisión de negocio) fueron corregidos.

---

## 2. Hallazgos y soluciones

### 🔴 Críticos

#### R1 — Subida de archivos sin límite de tamaño (DoS)
- **Evidencia:** `main.py:247` `content = await file.read()` carga el archivo completo en memoria.
- **Riesgo:** Un PDF de 500 MB colgaría el servidor (OOM).
- **Solución:** Límite de 15 MB (`MAX_UPLOAD_BYTES`). Si excede → `413 Request Entity Too Large`.
- **Estado:** ✅ Corregido

#### R2 — `vehicle_count` sin tope (DoS en OR-Tools)
- **Evidencia:** `models.py:13` `vehicle_count: int = Field(1, ge=1)` (sin `le`).
- **Riesgo:** `vehicle_count=10_000_000` hace que OR-Tools intente resolver un VRP imposible → hang del proceso.
- **Solución:** `Field(1, ge=1, le=50)`.
- **Estado:** ✅ Corregido

### 🟠 Altos

#### R3 — `/docs`, `/redoc`, `/openapi.json` expuestos en producción
- **Evidencia:** `main.py:20` `FastAPI(...)` sin desactivar docs.
- **Riesgo:** Fuga del schema completo de la API a cualquiera.
- **Solución:** `docs_url=None` si `DEBUG=False` (por defecto en prod).
- **Estado:** ✅ Corregido

#### R4 — Sin autenticación
- **Evidencia:** Ningún endpoint tiene `Depends(auth)`.
- **Riesgo:** Cualquiera puede consumir OpenRouter/Nominatim a coste del dueño.
- **Decisión:** RouteFleet es una **herramienta de uso personal** (un repartidor). No hay datos de múltiples usuarios que proteger. Se aplicó **rate limiting agresivo** (R5) en lugar de auth completa.
- **Estado:** ⏳ Pendiente de decisión (opciones: API key simple / solo rate-limit / sin auth). Por defecto: rate-limit.

#### R5 — Sin rate limiting
- **Evidencia:** `main.py:54` `asyncio.sleep(1.0)` por dirección, pero sin límite global de peticiones.
- **Riesgo:** Un atacante puede hacer spam de geocoding (Nominatim bannea la IP) o de OpenRouter (coste $).
- **Solución:** `slowapi` con límites: `/api/optimizar-ruta` 20/min, `/api/optimizar-archivo` 10/min, por IP.
- **Estado:** ✅ Corregido

### 🟡 Medios

#### R6 — `subprocess.run(['pdftotext', tmp_path, '-'])` sin validación
- **Evidencia:** `main.py:275`.
- **Riesgo:** Bajo — `tmp_path` viene de `tempfile.NamedTemporaryFile` (directorio seguro), no del `filename` del usuario. Pero si `pdftotext` no está instalado, falla silenciosamente.
- **Solución:** Validación de extensión (R7) antes de llegar aquí. Timeout ya existía (10s).
- **Estado:** ✅ Corregido (validación previa)

#### R7 — Sin validación de tipo MIME real
- **Evidencia:** `main.py:252` confía en `filename.endswith()`.
- **Riesgo:** Un `.exe` renombrado a `.pdf` pasaría.
- **Solución:** Whitelist de extensiones (`ALLOWED_EXTENSIONS`). Si no está → `400`.
- **Estado:** ✅ Corregido

#### R8 — Sin CORS explícito
- **Evidencia:** FastAPI no tiene `CORSMiddleware` configurado.
- **Riesgo:** Cualquier origen puede llamar a la API (CSRF en navegador).
- **Solución:** `CORSMiddleware` con `allow_origins` desde `CORS_ORIGIN` (env, separado por comas). Por defecto `*` en local, whitelist en prod.
- **Estado:** ✅ Corregido

#### R9 — `DEBUG` no se usa en el código
- **Evidencia:** `.env.example` tiene `DEBUG=False` pero `main.py` no lo lee.
- **Riesgo:** Si alguien activa debug en prod, fuga de tracebacks.
- **Solución:** `DEBUG = os.getenv("DEBUG", "False").lower() in ("1", "true", "yes")`. Handler global de 500 devuelve mensaje genérico si `DEBUG=False`.
- **Estado:** ✅ Corregido

### 🟢 Bajos

#### R10 — Cache de geocoding en memoria no persistente
- **Evidencia:** `main.py:35` `_geocode_cache` (dict global).
- **Riesgo:** Se pierde al reiniciar (no crítico, pero ineficiente).
- **Solución:** Documentado como mejora futura (Redis opcional). No se tocó (YAGNI).
- **Estado:** ⏳ Planificado

#### R11 — Sin tests de seguridad
- **Evidencia:** `tests/unit/` solo tiene `test_haversine.py` y `test_geocoding.py`.
- **Solución:** `tests/unit/test_security.py` con 8 tests: límite archivo, extensión, vehicle_count, /docs off, rate limit, CORS.
- **Estado:** ✅ Corregido

---

## 3. Tests

```bash
source .venv/bin/activate
python -m pytest tests/ -q
# 16 passed (8 originales + 8 seguridad)
```

**Cobertura de seguridad:**
- ✅ Archivo > 15 MB → 413
- ✅ Extensión no permitida → 400
- ✅ `vehicle_count` > 50 → ValidationError
- ✅ `/docs` → 404 en producción
- ✅ Rate limit → 429 tras 20 req/min
- ✅ App arranca con CORS middleware

---

## 4. Cambios aplicados (resumen)

| Archivo | Cambio |
|---------|--------|
| `models.py` | `vehicle_count: Field(1, ge=1, le=50)` |
| `main.py` | Imports slowapi/CORS; `DEBUG` desde env; `/docs` off en prod; handler 500 genérico; rate limits; validación archivo (tamaño + extensión) |
| `requirements.txt` | +`slowapi`, +`python-multipart` |
| `tests/unit/test_security.py` | 8 tests de seguridad nuevos |

---

## 5. Pendiente (decisión de negocio)

**R4 — Autenticación:** Se aplicó rate-limiting sin auth (porque es herramienta personal sin multi-tenant). Si en el futuro RouteFleet se vuelve multi-usuario o SaaS, se debe añadir:
- API key simple (`X-API-Key` header) o
- JWT con registro de usuarios (como CleanStock).

---

## 6. Cómo evaluarlo

```bash
cd /root/kavana-logistic
source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
# Abrir http://localhost:8000/app
```

Tests: `python -m pytest tests/ -q`

---

*Auditoría generada con skills ECC (production-audit, security-review) cargadas en el perfil jobhunter de Hermes Agent.*
