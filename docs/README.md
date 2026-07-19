# KAVANA RouteFleet — Documentación

Producto comercial B2B para empresas de reparto (reparto general, no metalúrgico).
App del repartidor (PWA) + panel de oficinas web ("Torre de Control").

## Accesos
| Qué | URL |
|---|---|
| Panel oficinas (Torre de Control) | https://routefleet.kavanasystems.com/ |
| App del repartidor (PWA) | https://routefleet.kavanasystems.com/app |
| Página de descarga PWA | https://routefleet.kavanasystems.com/download |
| Backend API | https://routefleet-api.onrender.com |

PIN oficina por defecto: `0000` (configurable vía `OFFICE_PIN`). PIN repartidor demo: `5855`.

## Documentación
- [ARQUITECTURA.md](ARQUITECTURA.md) — diagrama y componentes.
- [DESPLIEGUE.md](DESPLIEGUE.md) — backend (Render), frontends (GitHub Pages),
  DNS, **persistencia de datos (CRÍTICO)**.
- [BACKEND.md](BACKEND.md) — API Node/Express, auth JWT, store JSON.
- [API.md](API.md) — endpoints.
- [PANEL_OFICINAS.md](PANEL_OFICINAS.md) — Torre de Control.
- [APP_REPARTIDOR.md](APP_REPARTIDOR.md) — app PWA del repartidor.
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — **casos reales y soluciones**.

## Estado conocido (15/07/2026)
- ✅ Panel, PWA y página de descarga funcionando en producción.
- ✅ Login oficina (`0000`) y repartidor demo (`5855`) verificados contra backend.
- ⚠️ **BD efímera en Render free**: los repartidores/paradas se pierden en cada
  reinicio del backend. Ver DESPLIEGUE.md §1b. Migrar a Render Disk/Postgres
  antes de tener clientes reales.
- ✅ Estrategia de distribución: PWA ("añadir a inicio") como canal principal
  (se actualiza sola, funciona offline, sin pasar por Google Play).

## Desarrollo
Repositorio: `kavanasystemsinfo-ui/kavana-RouteFleet`. El VPS solo para
desarrollo/documentación; todo lo productivo fuera del VPS (Render + GitHub Pages).
YAGNI + TDD. En seguridad/auth no se escatima.
