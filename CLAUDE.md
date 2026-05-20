# CLAUDE.md — Noticias Digest

## Project overview

A Spanish-language personal news digest system. It fetches RSS feeds from ~35 sources, analyzes articles with the Claude AI API (bias detection, editorial critique, sentiment), finds stories covered by multiple sources, and renders a self-contained dark-themed HTML page. Can run as a CLI one-shot or as a persistent Flask server deployed on Render.

## Architecture

```
config.py       ← Central config: RSS sources, API keys, limits
fetcher.py      ← Parallel RSS download (ThreadPoolExecutor, feedparser)
analyzer.py     ← Per-category AI analysis via Claude API (batch per category)
synthesizer.py  ← Cross-source story grouping and synthesis via Claude API
renderer.py     ← Self-contained HTML generation (all CSS inline, dark forest theme)
main.py         ← CLI entry point
app.py          ← Flask server for cloud deployment (Render)
render.yaml     ← Render.com deployment config
```

### Data flow

```
config.py (FUENTES + FUENTES_ALTERNATIVAS)
    → fetcher.py      → dict[category, list[article]]
    → analyzer.py     → enriches articles with: sesgo_ia, critica, importante, sentimiento
    → synthesizer.py  → list[story_group] (cross-source synthesis)
    → renderer.py     → HTML string
    → guardar_y_abrir / Flask response
```

### Article schema

Every article dict carries these fields throughout the pipeline:

| Field | Set by | Description |
|---|---|---|
| `titulo` | fetcher | Article title |
| `enlace` | fetcher | URL |
| `resumen` | fetcher | Plain-text summary, max 500 chars |
| `fuente` | fetcher | Source name (e.g. "El País") |
| `sesgo_fuente` | fetcher/config | Declared bias of the outlet |
| `fecha` | fetcher | Formatted date string |
| `sesgo_ia` | analyzer | AI-detected bias of the article |
| `critica` | analyzer | 1-2 sentence editorial critique |
| `importante` | analyzer | Boolean: one of the top 2 articles in the batch |
| `sentimiento` | analyzer | `"alarmista"` \| `"neutral"` \| `"optimista"` |

## Critical known issue: incomplete Gemini → Claude migration

The last commit (`4718b09`) migrated AI calls from Gemini to the Anthropic Claude API in `analyzer.py` and `synthesizer.py`, but **did not finish the migration**. The codebase is currently broken for AI features:

- `config.py` exports `GEMINI_API_KEY` / `GEMINI_MODEL` — **not** `ANTHROPIC_API_KEY` / `CLAUDE_MODEL`
- `main.py`, `analyzer.py`, `synthesizer.py` all `import ANTHROPIC_API_KEY, CLAUDE_MODEL from config` → **ImportError at startup**
- `app.py` still checks `GEMINI_API_KEY` to decide if AI is available (inconsistent with the others)
- `render.yaml` references `GEMINI_API_KEY` as the env var to set in Render Dashboard

**To fix**, `config.py` needs these additions (replacing or alongside the Gemini vars):
```python
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL      = "claude-sonnet-4-6"   # or whichever model
```
And `app.py` must be updated to check `ANTHROPIC_API_KEY` instead of `GEMINI_API_KEY`.

Running `python main.py --sin-ia` still works because it skips the AI imports.

## Key files to know

### `config.py`
The single place to change:
- `FUENTES` — main RSS sources by category (España, Internacional, Tecnología, Economía, Ciencia)
- `FUENTES_ALTERNATIVAS` — libertarian/anarchist press sources (España Libertaria, Internacional Libertario, Contrainformación)
- `MAX_ARTICULOS_POR_FUENTE` — how many articles to take per feed (default 5)
- `ARCHIVO_SALIDA` — output filename for CLI mode (default `noticias.html`)
- `IDIOMA_ANALISIS` — language for AI responses (default `"español"`)

Bias values used throughout: `"izquierda"` | `"centro-izquierda"` | `"centro"` | `"centro-derecha"` | `"derecha"` | `"desconocido"`

### `analyzer.py`
Sends all articles of a category in a single Claude API call (not one per article). Returns structured JSON with per-article fields plus an `analisis_general` paragraph for each category. Uses `temperature=0.2`. Parallelizes up to 3 categories at once (`_MAX_WORKERS_ANALYSIS = 3`) to respect rate limits.

Retry logic: exponential backoff, 4 attempts for rate limits (30s base), 4 attempts for 5xx errors (5s base).

### `synthesizer.py`
Single Claude API call with up to 120 articles (across both main and alternative sources). Groups articles covering the same specific event (not just topic), requiring ≥2 unique sources per group. Uses `max_tokens=8192`, `temperature=0.3`. Groups are sorted by article count descending.

### `renderer.py`
Generates a fully self-contained HTML file — no external dependencies. CSS uses a dark "Bosque Vivo" (living forest) green theme. Color constants for bias labels are defined in `analyzer.py` (`COLORES_SESGO`) and imported into `renderer.py`.

The HTML has tabs: one per category in FUENTES, one for "Prensa Libertaria" (FUENTES_ALTERNATIVAS), and a "Síntesis" tab showing cross-source story groups.

### `app.py`
Flask server with four routes:
- `GET /` — serves cached HTML, shows loading page while generating
- `GET /regenerar` — triggers background regeneration, redirects to `/`
- `GET /analizar` — re-runs only AI analysis on already-fetched news (no re-download)
- `GET /estado` — JSON status: `{generando, tiene_cache, ultimo_update, ultimo_error}`

Auto-regenerates every 6 hours (`_INTERVALO_HORAS = 6`). Thread safety via a single `threading.Lock()`. The `SIN_IA` env var (set to `"1"`, `"true"`, or `"yes"`) disables AI analysis.

## Running locally

```bash
# Install dependencies
pip install -r requirements.txt

# CLI mode — full run with AI (requires ANTHROPIC_API_KEY)
ANTHROPIC_API_KEY=sk-ant-... python main.py

# CLI mode — RSS only, no AI
python main.py --sin-ia

# Help
python main.py --ayuda

# Flask server
ANTHROPIC_API_KEY=sk-ant-... python app.py
# Then visit http://localhost:5000
```

Output file for CLI mode: `noticias.html` (opened in browser automatically, gitignored).

## Deployment (Render.com)

Configured via `render.yaml`. Free tier, Frankfurt region, Python environment.

- Build: `pip install -r requirements.txt`
- Start: `python app.py`
- Set `ANTHROPIC_API_KEY` manually in the Render Dashboard (after fixing the migration)
- Optional: set `SIN_IA=1` for RSS-only mode (no API costs)
- Note: free tier sleeps after 15 min of inactivity; use cron-job.org to ping `/regenerar` and keep it alive

## Development conventions

- **Language**: project UI and comments are in Spanish; code identifiers are Spanish (e.g. `obtener_todas_las_noticias`, `analizar_todas_las_noticias`)
- **Module responsibility**: each module has a single clear responsibility; do not cross-import logic (e.g. don't put rendering logic in analyzer.py)
- **Parallelism**: fetcher uses up to 12 workers; analyzer uses up to 3 (rate-limit aware); keep these separate
- **AI calls**: always batch at the category level, never one call per article
- **Error handling**: AI failures are graceful — articles fall back to `sesgo_ia="desconocido"` and a placeholder `critica`; the pipeline always produces HTML even if AI is unavailable
- **HTML generation**: all CSS is inline in `renderer.py`; the output must be a single self-contained file with no external assets
- **No tests**: the project has no test suite; verify changes manually with `--sin-ia` first, then with AI enabled

## Dependencies

```
flask>=3.0.0        # web server
feedparser>=6.0.11  # RSS parsing
requests>=2.31.0    # HTTP (used by feedparser internally)
anthropic           # Claude API (not in requirements.txt yet — add it)
```

Note: `anthropic` is used by `analyzer.py` and `synthesizer.py` but is **missing from `requirements.txt`**. Add `anthropic>=0.25.0` to `requirements.txt` as part of completing the Gemini → Claude migration.
