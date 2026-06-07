# EnPapel — noticias-digest

Digest personal de noticias RSS en español. Flask + Claude AI. Desplegado en Render.
Repo: https://github.com/Dipenaa/noticias-digest | Prod: https://noticias-digest.onrender.com

---

## Estado actual del proyecto

> **Actualizar esta sección antes de cada handoff entre agentes.**

**Última sesión:** 2026-06-07 — Rediseño visual EnPapel (líneas SVG animadas estilo periódico)

**Qué está hecho:**
- CSS en 4 ficheros: `static/css/reset.css`, `layout.css`, `components.css`, `animations.css`
- Líneas SVG generativas en `static/js/lines.js` — se dibujan al cargar cada pestaña y tienen ciclo de vida (desaparecen y reaparecen lentamente)
- Títulos de sección como celda dentro del grid Bauhaus (`grid-titulo-celda`), posición aleatoria en cada carga
- Preview local en `localhost:5001` — regenerar HTML con `GET /regen`

**En progreso / pendiente inmediato:**
- Afinar comportamiento de líneas SVG (posición correcta respecto a columnas CSS grid)

**Próximos pasos priorizados:**
1. Verificar líneas SVG en modo oscuro y modo claro
2. Bugs Python del backlog (ver sección Issues)
3. Deploy a Render tras estabilizar el diseño

---

## Roles: Claude Code vs Cline

| Tarea | Agente |
|---|---|
| Edición rápida de CSS/JS, iteración visual | **Cline** |
| Arquitectura, decisiones, memoria entre sesiones | **Claude Code** |
| Bugs Python (analyzer, fetcher, synthesizer) | **Cline** (implementación) + **Claude Code** (revisión) |
| Commits, push, session-report | **Claude Code** |

**Protocolo de handoff:**
1. El agente que termina hace commit
2. Actualiza "Estado actual" arriba con qué hizo y qué queda
3. El siguiente agente lee esta sección antes de tocar nada

---

## Arquitectura clave

```
config.py          — fuentes RSS, modelos AI, límites
pipeline.py        — orquestador central (reemplaza app.py para lógica)
renderer/          — paquete modular: shell.py + tabs/ + components/
static/css/        — 4 ficheros CSS (ver sección Rediseño)
static/js/         — tabs.js, lines.js, sort.js, search.js
preview.py         — servidor local puerto 5001 para iterar diseño
```

**Variables de entorno requeridas:** `ANTHROPIC_API_KEY`, `REDIS_URL` (opcional), `DIGEST_PASSWORD`

---

## Rediseño CSS — EnPapel (mayo-junio 2026)

Paleta arena/crema oscura: `--bg: #0d0b08`, acento `--accent: #c8a470`, fuente Playfair Display.
Modo día en `body.light {}` dentro de `reset.css`.
**No tocar:** acento rojo `#dc2626` de Izquierda Crítica, violeta `#7c3aed` de Asombro.

---

# Issues del proyecto noticias

Archivo de incidencias y optimizaciones pendientes. Claude se encargará de cada punto cuando el usuario lo indique.

Prioridades: **🔴 Bug** → **🟡 Robustez** → **🟢 Optimización** → **⚪ Token/rendimiento**

---

## 🔴 BUGS

### B1 — `analyzer.py:219` — `max_tokens=900` insuficiente para lotes grandes

- **Archivo:** `noticias/analyzer.py` línea 219
- **Problema:** Se envía un lote de N artículos a la IA pidiendo 8 campos por artículo + `analisis_general`, pero solo se conceden 900 tokens de salida. Si N ≥ 5 (típico), la respuesta se trunca → JSON inválido → análisis perdido sin error visible.
- **Solución:** Calcular `max_tokens` como `max(900, len(nuevos) * 150)`. 150 tokens/artículo es más seguro.

### B2 — `fetcher.py:82/115` — Race condition en `_fuentes_fallidas`

- **Archivo:** `noticias/fetcher.py` líneas 82 y 115
- **Problema:** `_fuentes_fallidas.append()` es llamado desde múltiples hilos del `ThreadPoolExecutor` sin lock. Atómico por GIL en CPython, pero el orden es impredecible y el patrón es frágil.
- **Solución:** Usar `threading.Lock` alrededor del append, o reemplazar `list[str]` por una `queue.Queue`.

### B3 — `noise_filter.py` — Módulo nunca llamado desde main.py

- **Archivo:** `noticias/main.py` — en ninguna parte se importa o llama a `detectar_ruido()`
- **Problema:** `noise_filter.py` está completo pero el pipeline lo ignora. Código muerto o integración incompleta.
- **Solución:** Integrar la llamada a `detectar_ruido(noticias)` en `main.py` antes del análisis con IA, para filtrar artículos redundantes y ahorrar tokens.

### B4 — `synthesizer.py:205` — Default de `asombro` incorrecto

- **Archivo:** `noticias/synthesizer.py` línea 205
- **Problema:** `a.get("asombro", 2)` — usa default 2 para artículos sin análisis, priorizándolos sobre los analizados con `asombro=0` o `asombro=1`. Inversión de prioridad.
- **Solución:** Cambiar default a 0: `a.get("asombro", 0)`.

### B5 — `noise_filter.py:84` — Resumen truncado a 75 caracteres (insuficiente para clasificar)

- **Archivo:** `noticias/noise_filter.py` línea 84
- **Problema:** El prompt envía `resumen[:75]` (~10-15 palabras). Un clasificador humano no puede determinar si un artículo es redundante con tan poca información. La IA probablemente clasifica aleatoriamente, generando tanto falsos positivos (artículos señal eliminados) como falsos negativos (redundancias no detectadas).
- **Solución:** Aumentar a `resumen[:200]`. El coste en tokens es marginal (~30 tokens extra por artículo para un lote de 10) y la precisión mejora drásticamente.

### B6 — `claude_client.py:262-268` — Dead code: limpieza de fences markdown en Gemini con JSON mode

- **Archivo:** `noticias/claude_client.py` líneas 262-268
- **Problema:** La línea 214 fuerza `responseMimeType: application/json` en Gemini, lo que hace que Gemini devuelva JSON puro SIN bloques markdown. El código de líneas 263-266 que busca y elimina ``` es dead code que nunca se ejecuta. Lo mismo en línea 203-205 para la rama Anthropic (línea 133-134) — pero ahí sí puede ser necesario porque json.loads fallaría con fences. En Gemini, con JSON mode activo, json.loads nunca fallará por fences, pero el código sigue intentando limpiarlos.
- **Solución:** Eliminar la limpieza de fences en la rama Gemini (líneas 263-266) y simplificar a `return json.loads(texto)` directamente.

### B7 — `main.py:70-97` — Descarga y análisis secuenciales entre principales y alternativas

- **Archivo:** `noticias/main.py` líneas 70-97
- **Problema:** `obtener_todas_las_noticias()` y `obtener_noticias_alternativas()` se ejecutan en serie (70→81, luego 94→97). Lo mismo para los dos análisis con IA. El tiempo total de ejecución es la suma de ambos, cuando podrían solaparse con `ThreadPoolExecutor`.
- **Solución:** Paralelizar ambas descargas y ambos análisis para reducir el tiempo de pared ~40% sin coste extra de tokens. `noticias` y `alternativas` se descargan en paralelo; luego ambos análisis también en paralelo.

---

## 🟡 ROBUSTEZ

### R1 — `claude_client.py:112` — Sin timeout en llamada Anthropic

- **Archivo:** `noticias/claude_client.py` línea 112
- **Problema:** `client.messages.create(**kwargs)` sin `timeout=`. Si la API se cuelga, el pipeline se bloquea indefinidamente.
- **Solución:** Añadir `timeout=120` (o 60 para Haiku, 120 para Sonnet).

### R2 — `article_cache.py:55` — Redis sin reconexión

- **Archivo:** `noticias/article_cache.py` línea 55
- **Problema:** `_conectar_redis()` se ejecuta solo en `__init__`. Si Redis falla al arrancar, se usa disco permanentemente. Si Redis cae después, no se detecta (el `try/except` en `guardar()` lo captura pero no reconecta).
- **Solución:** Añadir método `_intentar_reconectar_redis()` que se llame periódicamente si `self._redis` es None y `_REDIS_URL` está configurada.

### R3 — `analyzer.py:227-228` — Silencio ante artículos perdidos

- **Archivo:** `noticias/analyzer.py` líneas 227-228
- **Problema:** Si la IA devuelve menos artículos de los enviados, los restantes reciben `{}` (valores por defecto) sin print de advertencia. El usuario nunca sabe que faltan análisis.
- **Solución:** Si `len(nuevos_idx) != len(resultado.get("articulos", []))`, mostrar `⚠️ La IA devolvió X artículos de Y esperados` antes de rellenar con defaults.

### R4 — `article_cache.py:91` — Redis TTL de 72h para toda la caché (incluye secciones 6h)

- **Archivo:** `noticias/article_cache.py` línea 91
- **Problema:** `self._redis.setex(_REDIS_KEY, _TTL_ARTICULO, blob)` guarda todo el blob JSON con TTL de 72h. Pero dentro del blob, las secciones `categorias` y `sintesis` tienen TTL de 6h según la lógica de la app. Aunque la app filtra correctamente en lectura, Redis almacena datos caducados durante 72h, desperdiciando memoria y ancho de banda en cada escritura.
- **Solución:** Usar TTLs separados por sección, o al menos usar el TTL mínimo de todas las secciones.

### R5 — `discoverer.py:199` — Sin manejo específico de errores HTTP

- **Archivo:** `noticias/discoverer.py` línea 199
- **Problema:** `requests.post(_GEMINI_URL, json=payload, timeout=60)` con `resp.raise_for_status()` atrapado en un `except Exception` genérico. No distingue entre 401 (auth), 429 (rate limit) o 500 (servidor). A diferencia de `claude_client.py` que tiene manejo específico por código de estado.
- **Solución:** Añadir manejo específico para 401/403, 429 y 5xx como en claude_client.py.

---

## 🟢 OPTIMIZACIONES

### O1 — `main.py` — Coste total nunca se muestra

- **Archivo:** `noticias/main.py` (final del `main()`)
- **Problema:** `claude_client.py` tiene `resumen_coste()` pero `main.py` nunca lo llama. El usuario no ve el gasto de la ejecución.
- **Solución:** Al final de `main()`, justo antes de `print(f"\n⏱  Completado en...")`, añadir `from claude_client import resumen_coste; print(f"  💰 {resumen_coste()}")`.

### O2 — `claude_client.py:183-284` — Lógica de reintentos duplicada

- **Archivo:** `noticias/claude_client.py`
- **Problema:** Las ramas Gemini y Anthropic tienen su propia implementación de reintentos con backoff exponencial. Dos implementaciones que hacen lo mismo = doble mantenimiento, doble riesgo de bugs.
- **Solución:** Extraer la lógica de reintento con backoff a una función común `_reintentar(max_retries, base_wait, fn)`.

### O3 — `renderer/__init__.py:67-68` — Campo `destacado` nunca asignado

- **Archivo:** `noticias/renderer/__init__.py`
- **Problema:** `_splash_headlines()` busca `a.get("destacado")` pero ningún módulo asigna este campo. El splash siempre muestra los primeros 3 artículos sin criterio de "destacado".
- **Solución:** Usar `asombro` como proxy: `a.get("asombro", 0) >= 2` en lugar de `a.get("destacado")`.

### O4 — `config.py:30-31` — Mismos modelos sin diferenciar

- **Archivo:** `noticias/config.py`
- **Problema:** `GEMINI_MODEL` y `GEMINI_MODEL_ANALISIS` ambos apuntan a `gemini-2.0-flash`. Tener dos variables sugiere que deberían diferir (ej: un modelo más barato para análisis, otro más capaz para síntesis).
- **Solución:** Documentar la intención o unificar en una sola variable. Si se quiere diferenciar, asignar un modelo más ligero a análisis (ej: `gemini-1.5-flash`).

---

## ⚪ AHORRO DE TOKENS / RENDIMIENTO

### T1 — `analyzer.py:213` — `resumen[:300]` → podría reducirse a `resumen[:200]`

- **Archivo:** `noticias/analyzer.py` línea 213
- **Impacto actual:** 300 chars por artículo se envían a la IA para análisis. Para 10 artículos = ~3000 chars de input (~750 tokens).
- **Propuesta:** Reducir a 200 chars. El análisis de sesgo y crítica no necesita el cuerpo completo del artículo, solo el enfoque y los detalles clave. 200 chars (~30 palabras) son suficientes para determinar sesgo y ángulo editorial.
- **Ahorro estimado:** ~33% menos tokens de input en cada llamada de análisis. Si hay ~10 categorías con ~3 artículos cada una (~30 llamadas), ahorro de ~10,000 tokens/ejecución (~$0.0008 en Gemini, ~$0.03 en Claude Haiku).

### T2 — `synthesizer.py:226` — `resumen[:250]` → podría reducirse a `resumen[:150]`

- **Archivo:** `noticias/synthesizer.py` línea 226
- **Impacto actual:** 250 chars por artículo para síntesis. La síntesis solo necesita saber de qué trata cada artículo para agruparlos, no necesita riqueza de detalle.
- **Propuesta:** Reducir a 150 chars. Suficiente para que la IA detecte co-ocurrencia de temas.
- **Ahorro estimado:** ~40% menos tokens de input en la llamada de síntesis (~3,000 tokens menos si hay 50 candidatos → ~$0.0003 en Gemini).

### T3 — `analyzer.py:32-169` — System prompt muy verboso → verificar si merece los tokens de cache write

- **Archivo:** `noticias/analyzer.py` líneas 32-169
- **Impacto actual:** ~2000+ tokens de system prompt. La primera llamada de cada generación paga cache_write (~$1.00/MTok en Haiku). Cada ~2000 tokens de cache_write cuestan ~$0.002. Con 5 categorías en paralelo, la primera ejecución paga ~$0.01 solo en cache_write.
- **Propuesta concreta:** Los ejemplos GOOD/BAD de crítica (líneas 59-66) ocupan ~200 tokens. El contexto del ecosistema mediático (líneas 141-153) ocupa ~100 tokens. Evaluar si mantenerlos o recortarlos. Si se recortan, la primera llamada ahorra ~$0.00015 — mínimo, pero en ejecuciones diarias se acumula.
- **Decisión:** Mantener tal cual. La calidad del análisis justifica el coste de cache write inicial. El prompt caching hace que las siguientes llamadas cuesten solo ~$0.0002 cada una.

### T4 — `noise_filter.py:84` — Arreglar B5 (resumen[:75]→[:200]) permitirá ahorrar tokens en re-análisis

- **Archivo:** `noticias/noise_filter.py` (depende de B3 — integrar noise_filter en pipeline)
- **Problema:** Si el noise_filter clasifica mal (por resumen muy corto), se filtran artículos señal como ruido o se dejan pasar redundancias. Las redundancias no filtradas llegan al analyzer, donde se pagan tokens para analizar artículos que no aportan nada nuevo.
- **Propuesta:** Al corregir B5 se eliminan falsos negativos → se filtran más redundancias → menos artículos llegan al analyzer → ahorro de tokens en análisis.
- **Ahorro estimado:** Si el 20% de los artículos son redundantes y el noise_filter los detecta correctamente, se ahorra ~20% de los tokens de análisis (~4,000 tokens/ejecución).

### T5 — `main.py:70-97` — Descarga paralela reduce tiempo pero no tokens (B7 es solo tiempo)

- **Nota:** A diferencia de los otros puntos, B7 reduce tiempo de ejecución pero NO tokens consumidos. Se ha movido aquí como referencia cruzada, pero no es un ahorro de tokens per se.
- **Ver también:** B7 para la implementación de paralelización.

### T6 — `synthesizer.py:64-142` — System prompt de síntesis muy extenso

- **Archivo:** `noticias/synthesizer.py` líneas 64-142
- **Impacto actual:** ~2800+ tokens de system prompt. Similar al analyzer, paga cache_write en la primera llamada.
- **Propuesta:** Los ejemplos de títulos GOOD/BAD (líneas 117-123) ocupan ~120 tokens. Los ejemplos de síntesis GOOD/BAD (líneas 130-132) ocupan ~200 tokens. El contexto de errores comunes (líneas 127-133) ocupa ~200 tokens. Total: ~520 tokens de ejemplos extensos.
- **Ahorro estimado:** Recortar ejemplos GOOD/BAD a solo texto (sin ejemplos) ahorraría ~300 tokens del cache_write. Con Sonnet a $3.75/MTok para cache_write, ahorro de ~$0.001 en la primera llamada de síntesis.
- **Decisión:** Mantener. Los ejemplos mejoran la calidad de la síntesis (párrafo 1 factual, párrafo 2 contraste, párrafo 3 opcional). El ahorro es marginal.

### T7 — `noise_filter.py:108` — Caché solo Redis → Si Redis no está, se ejecuta cada vez

- **Archivo:** `noticias/noise_filter.py` línea 108
- **Problema:** `_cache._redis_set(clave, json.dumps(...), ex=_TTL)` usa el método privado `_redis_set` que solo escribe en Redis, nunca en disco. Si Redis no está configurado, el noise_filter se ejecuta en cada ejecución del pipeline porque nunca hay datos cacheados.
- **Solución:** Usar el método público del cache (`set_articulo` o similar) o añadir un método específico en `ArticleCache` que guarde en disco también. Alternativa: permitir que `noise_filter` tenga su propio cache en disco si Redis no está disponible.
- **Ahorro estimado:** Si noise_filter se ejecuta a diario (B3 implementado) sin Redis, cada ejecución cuesta ~40 artículos * ~30 tokens/output = ~1200 tokens de Gemini Flash (~$0.00009). Pequeño, pero se acumula.
