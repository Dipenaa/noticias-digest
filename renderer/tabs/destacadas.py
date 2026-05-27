"""Pestaña Destacadas — artículos marcados por Claude como importantes."""

from renderer.components.tarjeta import tarjeta_destacada

TAB_ID    = "destacadas"
TAB_LABEL = "Destacadas"
TAB_ICON  = "⭐"


def render(noticias: dict[str, list[dict]],
           verificados: frozenset = frozenset(), **_) -> str:
    seleccionados: list[tuple[str, dict]] = []

    for categoria, articulos in noticias.items():
        importantes = [a for a in articulos if a.get("importante")]
        if importantes:
            seleccionados.extend((categoria, a) for a in importantes)
        elif articulos:
            seleccionados.append((categoria, articulos[0]))

    if not seleccionados:
        return '<p class="sin-destacadas">No hay artículos destacados disponibles.</p>'

    cards = "\n".join(tarjeta_destacada(a, cat, verificados) for cat, a in seleccionados)
    fuente_label = (
        "seleccionadas por Claude"
        if any(a.get("importante") for arts in noticias.values() for a in arts)
        else "primera noticia de cada sección (ejecuta con análisis IA para selección automática)"
    )

    return f"""
<div class="destacadas-header">
  <h2>Noticias destacadas</h2>
  <p>{len(seleccionados)} artículo(s) · {fuente_label}</p>
</div>
<div class="grid-destacadas">
{cards}
</div>"""
