# App del Repartidor — KAVANA RouteFleet

React PWA (carpeta `client/`). Desplegada en GitHub Pages en
`/kavana-RouteFleet/`. Estética oscura industrial, pensada para móvil.

## Pantalla de identificación (PIN)
Al abrir la app, si no hay PIN guardado, pide el PIN del repartidor.
Se valida contra `GET /api/drivers` y se guarda en `localStorage`
(`routefleet_driver_id`, `routefleet_driver_name`). No se pide más hasta
cambiar de dispositivo o pulsar "cambiar".

## Funciones
- **Carga**: escáner de albarán (cámara) → `POST /api/ocr` (IA) → crea parada
  con `driver_id` vía `POST /api/ocr_manual`.
- **Mapa**: vista de la parada activa (Google Maps embed).
- **Entregar**: firma del cliente en canvas (blanco, trazo negro) →
  `PATCH /stops/:id` con firma → genera POD en el navegador (jsPDF) y
  descarga garantizada (`DESCARGAR POD`). También sube la firma al backend.
- **Incidencia**: foto + nota → `POST /stops/:id/incident`.

## Variables
- `VITE_API_BASE` (build-time) → `https://routefleet-api.onrender.com`
  Sin slash final; el cliente añade `/api`.

## Build
```bash
cd client && npm install && npm run build   # → dist/
```
