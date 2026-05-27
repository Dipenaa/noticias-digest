"""Pestaña Síntesis — historias cubiertas por múltiples fuentes con perspectivas cruzadas."""

from renderer.components.tarjeta import tarjeta_sintesis

TAB_ID    = "sintesis"
TAB_LABEL = "&#128279; S&#237;ntesis"
TAB_ICON  = "🔗"


def render(grupos_sintesis: list[dict] | None = None, **_) -> str:
    grupos = grupos_sintesis or []

    if not grupos:
        return """<div class="sin-sintesis">
  <h3>Síntesis cruzada</h3>
  <p>Detecta historias que aparecen en múltiples fuentes con perspectivas distintas y las analiza con Claude.</p>
  <p class="sin-sintesis-nota">No se genera automáticamente para ahorrar tokens. Pulsa cuando quieras verla.</p>
  <button id="btn-sintetizar" onclick="generarSintesis()">Generar síntesis con Claude</button>
  <p id="sintesis-estado" style="display:none;margin-top:1rem;font-size:.82rem;color:var(--txt-3)">Analizando… puede tardar 20-30 s</p>
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
