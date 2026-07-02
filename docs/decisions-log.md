# Registro de Decisiones y Lecciones Aprendidas

## Formato de Entrada
### [YYYY-MM-DD] - [Tema de la Decisión]
- **Situación:** [Qué estaba pasando]
- **Decisión tomada:** [Qué decidiste hacer]
- **Resultado:** [Qué pasó como resultado]
- **Lección aprendida:** [Qué mejorarías la próxima vez]
- **Próximos pasos:** [Qué harás basado en esta lección]

## Entradas

### [2026-07-02] - Selección de enfoque para pruebas unitarias
- **Situación:** Necesitábamos validar funciones críticas (haversine, geocodificación) antes de construir la lógica de optimización para asegurar que los componentes básicos funcionaran correctamente.
- **Decisión tomada:** Implementar TDD estricto escribiendo pruebas RED primero (que fallan), luego código para hacerlas GREEN, y finalmente refactorizar si es necesario.
- **Resultado:** Las pruebas de haversine y geocodificación pasaron en primer intento. Detectamos tempranamente un issue con el manejo de pruebas asíncronas en geocodificación, lo que nos llevó a agregar pytest-asyncio y mejorar nuestros mocks.
- **Lección aprendida:** Invertir tiempo en escribir pruebas claras y aisladas al inicio ahorra tiempo significativo de depuración posterior y hace el código más confiable desde el comienzo.
- **Próximos pasos:** Aplicar este mismo patrón de TDD a la lógica de OR-Tools y los endpoints de la API a medida que los desarrollamos.

### [2026-07-02] - Elección de la biblioteca de geocodificación
- **Situación:** Necesitábamos convertir direcciones de texto a coordenadas (lat, lon) para el motor de optimización, pero queríamos evitar costos y dependencias de APIs externas pagadas desde el inicio para mantener el MVP accesible para PYMEs.
- **Decisión tomada:** Usar Nominatim de OpenStreetMap mediante la librería geopy para geocodificación gratuita, implementando manejo de errores y timeouts para direcciones no encontradas.
- **Resultado:** La geocodificación funciona correctamente para direcciones válidas y devuelve None adecuadamente para direcciones inválidas, permitiendo que el sistema maneje estos casos de error de forma graceful en el endpoint de la API.
- **Lección aprendida:** Aunque Nominatim tiene límites de rate y precisión ligeramente menor que servicios pagados, es suficientemente preciso para nuestras necesidades iniciales en zonas urbanas y suburbanas, y su gratuito lo hace ideal para el segmento PYME objetivo.
- **Próximos pasos:** Implementar un sistema simple de caché para direcciones frecuentemente consultadas para reducir llamadas repetidas a Nominatim y mejorar el rendimiento.

### [2026-07-02] - Enfoque para documentación del proyecto
- **Situación:** Al revisar el proyecto, notamos que aunque el código funcionaba bien, faltaba documentación que conectara las decisiones técnicas con el valor de negocio para demostrar rigurosidad ingenieril a posibles empleadores o consultoras.
- **Decisión tomada:** Crear documentación estructurada que incluyera un README enfocado en impacto de negocio, ADRs para decisiones técnicas significativas, y un registro de decisiones para mostrar aprendizaje y adaptación.
- **Resultado:** El README ahora comunica claramente el problema de negocio (costos de reparto en PYMEs), la solución (Zero Data Entry con IA futura), y incluye métricas de prueba reales. Se creó el primer ADR documentando la elección de OR-Tools.
- **Lección aprendida:** La documentación que explica el POR QUÉ detrás de las decisiones técnicas es tan importante como el código mismo para demostrar madurez ingenieril a audiencias técnicas como consultoras IT o CTOs de startups.
- **Próximos pasos:** Continuar actualizando este registro después de cada característica significativa completada, y usar el formato ADR para futuras decisiones técnicas como la selección de enfoque para el frontend PWA o la estrategia de integración de LLM en Fase 2.