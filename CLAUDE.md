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
config.py             — API keys, modelos, fuentes RSS
fetcher.py            — Descarga feeds RSS en paralelo; rastrea fuentes fallidas
analyzer.py           — Análisis de sesgo con Claude Haiku (con caché y prompt caching)
synthesizer.py        — Síntesis cruzada con Claude Sonnet (con caché)
claude_client.py      — Cliente Claude compartido: reintentos, rate limit, prompt caching
renderer.py           — Genera el HTML completo autocontenido
styles.py             — Todo el CSS (separado del renderer)
article_cache.py      — Caché persistente: Redis si REDIS_URL existe, sino JSON en disco
app.py                — Servidor Flask: /, /regenerar, /analizar, /estado, /manifest.json, /sw.js
main.py               — Alternativa CLI para ejecutar localmente
discoverer.py         — Herramienta para descubrir nuevos feeds RSS con Gemini
preview.py            — Servidor local en localhost:5001 para iterar diseño sin gastar tokens
autoresearch_analyzer.py     — Script de autoresearch para optimizar el prompt de analyzer.py
autoresearch_synthesizer.py  — Script de autoresearch para optimizar el prompt de synthesizer.py
```

## Modelos Claude
- **Análisis masivo:** `claude-haiku-4-5-20251001` (20× más barato que Sonnet)
- **Síntesis cruzada:** `claude-sonnet-4-6` (solo para detectar historias comunes)
- **Prompt caching:** el system prompt de analyzer.py se cachea entre llamadas (~80% menos tokens en ciclos normales)

## Skills disponibles

### Skills de proyecto (`.claude/skills/`)
- **`redisenar`** — Workflow completo para iterar el diseño visual sin gastar tokens. Usa `preview.py`.
- **`crear-skill`** — Crea o mejora skills para este proyecto.

### Skills globales (`~/.claude/skills/`) — disponibles en todos los proyectos
| Skill | Trigger | Qué hace |
|---|---|---|
| `/pensar` | Manual | Análisis profundo con ultrathink + effort max. Para decisiones importantes. |
| `/explorar` | Automático | Brainstorming, posibilidades, ángulos no obvios. |
| `/criticar` | Automático | Crítica honesta de código, planes o textos. |
| `/sintetizar` | Automático | Síntesis densa de información compleja. |
| `/autoresearch` | Manual | Loop autónomo de experimentación: optimiza un fichero iterando y midiendo. |
| `/auto-mejora` | Manual | Convierte lo aprendido en sesiones en reglas y skills duraderas. |
| `/enjambre` | Manual | Divide tareas grandes en subtareas paralelas (hasta 12 agentes). |
| `/orientar` | Manual | Recupera contexto cuando se pierde el hilo entre sesiones. |
| `/session-report` | Manual | Resumen de lo hecho en la sesión para handoff. |

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

## Diseño en progreso — rama `claude/buenas-xo9D9` (25 mayo 2026)
El nuevo tema **Dark Premium** está en `styles_sandbox.py`. Aún no aplicado a producción (`styles.py`).

Cambios del sandbox respecto a producción:
- Tema completamente oscuro (#000 fondo, glassmorphism en cards)
- Cards con hover expansion: el resumen se despliega y la crítica IA emerge al pasar el ratón
- Barras de espectro de sesgo (CSS puro, selectores `[title="sesgo"]`)
- Buscador estilo Spotlight: pequeño en reposo, se expande al hacer foco
- Sort bar como control segmentado iOS (4 opciones, compacto y alineado a la derecha)
- Sidebar con pestañas: acento azul en la activa, inactivas legibles
- Tipografía fluida con `clamp()`, títulos serif con gradiente

Para aplicar a producción: copiar `styles_sandbox.py` → `styles.py` y hacer push a master.

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

## Pendiente
- Configurar cron-job.org para keep-alive (ping a /estado cada 14 min)
- Verificar feeds RSS de Historia y Antropología en producción; usar discoverer.py si fallan
- Considerar Upstash Redis para que la caché sobreviva reinicios de Render
