"""Pestaña Para leer — lista de artículos guardados (gestionada por JS/localStorage)."""

TAB_ID    = "para-leer"
TAB_LABEL = "Para leer"
TAB_ICON  = "★"


def render(**_) -> str:
    return """
<div class="para-leer-header">
  <h2>Para leer</h2>
  <p id="para-leer-desc">Artículos guardados con &#9733; — se conservan entre sesiones</p>
</div>
<div id="para-leer-contenido">
  <div class="para-leer-empty">
    Todav&#237;a no has guardado ning&#250;n art&#237;culo.<br>
    Haz clic en &#9733; en cualquier tarjeta para a&#241;adirlo aqu&#237;.
  </div>
</div>"""
