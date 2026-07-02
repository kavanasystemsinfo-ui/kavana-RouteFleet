# Guía de Contribución para Kavana Logistic

## Filosofía de Desarrollo
Este proyecto sigue principios rigurosos de **TDD (Test-Driven Development)** y **YAGNI (You Aren't Gonna Need It)** para mantener alta calidad, evitar sobreingeniería y asegurar que cada línea de código tenga un propósito claro de negocio. Cada cambio debe ser justificable en términos de valor entregado al usuario final o reducción de riesgo técnico.

## Antes de Escribir Código
Sigue estrictamente el ciclo TDD para asegurar calidad desde el inicio:

1. **Escribe una prueba que falle (Fase RED)**
   - Crea una prueba unitaria que defina el comportamiento esperado de una función o característica nueva
   - La prueba debe fallar inicialmente porque la funcionalidad aún no existe
   - *Ejemplo:* Antes de implementar `haversine()`, escribir una prueba que verifique que la distancia entre Nueva York y Los Ángeles es aproximadamente 3940 km

2. **Ejecuta las pruebas para confirmar el fallo**
   - Ejecuta `pytest` y verifica que la nueva prueba falle (y que las existentes aún pasen)
   - Esto confirma que estás testeando lo correcto y que tu entorno está configurado adecuadamente

3. **Escribe el mínimo código necesario para hacer que la prueba pase (Fase Verde)**
   - Implementa solo lo necesario para satisfacer la prueba - nada más
   - Enfócate en hacer que la prueba pase, no en escribir código "perfecto" o "genérico"
   - *Ejemplo:* Implementar la fórmula de Haversine básica para pasar la prueba de distancia NYC-LA

4. **Ejecuta las pruebas para confirmar que pasan (Fase Verde)**
   - Verifica que tu nueva prueba pase y que no hayas roto funcionalidad existente
   - Si falla, vuelve al paso 3 hasta que pase

5. **Refactoriza solo si mejora la legibilidad o elimina duplicación (Fase de Refactor)**
   - Mejora la estructura del código sin cambiar su comportamiento
   - Solo refactoriza si:
     - El código es difícil de leer o entender
     - Hay código duplicado que se puede extraer en una función reutilizable
     - Puedes mejorar nombres de variables o funciones para mayor claridad
   - Nunca refactorices solo por "hacerlo mejor" - debe haber un beneficio claro de mantenibilidad
   - Después de refactorizar, ejecuta las pruebas nuevamente para asegurarte de que todo sigue pasando

## Commits Significativos
Cada commit debe responder claramente a la pregunta: **"¿Qué problema específico resuelve este cambio?"**

### ✅ Buenos Ejemplos de Mensajes de Commit (basados en tu trabajo real):
- `feat: agregar validación de coordenadas en geocodificación para prevenir errores 422 en direcciones inválidas`
- `refactor: separar lógica de cálculo de distancia Haversine en función pura para facilitar testing unitario`
- `test: agregar casos frontera para direcciones no encontradas y errores de red en geocodificación`
- `docs: actualizar README con ejemplo real de uso usando coordenadas de NYC`
- `chore: instalar dependencias faltantes (httpx, geopy) y actualizar requirements.txt`
- `fix: corregir advertencia de Pydantic en Field() args (ejemplo → json_schema_extra)`

### ❌ Malos Ejemplos de Mensajes de Commit (Evítalos):
- `fix` - No especifica qué se arregló
- `update` - No indica qué se actualizó ni por qué
- `trabajo en geocodificación` - No especifica qué aspecto se trabajó ni qué se logró
- `actualizar código` - Muy genérico, no comunica valor ni propósito
- `wip` - No informa sobre progreso ni qué se completó

## Antes de Hacer Push
Antes de enviar tus cambios al repositorio remoto, verifica:

1. **Ejecuta el suite completo de pruebas con cobertura:**
   ```bash
   pytest --cov=.
   ```
2. **Verifica que la cobertura no baje más del 2% desde tu último commit significativo**
   - Si la cobertura disminuye significativamente, investiga por qué y agrega pruebas faltantes
   - La cobertura debe mantenerse o mejorar con cada cambio significativo
3. **Revisa que todos tus commits tengan mensajes significativos** (según la guía arriba)
4. **Asegúrate de que tu rama esté actualizada con la rama principal** (si aplica):
   ```bash
   git fetch origin
   git rebase origin/main
   ```
5. **Ejecuta una última prueba de smoke en el endpoint principal:**
   ```bash
   curl -s http://127.0.0.1:8000/health | grep '"status":"healthy"'
   ```

## ¿Por Qué Esto Importa?
Este enfoque no es solo sobre seguir reglas - es sobre demostrar disciplina de ingeniería que los equipos técnicos de élite valoran:

- **Para Consultoras IT:** Muestras que entiendes que el software resuelve problemas de negocio, y que tu proceso minimiza riesgos y maximiza el valor entregado al cliente
- **Para Startups:** Demuestras que puedes moverte rápido sin acumular deuda técnica que te ralentice más adelante
- **Para Ti Mesmo:** Crea un historial de trabajo claro que muestre tu progreso y pensamiento, facilitando revisiones de código y colaboración futura

Recuerda: El objetivo no es ser perfecto, sino ser intencional y transparente en tu proceso de desarrollo. Cada commit, cada prueba, cada decisión documentada es una oportunidad para mostrar cómo piensas como ingeniero de software profesional.