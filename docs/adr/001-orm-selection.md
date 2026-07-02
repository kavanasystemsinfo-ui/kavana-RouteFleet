# ADR 001: Selección de OR-Tools para optimización de rutas VRP-TW

## Status
Aceptado

## Context
Kavana Logistic necesita resolver el problema de Vehicle Routing Problem with Time Windows (VRP-TW) para optimizar rutas de reparto de última milla en PYMEs de distribución local. Las restricciones clave son:
- **Presupuesto limitado:** Las PYMEs objetivo tienen presupuestos ajustados para tecnología
- **Requisito de gratitud:** La solución debe ser gratuita o de muy bajo costo para ser viable en el segmento objetivo
- **Complejidad necesaria:** Debe soportar ventanas de tiempo (horarios límite de entrega) y múltiples vehículos
- **Facilidad de integración:** Debe ser una librería de Python que se pueda integrar directamente en el backend FastAPI sin dependencias externas complejas

## Decision
Utilizar Google OR-Tools (versión 9.15.6755) como librería de optimización de rutas en Python.

## Consequences
### Positivas
- **Gratis para uso comercial:** Licencia Apache 2.0, sin costos de licencia
- **Soporta VRP-TW completo:** Maneja ventanas de tiempo, múltiples vehículos, y capacidades de vehículo
- **Alto rendimiento:** Procesa miles de combinaciones en segundos para instancias típicas de PYMEs (20-50 paradas)
- **Documentación y comunidad:** Amplia documentación oficial y ejemplos disponibles
- **Integración sencilla:** Librería de Python nativa, no requiere servicios externos ni claves de API

### Negativas
- **Curva de aprendizaje:** Requiere entender conceptos de programación de restricciones (mitigado con comentarios en código y pruebas unitarias)
- **Menos visual que alternativas:** No incluye herramientas de visualización incorporadas (mitigado planeando añadir Leaflet.js en fase frontend)
- **Dependencia de CPU:** El cómputo ocurre en el servidor (aceptable para instancias PYMEs <100 paradas)

### Alternativas consideradas
- **GraphHopper / Jsprit:** 
  * Rechazado porque: Aunque poderoso, es excesivamente complejo para nuestras necesidades específicas de VRP-TW en escala PYME; requeriría mayor esfuerzo de integración y tuning.
- **API de Optimización de Rutas de Google Maps:**
  * Rechazado porque: Costo prohibitivo en escala (≈$0.005 por ruta después de 1000 rutas/mes), requiere conectividad constante a internet (riesgo en zonas con cobertura irregular), y pierde control sobre el algoritmo de optimización.
- **Implementación propia de algoritmo genético:**
  * Rechazado porque: Alto riesgo de errores en implementación, tiempo de desarrollo significativo para lograr rendimiento competitivo, y menor confiabilidad que una librería probada como OR-Tools.

## Notas Adicionales
Esta decisión alinea directamente con nuestro principio YAGNI: implementamos solo lo necesario para resolver el problema de optimización de rutas en el contexto de PYMEs de reparto local, evitando sobreingeniería con soluciones empresariales costosas o complejas innecesarias para nuestra etapa inicial.