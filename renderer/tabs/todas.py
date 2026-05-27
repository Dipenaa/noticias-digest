"""Pestaña Todas — secciones completas con todas las noticias."""

from renderer.components.badges import leyenda
from renderer.components.tarjeta import tarjeta

TAB_ID    = "todas"
TAB_LABEL = "Todas las noticias"
TAB_ICON  = "📰"


def _seccion(categoria: str, articulos: list[dict], analisis: str,
             verificados: frozenset = frozenset()) -> str:
    id_seccion = categoria.lower().replace(" ", "-")

    if articulos:
        tarjetas  = "\n".join(tarjeta(a, verificados, i) for i, a in enumerate(articulos))
        contenido = f'<div class="grid">{tarjetas}</div>'
    else:
        contenido = '<p class="sin-articulos">No se encontraron artículos.</p>'

    analisis_html = ""
    if analisis:
        analisis_html = f"""
<div class="analisis-general">
  <div class="analisis-general-titulo">🔍 Análisis crítico de la sección</div>
  <p>{analisis}</p>
</div>"""

    return f"""
<section id="{id_seccion}" class="seccion">
  <div class="seccion-header">
    <div class="seccion-acento"></div>
    <h2 class="seccion-titulo">{categoria}</h2>
  </div>
  {analisis_html}
  {contenido}
</section>"""


def nav(categorias: list[str]) -> str:
    """Barra de navegación de categorías (solo visible en pestaña Todas)."""
    links = "".join(
        f'<a href="#{cat.lower().replace(" ", "-")}">{cat}</a>'
        for cat in categorias
    )
    return f'<nav id="cat-nav">{links}</nav>'


def render(noticias: dict[str, list[dict]],
           analisis: dict[str, str],
           verificados: frozenset = frozenset(), **_) -> str:
    secciones = "\n".join(
        _seccion(cat, arts, analisis.get(cat, ""), verificados)
        for cat, arts in noticias.items()
    )
    return leyenda() + secciones
