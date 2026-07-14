# Despliegue — KAVANA RouteFleet

## Arquitectura de despliegue (todo fuera del VPS)
| Componente | Donde vive | URL |
|---|---|---|
| Backend API (Node/Express, store JSON) | Render | https://routefleet-api.onrender.com |
| Panel oficinas "Torre de Control" (React) | GitHub Pages (`gh-pages-admin`) | https://routefleet.kavanasystems.com |
| App del repartidor (React PWA) | GitHub Pages (`gh-pages-admin`/`/app`) | https://routefleet.kavanasystems.com/app |

El VPS solo se usa para desarrollo/documentación.

## 1. Backend (Render)
- New → Web Service → repo `kavana-RouteFleet`, rama `main`, Root `server`.
- Build: `npm install` · Start: `node src/index.js`.
- Variables obligatorias: `JWT_SECRET` (cadena ≥32 chars aleatoria),
  `OFFICE_PIN` (PIN oficina, def. `0000`), `CORS_ORIGINS`
  (def. github.io + routefleet.kavanasystems.com).
- **Nota**: el auto-deploy puede quedar fijado a un commit viejo. Tras push de
  cambios al backend, pulsa **Manual Deploy** para aplicar `main` HEAD.

## 2. Frontends combinados (GitHub Pages + dominio propio)
- **Un solo workflow** `.github/workflows/deploy-combined.yml` builda los dos
  frontends y publica en la rama `gh-pages-admin`:
  - Panel de oficinas en la **raíz** (`/`).
  - App del repartidor en **`/app`** (`client/` con `base: '/app/'`).
  - Se incluye `.nojekyll`.
- En repo → **Settings → Pages**:
  - Source: **Deploy from a branch**
  - Branch: **`gh-pages-admin`**, carpeta `/ (root)`
  - Custom domain: **`routefleet.kavanasystems.com`** → Save → **Enforce HTTPS**
- **Si el dominio sirve contenido viejo tras un deploy**: quita (Remove) el
  custom domain, guarda, espera 1 min y vuelve a ponerlo + Enforce HTTPS. Esto
  reasocia el dominio al sitio de `gh-pages-admin`.

## 3. DNS (gestor del dominio `kavanasystems.com`)
- CNAME `routefleet` → `kavanasystemsinfo-ui.github.io`.

## Verificar tras desplegar
```bash
# Backend vivo
curl https://routefleet-api.onrender.com/api/settings
# Auth: sin token debe dar 401
curl -o /dev/null -w "%{http_code}\n" https://routefleet-api.onrender.com/api/drivers
# CORS para panel
curl -s -i https://routefleet-api.onrender.com/api/drivers \
  -H "Origin: https://routefleet.kavanasystems.com" \
  | grep access-control-allow-origin
```
