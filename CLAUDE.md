# Preferencias del proyecto

## Idioma
Responde siempre en español, independientemente del idioma en que se escriba el mensaje.

---

# Estado del proyecto

## Qué es esto
Digest personal de noticias en español. Descarga feeds RSS de ~51 fuentes organizadas por categoría, las analiza con Claude (sesgo, crítica, sentimiento, asombro) y genera un HTML interactivo con filtros, síntesis cruzada, pestaña Asombro y vista inmersiva. Se despliega en Render como servidor Flask.

## Despliegue
- **Repositorio:** https://github.com/Dipenaa/noticias-digest
- **URL en producción:** https://noticias-digest.onrender.com
- **Plataforma:** Render (plan gratuito)
- **Variables de entorno requeridas en Render:**
  - `ANTHROPIC_API_KEY` — para el análisis con Claude (requerida)
  - `REDIS_URL` — para caché persistente (opcional, Upstash Redis gratuito)
  - `GEMINI_API_KEY` — solo para discoverer.py (opcional)
  - `DIGEST_PASSWORD` — contraseña de acceso básico (por defecto: "dipe")
- **Keep-alive:** configurar cron-job.org para hacer ping a `/estado` cada 14 minutos

## Arquitectura resumida
```
config.py             — API keys, modelos, fuentes RSS; MAX_ARTICULOS_POR_FUENTE=1
fetcher.py            — Descarga feeds RSS en paralelo; rastrea fuentes fallidas
analyzer.py           — Análisis de sesgo con Claude Haiku (con caché y prompt caching)
synthesizer.py        — Síntesis cruzada con Claude Sonnet (con caché y pre-filtro de keywords)
claude_client.py      — Cliente Claude: reintentos, rate limit, prompt caching, coste en $
noise_filter.py       — Detecta artículos repetitivos (ruido); marca es_ruido=True
macro_tracker.py      — Identifica 2-5 procesos mundiales del día (Haiku, caché 24h)
watch.py              — Vigilancia de condiciones personalizadas (batch, caché 6h)
briefing_generator.py — Memo de inteligencia diario (Sonnet, caché 12h)
pipeline.py           — Pipeline central: estado compartido entre hilos; _INTERVALO_HORAS=18
renderer.py           — SHIM de compatibilidad — el código real está en el paquete renderer/
renderer/             — Paquete modular: shell.py + tabs/ + components/
styles.py             — Todo el CSS (separado del renderer)
article_cache.py      — Caché persistente: Redis si REDIS_URL existe, sino JSON en disco
app.py                — Servidor Flask (~150 líneas); delega toda lógica a pipeline.py
main.py               — Alternativa CLI para ejecutar localmente
discoverer.py         — Herramienta para descubrir nuevos feeds RSS con Gemini
preview.py            — Servidor local en localhost:5001 para iterar diseño sin gastar tokens
autoresearch_analyzer.py     — Script de autoresearch para optimizar el prompt de analyzer.py
autoresearch_synthesizer.py  — Script de autoresearch para optimizar el prompt de synthesizer.py
```

## Presupuesto de coste API

**Máximo $0.10-0.15/día.** Antes de añadir cualquier nueva llamada a Claude, estima su coste.

- Haiku: $0.80 input / $4.00 output por MTok (caché read: $0.08)
- Sonnet: $3.00 input / $15.00 output por MTok (caché read: $0.30)
- Ver coste acumulado en los logs de Render: líneas `💰 haiku in=... → $0.00xx (total $...)`

## Optimizaciones de coste ya aplicadas (no revertir)

- `MAX_ARTICULOS_POR_FUENTE = 1` en config.py (era 2)
- `_INTERVALO_HORAS = 18` en pipeline.py (era 12) — regenera cada 18h en vez de 12h
- `cache_system=True` en TODAS las llamadas a `llamar_claude` — cachea system prompts
- `_MAX_ARTICULOS_SINTESIS = 80` con pre-filtro de keywords (descarta temas únicos antes de Claude)
- Filtro `es_ruido` en synthesizer — descarta artículos repetitivos antes de Claude
- `separators=(',', ':')` en `json.dumps` del payload del synthesizer (~900 tokens menos)
- watch.py: N condiciones → 1 llamada batch (era N llamadas individuales)
- `max_tokens` reducidos: analyzer 700, briefing 550, noise_filter 1200

## Modelos Claude
- **Análisis masivo:** `claude-haiku-4-5-20251001` (20× más barato que Sonnet)
- **Síntesis cruzada:** `claude-sonnet-4-6` (solo para detectar historias comunes)
- **Prompt caching:** activo en todos los módulos vía `cache_system=True`; ahorra ~70-80% en tokens de instrucciones

## Skills disponibles

### Skills de proyecto (`.claude/skills/`)
- **`redisenar`** — Workflow completo para iterar el diseño visual sin gastar tokens. Usa `preview.py`.
- **`crear-skill`** — Crea o mejora skills para este proyecto.
- **`briefing`** — Memo de inteligencia estilo PDB sobre el digest del día (~300 palabras).
- **`vigilar`** — Gestiona condiciones de alerta que se comprueban en cada generación del digest.

### Skills globales (`~/.claude/skills/`) — disponibles en todos los proyectos
| Skill | Trigger | Qué hace |
|---|---|---|
| `/pensar` | Manual | Análisis profundo para tomar una decisión difícil. Convergente. |
| `/explorar` | Automático | Genera opciones y posibilidades antes de decidir. Divergente. |
| `/criticar` | Automático | Crítica honesta de código, planes o textos. |
| `/sintetizar` | Automático | Síntesis densa de información compleja. |
| `/investigar` | Automático | Research web → síntesis → guardar. |
| `/autoresearch` | Manual | Loop autónomo de experimentación: optimiza un fichero iterando y midiendo. |
| `/auto-mejora` | Manual | Convierte lo aprendido en sesiones en reglas y skills duraderas. |
| `/enjambre` | Manual | Divide tareas grandes en subtareas paralelas (hasta 12 agentes). |
| `/orientar` | Automático | Recupera contexto al inicio de sesión. Bootstrap si memoria vacía. |
| `/rutina-diaria` | Manual | Inicio de jornada: orientación + briefing + producción + agenda. |
| `/session-report` | Manual | Resumen de lo hecho en la sesión para handoff. |
| `/pipeline` | Manual | Encadena skills: `/pipeline briefing → guardar`. |

### Pipelines nombradas (`~/.claude/pipelines.md`)
| Pipeline | Cadena | Cuándo |
|---|---|---|
| `/morning` | orientar → briefing → check-status prod | Al empezar el día |
| `/cierre` | session-report → guardar | Al terminar |
| `/research` | investigar → sintetizar → guardar | Investigación completa |
| `/audit` | criticar → explorar | Revisar algo a fondo |

## Autoresearch de prompts (21 mayo 2026)
Se ejecutó `/autoresearch` sobre los dos prompts principales con artículos ficticios de prueba:

**analyzer.py** — baseline 8/9 → final 9/9
- Mejora: las críticas deben empezar directamente con la observación, no con "El artículo presenta..."

**synthesizer.py** — baseline 8/9 → final 9/9
- Mejora: los títulos de grupos deben tener verbo activo que capture la tensión de la historia
- Bug corregido: usaba Haiku en vez de Sonnet (modelo equivocado)

Coste total del autoresearch: ~1.5 céntimos.

Scripts reutilizables guardados: `autoresearch_analyzer.py` y `autoresearch_synthesizer.py`.

## Lo que se arregló (historial)
- **Seguridad:** clave Gemini real eliminada del código fuente
- **Caché persistente en Render:** article_cache.py usa Redis si REDIS_URL está configurada
- **claude_client.py:** cliente Claude centralizado con reintentos, rate limit y prompt caching
- **Feeds fallidos visibles:** la pestaña Estadísticas muestra fuentes que no devolvieron artículos
- **Móvil:** barra de pestañas con scroll horizontal
- **CSS separado:** styles.py contiene todo el CSS; renderer.py solo lógica Python
- **Autenticación básica:** app.py protege todas las rutas con contraseña (DIGEST_PASSWORD)
- **synthesizer.py:** corregido modelo incorrecto (era Haiku, debe ser Sonnet)
- **Botones de regeneración IA eliminados (25 mayo 2026):** quitados el botón "Regenerar análisis IA" del banner y el botón "Generar síntesis con Claude" de la pestaña Síntesis — evita llamadas API no autorizadas
- **Tema Dark Premium aplicado (25-26 mayo 2026):** `styles.py` reemplazado por el sandbox oscuro + correcciones
- **Síntesis en generación normal (26 mayo 2026):** `_generar()` en app.py ahora llama a `sintetizar_noticias()` — antes solo se ejecutaba via `/analizar`
- **CSS proceso-* restaurado (26 mayo 2026):** toda la CSS de `.proceso-strip`, `.proceso-body`, `.proceso-grid`, etc. se perdió al aplicar el tema y fue restaurada adaptada al tema oscuro
- **Contraste mejorado (26 mayo 2026):** `--txt-3` subió de `#3d3d3f` a `#636366`; `--txt-2` de `#86868b` a `#aeaeb2`; `nav a` y `.sort-btn` más visibles
- **Pestaña Actualidad vacía resuelta (27 mayo 2026):** macro_tracker usaba filtro substring que bloqueaba categorías válidas; corregido a exact match + prompt ampliado a procesos nacionales + fallback regex para JSON
- **Coste API optimizado (27 mayo 2026):** 8 cambios reducen gasto estimado ~60-70% (ver sección "Optimizaciones de coste")
- **Renderer modularizado (27 mayo 2026):** renderer.py es ahora un shim; código real en paquete `renderer/`; pipeline.py centraliza la lógica de app.py
- **claude_client.py con tracking de coste en $ (27 mayo 2026):** `_calcular_coste()`, `reset_coste()`, `resumen_coste()` + logging `💰` con importe real por llamada

## Estado del diseño — rama `claude/buenas-xo9D9` (26 mayo 2026)
El tema **Dark Premium** ya está en producción (`styles.py`).

Características:
- Fondo negro puro (`#000`), glassmorphism en cards (`rgba(255,255,255,0.033)`)
- Cards con hover expansion: resumen se despliega, crítica IA emerge
- Barras de espectro de sesgo (CSS puro con `[title="sesgo"]`)
- Buscador estilo Spotlight (180px → 400px al hacer foco)
- Sort bar como control segmentado iOS (4 opciones, derecha)
- Sidebar con pestañas: acento azul en activa
- Tipografía fluida con `clamp()`, títulos serif con gradiente

## Cómo activar Redis (Upstash — gratuito)
1. Ir a https://upstash.com y crear una base de datos Redis gratuita
2. Copiar la "Redis URL" (formato `rediss://default:xxx@host:port`)
3. Añadir `REDIS_URL=rediss://...` en las variables de entorno de Render
4. Redeploy — el servidor usará Redis automáticamente

## Cómo ejecutar localmente
```bash
git clone https://github.com/Dipenaa/noticias-digest.git
cd noticias-digest
pip install -r requirements.txt
export ANTHROPIC_API_KEY=tu_clave
python main.py          # genera noticias.html y lo abre
# o
python app.py           # servidor web en localhost:5000
# o (para iterar diseño sin tokens)
python preview.py       # vista previa en localhost:5001
```

## Infraestructura activa (confirmado 26 mayo 2026)
- **Upstash Redis** — base de datos "Noticias", AWS Ireland, activa, $0.00/mes
- **Cron-job.org** — ping a `/icon.svg` cada 10 min, todos los eventos 200 OK

## Pendiente
- Verificar feeds RSS de Historia y Antropología (no se puede desde entorno remoto — comprobar en pestaña Estadísticas en producción)
- Configurar Playwright MCP para iterar diseño con screenshots reales (usuario aprobó)
