"""Pestaña Síntesis — historias cubiertas por múltiples fuentes con perspectivas cruzadas."""

from renderer.components.tarjeta import tarjeta_sintesis

TAB_ID    = "sintesis"
TAB_LABEL = "Síntesis"
TAB_ICON  = "🔗"


def render(grupos_sintesis: list[dict] | None = None, **_) -> str:
    grupos = grupos_sintesis or []

    if not grupos:
        return """<div class="sin-sintesis">
  <h3>Sin síntesis hoy</h3>
  <p>No se detectaron historias con cobertura cruzada suficiente en este digest.</p>
</div>"""

    cards = "\n".join(tarjeta_sintesis(g) for g in grupos)
    return f"""
<div class="sintesis-header">
  <h2>Síntesis de historias</h2>
  <p>{len(grupos)} historia(s) detectada(s) en múltiples fuentes · perspectivas cruzadas generadas por Claude</p>
</div>
<div class="grid-sintesis">
{cards}
</div>"""
