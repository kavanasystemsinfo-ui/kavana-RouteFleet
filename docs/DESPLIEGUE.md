# Despliegue — KAVANA RouteFleet

## 1. Backend (Render)
- New → Web Service → repo `kavana-RouteFleet`, rama `main`, Root `server`.
- Build: `npm install` · Start: `node src/index.js`.
- Variables: `OFFICE_PIN` (opcional), `CORS_ORIGINS` (opcional, ya trae defaults).
- **Importante**: el auto-deploy puede quedar fijado a un commit viejo. Tras
  push de cambios al backend, pulsa **Manual Deploy** para aplicar `main` HEAD.

## 2. App repartidor (GitHub Pages)
- Workflow `.github/workflows/deploy.yml` (Source: GitHub Actions).
- Secret repo `VITE_API_BASE=https://routefleet-api.onrender.com`.
- URL: `https://kavanasystemsinfo-ui.github.io/kavana-RouteFleet/`
- Base del build: `/kavana-RouteFleet/` (en `client/vite.config.js`).

## 3. Panel oficinas (GitHub Pages + dominio propio)
- Workflow `.github/workflows/deploy-admin.yml` publica `client-admin/dist`
  en la rama `gh-pages-admin` (orphan).
- En repo → Settings → Pages: selecciona rama **`gh-pages-admin`**,
  carpeta `/ (root)`.
- Custom domain: `routefleet.kavanasystems.com` (activa HTTPS).
- DNS (gestor de `kavanasystems.com`): CNAME `routefleet` →
  `kavanasystemsinfo-ui.github.io`.

## Verificar tras desplegar
```bash
# Backend vivo
curl https://routefleet-api.onrender.com/api/settings
# CORS para panel
curl -s -i https://routefleet-api.onrender.com/api/drivers \
  -H "Origin: https://routefleet.kavanasystems.com" \
  | grep access-control-allow-origin
```
