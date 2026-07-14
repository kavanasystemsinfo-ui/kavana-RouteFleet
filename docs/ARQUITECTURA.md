# Arquitectura — KAVANA RouteFleet

## Principio rector
El VPS (167.233.97.71) es **solo entorno de desarrollo y documentación**. Los
proyectos terminados viven fuera del VPS, igual que CleanStock:
- Backend → **Render** (servicio `routefleet-api`, Free).
- Frontends → **GitHub Pages** (sin servidor propio, HTTPS automático).

## Componentes

```
┌─────────────────────┐         ┌──────────────────────────┐
│ App Repartidor      │  HTTPS  │ Backend API (Render)     │
│ (GitHub Pages)      │ ──────▶ │ Express + store JSON     │
│ React PWA           │ ◀────── │ /api/* , /pods/*          │
└─────────────────────┘         └──────────────────────────┘
                                        ▲
┌─────────────────────┐                 │
│ Panel Oficinas      │  HTTPS          │
│ Torre de Control    │ ────────────────┘
│ (GitHub Pages       │
│  gh-pages-admin)    │
└─────────────────────┘
```

## Datos
- Store JSON en disco (`routefleet.json` en el server de Render). Sin SQLite
  para evitar compilación nativa en Render Free. Listo para migrar a Postgres.
- PODs: PDFs generados con pdfkit en `./pods`. En Render son efímeros tras
  spin-down; el endpoint `GET /api/stops/:id/pod` los regenera al vuelo si la
  parada tiene firma guardada.

## Identidades
- **Repartidor**: se identifica con un PIN (4 dígitos) que se guarda en
  `localStorage` del móvil. Cada parada se etiqueta con `driver_id`.
- **Oficina**: login con PIN único de empresa (`OFFICE_PIN`, def. `0000`).
  MVP sin usuarios/roles (YAGNI).

## Flujo
1. Oficina da de alta repartidores (PIN) en el panel.
2. Repartidor abre la app, introduce su PIN (se guarda en el móvil).
3. Repartidor escanea albarán → parada creada con `driver_id`.
4. Repartidor entrega → POD generado en el navegador (jsPDF) + subido al backend.
5. Oficina ve en el panel: Dashboard (KPIs), Repartos (filtros), Firmas (galería).
