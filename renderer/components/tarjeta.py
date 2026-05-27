"""Tarjetas de artículo: normal, destacada, asombro y síntesis."""

import html as _html

from renderer.components.badges import badge, badge_sentimiento, badge_novedad


def _escape(articulo: dict, campos: list[str]) -> dict:
    return {k: _html.escape(str(articulo.get(k) or ""), quote=True) for k in campos}


def tarjeta(articulo: dict, verificados: frozenset = frozenset(), orden: int = 0) -> str:
    sesgo_fuente = articulo.get("sesgo_fuente") or "desconocido"
    sesgo_ia     = articulo.get("sesgo_ia")     or "desconocido"
    sentimiento  = articulo.get("sentimiento")  or ""
    critica      = (articulo.get("critica") or "").strip()
    critica_html = (
        f'<div class="critica"><span class="critica-icono">💡</span>{critica}</div>'
        if critica else ""
    )
    verified_html = (
        '<span class="badge-verified" title="Confirmado por múltiples fuentes de distinto sesgo">&#10003; Multi-fuente</span>'
        if articulo.get("enlace") in verificados else ""
    )
    novedad_html = badge_novedad(articulo)
    search_data  = f'{articulo["titulo"].lower()} {articulo["fuente"].lower()} {(articulo.get("resumen") or "").lower()}'
    da = _escape(articulo, ["titulo", "fuente", "fecha", "enlace", "resumen", "sentimiento"])
    da["critica"]   = _html.escape(critica, quote=True)
    importante = "true" if articulo.get("importante") else "false"

    return f"""
<div class="tarjeta"
     data-search="{_html.escape(search_data, quote=True)}"
     data-sesgo-fuente="{sesgo_fuente}" data-sesgo-ia="{sesgo_ia}"
     data-titulo="{da['titulo']}" data-fuente="{da['fuente']}"
     data-fecha="{da['fecha']}"   data-enlace="{da['enlace']}"
     data-resumen="{da['resumen']}" data-critica="{da['critica']}"
     data-sentimiento="{da['sentimiento']}"
     data-importante="{importante}" data-order="{orden}"
     onclick="if(!event.target.closest('a,.bookmark-btn'))abrirArticulo(this)">
  <div class="tarjeta-meta">
    <div class="fuente-bloque">
      <span class="fuente-nombre">{articulo["fuente"]}</span>
      <span class="fecha">{articulo["fecha"]}</span>
    </div>
    <div class="badges">
      <span class="badge-etiqueta">Fuente:</span>
      {badge(sesgo_fuente)}
      <span class="badge-etiqueta">IA:</span>
      {badge(sesgo_ia)}
      {badge_sentimiento(sentimiento)}
      {verified_html}
      {novedad_html}
      <button class="bookmark-btn" title="Guardar para leer"
              data-enlace="{da['enlace']}" data-titulo="{da['titulo']}"
              data-fuente="{da['fuente']}" data-fecha="{da['fecha']}"
              onclick="toggleBookmark(event,this)">&#9733;</button>
    </div>
  </div>
  <div class="titulo">
    <a href="{articulo['enlace']}" target="_blank" rel="noopener noreferrer">
      {articulo["titulo"]}
    </a>
  </div>
  {critica_html}
</div>"""


def tarjeta_destacada(articulo: dict, categoria: str,
                      verificados: frozenset = frozenset()) -> str:
    sesgo_fuente = articulo.get("sesgo_fuente") or "desconocido"
    sesgo_ia     = articulo.get("sesgo_ia")     or "desconocido"
    sentimiento  = articulo.get("sentimiento")  or ""
    critica      = (articulo.get("critica") or "").strip()
    critica_html = (
        f'<div class="critica"><span class="critica-icono">💡</span>{critica}</div>'
        if critica else ""
    )
    verified_html = (
        '<span class="badge-verified">&#10003; Multi-fuente</span>'
        if articulo.get("enlace") in verificados else ""
    )
    novedad_html  = badge_novedad(articulo)
    search_data   = f'{articulo["titulo"].lower()} {articulo["fuente"].lower()} {categoria.lower()}'
    da = _escape(articulo, ["titulo", "fuente", "fecha", "enlace", "resumen", "sentimiento"])
    da["critica"]   = _html.escape(critica, quote=True)
    da["categoria"] = _html.escape(categoria, quote=True)

    return f"""
<div class="tarjeta-destacada"
     data-search="{_html.escape(search_data, quote=True)}"
     data-sesgo-fuente="{sesgo_fuente}" data-sesgo-ia="{sesgo_ia}"
     data-titulo="{da['titulo']}"   data-fuente="{da['fuente']}"
     data-fecha="{da['fecha']}"     data-enlace="{da['enlace']}"
     data-resumen="{da['resumen']}" data-critica="{da['critica']}"
     data-categoria="{da['categoria']}" data-sentimiento="{da['sentimiento']}"
     onclick="if(!event.target.closest('a,.bookmark-btn'))abrirArticulo(this)">
  <div class="tarjeta-meta">
    <div class="fuente-bloque">
      <span class="categoria-label">{categoria}</span>
      <span class="fuente-nombre">{articulo["fuente"]}</span>
      <span class="fecha">{articulo["fecha"]}</span>
    </div>
    <div class="badges">
      <span class="badge-etiqueta">Fuente:</span>
      {badge(sesgo_fuente)}
      <span class="badge-etiqueta">IA:</span>
      {badge(sesgo_ia)}
      {badge_sentimiento(sentimiento)}
      {verified_html}
      {novedad_html}
      <button class="bookmark-btn" title="Guardar para leer"
              data-enlace="{da['enlace']}" data-titulo="{da['titulo']}"
              data-fuente="{da['fuente']}" data-fecha="{da['fecha']}"
              onclick="toggleBookmark(event,this)">&#9733;</button>
    </div>
  </div>
  <div class="titulo">
    <a href="{articulo['enlace']}" target="_blank" rel="noopener noreferrer">
      {articulo["titulo"]}
    </a>
  </div>
  {critica_html}
</div>"""


def tarjeta_asombro(articulo: dict) -> str:
    score        = int(articulo.get("asombro") or 0)
    razon        = (articulo.get("asombro_razon") or articulo.get("critica") or "").strip()
    categoria    = articulo.get("_cat", "")
    sesgo_ia     = articulo.get("sesgo_ia") or "desconocido"
    sesgo_fuente = articulo.get("sesgo_fuente") or "desconocido"
    importante   = "true" if articulo.get("importante") else "false"
    estrellas    = "✦" * score + "✧" * (3 - score)
    search_data  = f'{articulo["titulo"].lower()} {articulo["fuente"].lower()}'
    da = _escape(articulo, ["titulo", "fuente", "fecha", "enlace", "resumen", "sentimiento"])
    da["critica"] = _html.escape(articulo.get("critica") or "", quote=True)

    razon_html    = f'<p class="asombro-razon">💡 {_html.escape(razon)}</p>' if razon else ""
    resumen_corto = _html.escape((articulo.get("resumen") or "")[:220])

    return f"""
<div class="asombro-card"
     data-search="{_html.escape(search_data, quote=True)}"
     data-sesgo-fuente="{sesgo_fuente}" data-sesgo-ia="{sesgo_ia}"
     data-titulo="{da['titulo']}" data-fuente="{da['fuente']}"
     data-fecha="{da['fecha']}" data-enlace="{da['enlace']}"
     data-resumen="{da['resumen']}" data-critica="{da['critica']}"
     data-sentimiento="{da['sentimiento']}"
     data-importante="{importante}" data-order="0"
     onclick="if(!event.target.closest('a,.bookmark-btn'))abrirArticulo(this)">
  <div class="asombro-score">{estrellas}</div>
  <span class="asombro-cat">{_html.escape(categoria)}</span>
  <h3 class="asombro-titulo">
    <a href="{_html.escape(articulo['enlace'])}" target="_blank" rel="noopener"
       onclick="event.stopPropagation()">{_html.escape(articulo['titulo'])}</a>
  </h3>
  <div class="asombro-fuente">{_html.escape(articulo['fuente'])} · {_html.escape(articulo['fecha'])}</div>
  {razon_html}
  <p class="asombro-resumen">{resumen_corto}</p>
  <button class="bookmark-btn" title="Guardar para leer"
          data-enlace="{da['enlace']}" data-titulo="{da['titulo']}"
          data-fuente="{da['fuente']}" data-fecha="{da['fecha']}"
          onclick="toggleBookmark(event,this)">&#9733;</button>
</div>"""


def tarjeta_sintesis(grupo: dict) -> str:
    """Tarjeta de síntesis con comparador de ángulos por sesgo político."""
    articulos = grupo["articulos"]
    n = len(articulos)

    _izq = ["izquierda", "centro-izquierda"]
    _der = ["centro-derecha", "derecha"]
    cols = {
        "Izquierda":   [a for a in articulos if a.get("sesgo_fuente") in _izq],
        "Centro":      [a for a in articulos if a.get("sesgo_fuente") == "centro"],
        "Derecha":     [a for a in articulos if a.get("sesgo_fuente") in _der],
        "Alternativa": [a for a in articulos if a.get("alt")],
    }
    cols_con_datos = {k: v for k, v in cols.items() if v}
    hay_comparador = len(cols_con_datos) >= 2

    fuentes_html = ""
    for art in articulos:
        alt_badge = '<span class="sintesis-fuente-alt">ALT</span>' if art.get("alt") else ""
        fuentes_html += f"""
<div class="sintesis-fuente-item">
  <span class="sintesis-fuente-nombre">{art["fuente"]}</span>
  {badge(art.get("sesgo_fuente") or "desconocido")}
  {alt_badge}
  <a class="sintesis-fuente-link" href="{art['enlace']}" target="_blank" rel="noopener noreferrer">
    {art["titulo"]}
  </a>
</div>"""

    angulos_html = ""
    if hay_comparador:
        columnas = ""
        for nombre, arts in cols_con_datos.items():
            items = "".join(
                f'<div class="angulo-item"><a href="{a["enlace"]}" target="_blank" rel="noopener noreferrer">{a["titulo"]}</a></div>'
                for a in arts
            )
            columnas += f'<div class="angulo-col"><div class="angulo-label">{nombre}</div>{items}</div>'
        angulos_html = f'<div class="angulos-grid">{columnas}</div>'

    comparador_badge = (
        '<span style="font-size:.6rem;color:#a78bfa;font-weight:600">&#9670; Comparador activo</span>'
        if hay_comparador else ""
    )

    return f"""
<div class="sintesis-card" data-search="{grupo['titulo'].lower()} {' '.join(a['fuente'].lower() for a in articulos)}">
  <div class="sintesis-meta">
    <span class="sintesis-fuentes-count">{n} fuente{"s" if n != 1 else ""}</span>
    {comparador_badge}
  </div>
  <div class="sintesis-titulo">{grupo["titulo"]}</div>
  <div class="sintesis-texto">{grupo["sintesis"]}</div>
  {angulos_html if hay_comparador else f'<div class="sintesis-fuentes">{fuentes_html}</div>'}
</div>"""
