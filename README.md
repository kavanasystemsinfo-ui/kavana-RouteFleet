# Kavana Logistics v1.0

> **Optimización de Rutas de Reparto de Última Milla con Inteligencia Artificial**
>
> App independiente para repartidores autónomos y flotas locales. Optimiza rutas de entrega con un solo clic: sube una foto del albarán y el sistema calcula la ruta más corta usando OR-Tools y OpenStreetMap. **Zero Data Entry**: el repartidor no teclea nada.

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

### Optimizar ruta con archivo (PDF, imagen)
```bash
curl -X POST http://localhost:8002/api/optimizar-archivo \
  -F "file=@albaran.pdf" \
  -F "depot=Poligono Fuente del Jarro, Paterna"
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

## 📱 Frontend PWA

Interfaz mobile-first con 3 modos de entrada:

| Modo | Descripción |
|------|-------------|
| 📝 **Texto Libre** | Pega el texto de un albarán y la IA extrae las paradas |
| 📸 **Foto / PDF** | Sube una foto o PDF del albarán — extracción automática |
| 📋 **Manual** | Añade paradas una a una con dirección y hora |

### Características
- 🏭 **Depósito global**: se guarda en el navegador (localStorage), no hace falta escribirlo cada vez
- 🗺️ **Google Maps**: botón para buscar la dirección de salida en el mapa
- 📊 **Resultados**: ruta optimizada con km totales, horas estimadas y orden de paradas
- 🎨 **Diseño**: dark theme KAVANA (#FF6B35), responsive, sin dependencias externas

## 📄 Roadmap

- [x] API de optimización con OR-Tools (VRP)
- [x] Geocodificación gratuita con OpenStreetMap
- [x] Extracción de texto con LLM (OpenRouter)
- [x] Procesamiento de imágenes de albaranes
- [x] Parser inteligente multi-formato (PDF, texto, CSV)
- [x] 8 tests unitarios pasando (TDD)
- [x] Frontend PWA con 3 modos de entrada
- [x] Depósito global con persistencia en localStorage
- [x] Google Maps picker para dirección de salida
- [ ] Integración con WhatsApp para enviar ruta al repartidor
- [ ] Exportación de hoja de ruta PDF

---

**Autor:** Jorge Adán Rodríguez · **GitHub:** [kavanasystemsinfo-ui](https://github.com/kavanasystemsinfo-ui)
