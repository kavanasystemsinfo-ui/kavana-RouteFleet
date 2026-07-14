# API REST — KAVANA RouteFleet

Base: `https://routefleet-api.onrender.com/api`

## Paradas (stops)
- `GET /stops` → lista. Query: `?driver_id=1&status=delivered&from=2026-07-01&to=2026-07-31`
- `POST /ocr_manual` → crea parada. Body: `{stop_number, address, driver_id}`
- `PATCH /stops/:id` → actualiza. Body: `{status, signature, receiverName, driver_id}`.
  Si `status=delivered` y `signature`, genera POD y devuelve `{success, pod_url}`.
- `DELETE /stops/:id` · `DELETE /stops` (borra todas)
- `POST /stops/:id/incident` → Body `{type, photo_data, notes}` (pone status=incident)
- `GET /stops/:id/pod` → `{pod_url}` (regenera si hace falta)

## Repartidores (drivers)
- `GET /drivers` → lista
- `POST /drivers` → Body `{name, pin, phone}` (404 si falta name/pin)
- `PATCH /drivers/:id` → Body `{active: bool}`

## Oficina
- `POST /office/login` → Body `{pin}`. 200 si coincide con `OFFICE_PIN`, 401 si no.

## Config / métricas
- `GET /settings` · `PUT /settings` (`{cost_per_km, cost_per_hour}`)
- `GET /dashboard-data` → `{metrics, stops (con pod_url), settings}`

## PODs (estáticos)
- `GET /pods/<file>.pdf` → descarga del PDF
