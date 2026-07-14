# Backend — KAVANA RouteFleet

Node/Express, store en JSON (sin SQLite). Todo desplegado en Render
(`routefleet-api`). 29 tests con `node --test`.

## Arranque
```bash
cd server
npm install
npm test                # 29 tests verdes
ROUTEFLEET_DB=/tmp/dev.json PORT=5001 node src/index.js
```

## Variables de entorno
| Var | Def. | Uso |
|---|---|---|
| `PORT` | 5001 | Puerto |
| `ROUTEFLEET_DB` | `./routefleet.json` | Ruta del store JSON |
| `OFFICE_PIN` | `0000` | PIN de login de oficina |
| `CORS_ORIGINS` | github.io + routefleet.kavanasystems.com | Orígenes CORS |

## Capa de datos (`src/db.js`)
Store JSON con interfaz agnóstica (`initDb()`, `queries.*`):
- `stops`: `[{id, stop_number, address, status, driver_id, receiver_name, signature, created_at}]`
- `drivers`: `[{id, name, pin, phone, active}]`
- `incidents`: `[{id, stop_id, type, photo_data, notes, created_at}]`
- `settings`: `{cost_per_km, cost_per_hour}`
- `pods`: `{[stopId]: url}`

## Servicios
- `pdfService.js`: genera el POD (PDF) con firma negra sobre blanco.
- `ocrService.js`: procesa imagen de albarán (stub/IA).
- `aiService.js`: optimización de ruta (stub/IA).
