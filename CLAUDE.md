# Preferencias del proyecto

## Idioma
Responde siempre en español, independientemente del idioma en que se escriba el mensaje.

---

# Estado del proyecto

## Qué es esto
Digest personal de noticias en español. Descarga feeds RSS de ~51 fuentes organizadas por categoría, las analiza con Claude (sesgo, crítica, sentimiento) y genera un HTML interactivo con filtros, síntesis cruzada y vista inmersiva. Se despliega en Render como servidor Flask.

## Despliegue
- **Repositorio:** https://github.com/Dipenaa/noticias-digest
- **URL en producción:** https://noticias-digest.onrender.com
- **Plataforma:** Render (plan gratuito)
- **Variables de entorno requeridas en Render:**
  - `ANTHROPIC_API_KEY` — para el análisis con Claude (el usuario aún no la tiene, tiene que comprarla en console.anthropic.com)
  - `GEMINI_API_KEY` — solo para discoverer.py (opcional)
- **Keep-alive:** configurar cron-job.org para hacer ping a `/estado` cada 14 minutos (el usuario lo tiene que hacer desde casa)

## Lo que se hizo en esta sesión

### Bugs corregidos
- `config.py` no tenía `ANTHROPIC_API_KEY` ni `CLAUDE_MODEL` → causaba ImportError al arrancar
- `app.py` comprobaba `GEMINI_API_KEY` para activar la IA en vez de `ANTHROPIC_API_KEY`
- Comentarios y docstrings que decían "Gemini" cuando el análisis lo hace Claude

### Optimizaciones de coste (muy importantes)
- **`article_cache.py`** — nuevo módulo de caché persistente en disco (article_cache.json):
  - Artículos ya analizados se guardan 24h → en ciclos normales solo se mandan a Claude los artículos nuevos
  - Caché de síntesis cruzada 6h → si los artículos no cambiaron, no se llama a Sonnet
  - Singleton `shared` para que analyzer.py y synthesizer.py compartan el mismo estado
- **Haiku para análisis** (`claude-haiku-4-5-20251001`) en vez de Sonnet → 20× más barato
- **Sonnet** (`claude-sonnet-4-6`) se reserva solo para la síntesis cruzada
- **Deduplicación de artículos** en fetcher.py → elimina URLs duplicadas antes del análisis

### Nuevas funcionalidades
- **PWA (Progressive Web App):** el usuario puede instalar el digest en el móvil como app
  - `/manifest.json` — configuración de la app
  - `/icon.svg` — icono
  - `/sw.js` — service worker (funciona sin conexión con el último digest cacheado)
- **Validación de API key al arrancar** — aviso inmediato en logs si falta ANTHROPIC_API_KEY
- **`/estado` mejorado** — ahora incluye `anthropic_key_ok`, `cache_articulos`, `cache_sintesis`

## Problema pendiente importante
El disco de Render gratuito es efímero: `article_cache.json` se pierde cada vez que el servidor se reinicia. Soluciones posibles (no implementadas aún):
1. **Upstash Redis** (gratis hasta cierto límite) — sustituir el JSON por Redis
2. **Render Disk** (de pago) — añadir disco persistente en Render
3. **Render plan Starter** (7$/mes) — el servidor no duerme nunca y la caché aguanta más

## Arquitectura resumida
```
config.py          — API keys, modelos, fuentes RSS
fetcher.py         — Descarga feeds RSS en paralelo (ThreadPoolExecutor)
analyzer.py        — Análisis de sesgo con Claude Haiku (con caché)
synthesizer.py     — Síntesis cruzada con Claude Sonnet (con caché)
renderer.py        — Genera el HTML completo autocontenido
article_cache.py   — Caché persistente (singleton `shared`)
app.py             — Servidor Flask: /, /regenerar, /analizar, /estado, /manifest.json, /sw.js
main.py            — Alternativa CLI para ejecutar localmente
discoverer.py      — Herramienta para descubrir nuevos feeds RSS con Gemini
```

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
