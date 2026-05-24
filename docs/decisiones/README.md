# Decisiones

Registro de decisiones técnicas y de producto. Qué se eligió, alternativas descartadas, y por qué.

Formato sugerido: `YYYY-MM-DD-nombre-decision.md`

## Decisiones ya tomadas (resumidas)
- **Redis + disco fallback** — Upstash Redis en producción, JSON local como fallback cuando no hay REDIS_URL
- **Haiku para análisis masivo, Sonnet para síntesis** — 20x más barato; calidad suficiente para análisis por artículo
- **Prompt caching en analyzer.py** — ~80% menos tokens en ciclos normales donde el system prompt no cambia
- **CSS en styles.py separado** — permite iterar diseño con preview.py sin gastar tokens en Claude
