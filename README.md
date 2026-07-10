# Kavana Logistic v1.0

> **Optimización de Rutas de Reparto con Inteligencia Artificial**
>
> Kavana Logistic es un módulo autónomo diseñado para resolver la ineficiencia operativa en PYMEs que gestionan flotas locales de reparto. Filosofía **"Zero Data Entry"**: el operario sube una foto de un albarán y la IA genera la ruta óptima en segundos.

## 📋 Estado del Proyecto

| Componente | Estado | Detalle |
|-----------|--------|---------|
| 🧪 **Tests** | ✅ 8/8 | TDD con pytest |
| ⚡ **API** | ✅ Funcional | FastAPI en puerto 8002 |
| 🗺️ **Geocodificación** | ✅ | OpenStreetMap (Nominatim) |
| 📐 **Optimización** | ✅ | Google OR-Tools (VRP-TW) |
| 🧠 **Extracción IA** | ✅ | OpenRouter LLM (texto/imagen) |
| 📱 **Frontend PWA** | 📁 Código base | `frontend/index.html` |

## 🏗️ Arquitectura

```
┌──────────────────────────────────────────────────────────────┐
│                     VPS Hetzner                               │
│                                                               │
│  ┌──────────────────┐    ┌──────────────────────────────┐    │
│  │   Frontend PWA    │    │   FastAPI Backend            │    │
│  │   HTML/JS         │───→│   Puerto 8002                │    │
│  │   Mobile-First    │    │                              │    │
│  └──────────────────┘    │  ┌────────────────────────┐  │    │
│                          │  │ POST /api/optimizar-ruta│  │    │
│                          │  │ POST /api/optimizar-    │  │    │
│                          │  │        archivo          │  │    │
│                          │  └────────────────────────┘  │    │
│                          └──────────┬───────────────────┘    │
│                                     │                        │
│              ┌──────────────────────┼──────────────────┐     │
│              │         ↓            ↓                  │     │
│              │  ┌──────────┐  ┌──────────────┐        │     │
│              │  │ LLM Text │  │  OR-Tools     │        │     │
│              │  │ Extractor│  │  Route Solver │        │     │
│              │  └──────────┘  └──────────────┘        │     │
│              │         ↓            ↓                  │     │
│              │  ┌──────────────────────────┐          │     │
│              │  │  Nominatim Geocoder       │          │     │
│              │  │  (OpenStreetMap — FREE)   │          │     │
│              │  └──────────────────────────┘          │     │
│              └────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────┘
```

## 🧠 Propuesta de Valor

| Problema | Solución |
|----------|----------|
| 📋 **Entrada manual compleja** | Sube una foto del albarán → la IA extrae direcciones y horarios |
| ⛽ **Rutas ineficientes** | OR-Tools resuelve VRP con ventanas de tiempo en milisegundos |
| 💰 **Coste de APIs de mapas** | OpenStreetMap gratuito, sin límites |
| 📱 **Formación del operario** | PWA mobile-first, sin instalar nada |

## 🛠️ Stack Técnico

| Componente | Tecnología | Justificación |
|------------|-----------|---------------|
| **Backend** | FastAPI (Python 3.11) | Alto rendimiento, async nativo |
| **Optimización** | Google OR-Tools | Librería gratuita para VRP-TW a nivel producción |
| **Geocodificación** | Nominatim (OSM) | Open source, sin límites de API |
| **Extracción IA** | OpenRouter (Gemini Flash) | Modelo gratuito para parsing de texto |
| **Validación** | Pydantic v2 | Tipado fuerte y validación automática |
| **Frontend** | HTML5 + JS vanilla | PWA ligera, sin dependencias de framework |
| **Testing** | Pytest + pytest-asyncio | 8 tests unitarios y de integración |

## 🚀 Uso de la API

### Optimizar ruta con texto libre
```bash
curl -X POST http://localhost:8002/api/optimizar-ruta \
  -H "Content-Type: application/json" \
  -d '{
    "document_text": "Cliente A, Calle Mayor 1, 10:00\nCliente B, Av. Puerto 20, 12:00",
    "depot": "Paterna, Valencia",
    "vehicle_count": 1
  }'
```

### Optimizar ruta con lista estructurada
```bash
curl -X POST http://localhost:8002/api/optimizar-ruta \
  -H "Content-Type: application/json" \
  -d '{
    "paradas": [
      {"cliente":"Bar Pepe","direccion":"Calle Colon 5, Valencia","horario_limite":"10:00"},
      {"cliente":"Oficina","direccion":"Av. Blasco Ibanez 20, Valencia","horario_limite":"12:00"}
    ],
    "depot": "Poligono Fuente del Jarro, Paterna",
    "vehicle_count": 2
  }'
```

### Respuesta
```json
{
  "orden_optimizado": [0, 1],
  "distancia_total_km": 15.3,
  "tiempo_total_horas": 0.4,
  "detalles": [
    {"cliente": "Bar Pepe", "direccion": "Calle Colon 5, Valencia", "hora_llegada_estimada": "09:45"},
    {"cliente": "Oficina", "direccion": "Av. Blasco Ibanez 20, Valencia", "hora_llegada_estimada": "10:10"}
  ]
}
```

## 📄 Roadmap

- [x] API de optimización con OR-Tools
- [x] Geocodificación gratuita con OpenStreetMap
- [x] Extracción de texto con LLM (OpenRouter)
- [x] Procesamiento de imágenes de albaranes
- [x] 8 tests unitarios pasando (TDD)
- [ ] Frontend PWA funcional completo
- [ ] Dockerización con restart automático
- [ ] Integración con WhatsApp para notificaciones de ruta
- [ ] Exportación de hoja de ruta PDF para el repartidor
- [ ] Dashboard de histórico de rutas y estadísticas

---

**Autor:** Jorge Adán Rodríguez · **GitHub:** [kavanasystemsinfo-ui](https://github.com/kavanasystemsinfo-ui)
