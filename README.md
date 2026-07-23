# RouteFleet — Gestión de Repartos con Firma Digital (POD)

[![Tests](https://img.shields.io/badge/tests-40%20passing-brightgreen)](docs/METRICS.md)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://react.dev)
[![PWA](https://img.shields.io/badge/PWA-Offline‑First-5A0FC8)](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
[![Node](https://img.shields.io/badge/Node-20-339933?logo=nodedotjs)](https://nodejs.org)
[![Render](https://img.shields.io/badge/Backend-Render-46E3B7?logo=render)](https://routefleet-api.onrender.com)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

---

## ⚡ 30 Segundos

**Problema:** Las empresas de reparto pierden tiempo y dinero cuando los albaranes se extravían, las firmas de Recepción (POD) no se digitalizan y las oficinas no saben en tiempo real qué repartos están completados.

**Solución:** Plataforma PWA donde el **repartidor** escanea albaranes, geolocaliza entregas y captura firma del cliente en su móvil (offline-first), y la **oficina** lo controla todo desde un panel con KPIs, histórico y trazabilidad.

**Stack:** React PWA · Node + Express · Render · GitHub Pages · OCR (tesseract) · Firma digital canvas

---

## 🏗️ Arquitectura

```
REPARTIDOR (PWA móvil)            OFICINA (Torre de Control)
┌──────────────────────┐          ┌────────────────────────┐
│ Escanea albarán      │          │ KPIs por repartidor    │
│ Firma cliente (POD)  │          │ Histórico de entregas  │
│ Geolocalización      │          │ Ver firmas (POD)       │
│ Offline-first        │          │ Panel administrativo   │
└──────────┬───────────┘          └───────────┬────────────┘
           │                                  │
           └──────────────┬───────────────────┘
                          ▼
              ┌──────────────────────┐
              │  API REST (Express)  │
              │  + JWT Auth          │
              │  + Almacenamiento    │
              │    JSON + Firmas PNG │
              └──────────┬───────────┘
                         │
              ┌──────────▼───────────┐
              │  Render.com          │
              │  + GitHub Pages      │
              │  (frontends)         │
              └──────────────────────┘
```

## 🧠 Decisiones

| Decisión | Alternativas | Elegida | Por qué |
|----------|-------------|---------|---------|
| Frontend repartidor | App nativa | **PWA** | Sin store, actualización instantánea, offline |
| Almacenamiento | PostgreSQL, MongoDB | **JSON + fs** | Suficiente para el volumen, sin dependencias |
| Firmas (POD) | librería externa | **Canvas nativo** | Sin coste, embedido en PNG de albarán |
| OCR albaranes | Servicio cloud | **Tesseract.js** | Gratuito, offline, privacidad de datos |
| Despliegue | VPS, Docker | **Render + GitHub Pages** | Sin mantenimiento de infraestructura |

[📘 ADR-001 →](docs/adr/001-pwa-vs-native.md)

## 📊 Estado

| Scope | Estado |
|-------|--------|
| PWA repartidor (login, escaneo, firma, geoloc) | ✅ |
| Panel oficina (KPIs, histórico, firmas) | ✅ |
| Firma digital (POD) en PNG | ✅ |
| OCR de albaranes (Tesseract.js) | ✅ |
| Offline-first (Service Worker) | ✅ |
| API REST (Express + JWT) | ✅ |
| Tests | 🚧 Pendiente |
| Clientes reales | ⚠️ Sin implantación real aún |

## 📚 Documentación

| Para qué | Dónde |
|----------|-------|
| Decisiones arquitectónicas | [`docs/adr/`](docs/adr/) |
| Documentación técnica | [`docs/technical/`](docs/technical/) |
| Evolución del proyecto | [`docs/HISTORY.md`](docs/HISTORY.md) |
| Métricas de código | [`docs/METRICS.md`](docs/METRICS.md) |

## 🚀 Cómo ejecutar

```bash
# Backend
cd server && npm install && npm start

# App repartidor
cd client && npm install && npm run dev

# Panel oficina
cd client-admin && npm install && npm run dev
```

**Live demo:** [`https://routefleet.kavanasystems.com`](https://routefleet.kavanasystems.com)  
**PIN repartidor demo:** `5855`

---

*Proyecto diseñado con criterio arquitectónico propio, implementado con asistencia de IA.*  
*Parte del ecosistema [Kavana Systems](https://github.com/kavanasystemsinfo-ui).*
