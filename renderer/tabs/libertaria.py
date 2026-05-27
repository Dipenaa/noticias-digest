"""Pestaña Prensa Libertaria — fuentes anarquistas, libertarias y de contrainformación."""

from renderer.components.tarjeta import tarjeta
from renderer.components.badges import leyenda as _leyenda

TAB_ID    = "libertaria"
TAB_LABEL = "&#9889; Prensa Libertaria"
TAB_ICON  = "⚡"


def _seccion(categoria: str, articulos: list[dict], analisis_txt: str,
             verificados: frozenset = frozenset()) -> str:
    id_seccion = categoria.lower().replace(" ", "-")

    if articulos:
        tarjetas  = "\n".join(tarjeta(a, verificados, i) for i, a in enumerate(articulos))
        contenido = f'<div class="grid">{tarjetas}</div>'
    else:
        contenido = '<p class="sin-articulos">No se encontraron artículos.</p>'

    analisis_html = ""
    if analisis_txt:
        analisis_html = f"""
<div class="analisis-general">
  <div class="analisis-general-titulo">🔍 Análisis crítico de la sección</div>
  <p>{analisis_txt}</p>
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


def render(alternativas: dict[str, list[dict]] | None = None,
           analisis_alt: dict[str, str] | None = None,
           verificados: frozenset = frozenset(), **_) -> str:
    alts    = alternativas or {}
    an_alt  = analisis_alt or {}

    if not alts or not any(alts.values()):
        return '<p class="sin-articulos" style="padding:3rem 0;text-align:center">No se encontraron artículos en fuentes alternativas.</p>'

    secciones = "\n".join(
        _seccion(cat, arts, an_alt.get(cat, ""), verificados)
        for cat, arts in alts.items()
    )

    aviso = """<div class="libertaria-header">
  <strong>⚡ Prensa Libertaria y Contrainformación</strong>
  Fuentes anarquistas, libertarias y de contrainformación. Perspectivas
  críticas con el orden establecido, el Estado y el capitalismo.
  Como en el resto del digest, el análisis de sesgo es orientativo.
</div>"""

    return aviso + "\n" + secciones
