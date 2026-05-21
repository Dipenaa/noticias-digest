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
- **Keep-alive:** configurar cron-job.org para hacer ping a `/estado` cada 14 minutos

## Arquitectura resumida
```
config.py          — API keys, modelos, fuentes RSS
fetcher.py         — Descarga feeds RSS en paralelo; rastrea fuentes fallidas
analyzer.py        — Análisis de sesgo con Claude Haiku (con caché)
synthesizer.py     — Síntesis cruzada con Claude Sonnet (con caché)
renderer.py        — Genera el HTML completo autocontenido
article_cache.py   — Caché persistente: Redis si REDIS_URL está configurada, sino JSON en disco
app.py             — Servidor Flask: /, /regenerar, /analizar, /estado, /manifest.json, /sw.js
main.py            — Alternativa CLI para ejecutar localmente
discoverer.py      — Herramienta para descubrir nuevos feeds RSS con Gemini
```

## Modelos Claude
- **Análisis masivo:** `claude-haiku-4-5-20251001` (20× más barato que Sonnet)
- **Síntesis cruzada:** `claude-sonnet-4-6` (solo para detectar historias comunes)

## Lo que se arregló (sesión actual)
- **Seguridad:** clave Gemini real eliminada del código fuente (config.py)
- **Caché persistente en Render:** article_cache.py ahora usa Redis si se configura REDIS_URL
  - Sin Redis → sigue usando JSON en disco (se pierde al reiniciar en Render gratuito)
  - Con Redis (Upstash) → la caché sobrevive reinicios → ahorro real de tokens
- **Referencias "Gemini" eliminadas:** todos los textos visibles al usuario ya dicen "Claude"
  - Footer, cabecera, pestaña Síntesis, pestaña Destacadas, estadísticas, página de carga
- **Feeds fallidos visibles:** la pestaña Estadísticas muestra qué fuentes no devolvieron artículos
- **Móvil:** la barra de pestañas ahora hace scroll horizontal (no desborda)

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
```

## Pendiente
- Configurar cron-job.org para keep-alive (ping a /estado cada 14 min)
- Verificar que las URLs RSS de Historia y Antropología funcionan en producción
- Si los feeds de Historia/Antropología fallan, usar discoverer.py para encontrar alternativas
