"""Pestaña Asombro — artículos con alto factor de fascinación (asombro ≥ 2)."""

from renderer.components.tarjeta import tarjeta_asombro

TAB_ID    = "asombro"
TAB_LABEL = "&#10024; Asombro"
TAB_ICON  = "✨"


def render(noticias: dict[str, list[dict]],
           alternativas: dict[str, list[dict]] | None = None, **_) -> tuple[str, int]:
    """Devuelve (html, n_articulos)."""
    candidatos: list[dict] = []

    for cat, arts in noticias.items():
        for a in arts:
            if int(a.get("asombro") or 0) >= 2:
                candidatos.append({**a, "_cat": cat})

    for cat, arts in (alternativas or {}).items():
        for a in arts:
            if int(a.get("asombro") or 0) >= 2:
                candidatos.append({**a, "_cat": cat})

    candidatos.sort(key=lambda x: int(x.get("asombro") or 0), reverse=True)

    if not candidatos:
        return ("""
<div class="asombro-header">
  <h2>✨ Asombro</h2>
  <p>Hoy el mundo no ha dicho nada especialmente fascinante,<br>
     o todavía no hay análisis de IA disponible.</p>
</div>
<div class="asombro-empty">
  <div class="asombro-empty-icon">🌍</div>
  <p>Vuelve más tarde o activa la API de Claude para descubrir<br>qué hay de fascinante hoy.</p>
</div>""", 0)

    cards = "\n".join(tarjeta_asombro(a) for a in candidatos)
    return (f"""
<div class="asombro-header">
  <h2>✨ Asombro</h2>
  <p>No las noticias más importantes del día — las que más te hacen pensar.<br>
     Artículos que revelan algo genuinamente fascinante sobre el mundo.</p>
</div>
<div class="asombro-grid">
{cards}
</div>""", len(candidatos))
