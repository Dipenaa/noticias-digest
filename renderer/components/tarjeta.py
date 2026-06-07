"""Tarjetas de artículo: normal, destacada, asombro y síntesis."""

import html as _html
import json as _json

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
    titulo_mostrar = articulo.get("titulo_es") or articulo["titulo"]
    search_data  = f'{titulo_mostrar.lower()} {articulo["fuente"].lower()} {(articulo.get("resumen") or "").lower()}'
    da = _escape(articulo, ["fuente", "fecha", "enlace", "resumen", "sentimiento"])
    da["titulo"]  = _html.escape(titulo_mostrar, quote=True)
    da["critica"] = _html.escape(critica, quote=True)
    importante = "true" if articulo.get("importante") else "false"
    resumen_html = (
        f'<p class="resumen">{_html.escape(articulo.get("resumen") or "")}</p>'
        if articulo.get("resumen") else ""
    )

    asombro = int(articulo.get("asombro") or 0)
    asombro_razon = _html.escape(articulo.get("asombro_razon") or "", quote=True)
    novedad = int(articulo.get("novedad") or articulo.get("asombro") or 2)
    tags = articulo.get("tags") or []
    tags_json = _html.escape(_json.dumps(tags, ensure_ascii=False), quote=True)
    pregunta = _html.escape(str(articulo.get("pregunta") or ""), quote=True)
    tags_html = ""
    if tags:
        chips = "".join(
            f'<button class="article-tag" onclick="event.stopPropagation();filtrarTag(this)">{_html.escape(t)}</button>'
            for t in tags
        )
        tags_html = f'<div class="article-tags">{chips}</div>'
    return f"""
<div class="tarjeta"
     data-search="{_html.escape(search_data, quote=True)}"
     data-sesgo-fuente="{sesgo_fuente}" data-sesgo-ia="{sesgo_ia}"
     data-titulo="{da['titulo']}" data-fuente="{da['fuente']}"
     data-fecha="{da['fecha']}"   data-enlace="{da['enlace']}"
     data-resumen="{da['resumen']}" data-critica="{da['critica']}"
     data-sentimiento="{da['sentimiento']}"
     data-asombro="{asombro}" data-asombro-razon="{asombro_razon}"
     data-novedad="{novedad}" data-tags="{tags_json}" data-pregunta="{pregunta}"
     data-importante="{importante}" data-order="{orden}"
     onclick="if(!event.target.closest('a,.bookmark-btn,.leer-btn,.article-tag'))abrirArticulo(this)">
  <div class="tarjeta-meta">
    <div class="fuente-bloque">
      <span class="fuente-nombre">{articulo["fuente"]}</span>
      <span class="fecha">{articulo["fecha"]}</span>
    </div>
    <div class="badges">
      <span class="badge-etiqueta">Fuente:</span>
      {badge(sesgo_fuente)}
      {badge_sentimiento(sentimiento)}
      {verified_html}
      {novedad_html}
      <button class="leer-btn" title="Escuchar" onclick="leerArticuloTarjeta(event,this)">🔊</button>
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
  {resumen_html}
  {critica_html}
  {tags_html}
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
    titulo_mostrar = articulo.get("titulo_es") or articulo["titulo"]
    search_data   = f'{titulo_mostrar.lower()} {articulo["fuente"].lower()} {categoria.lower()}'
    da = _escape(articulo, ["fuente", "fecha", "enlace", "resumen", "sentimiento"])
    da["titulo"]    = _html.escape(titulo_mostrar, quote=True)
    da["critica"]   = _html.escape(critica, quote=True)
    da["categoria"] = _html.escape(categoria, quote=True)
    resumen_html = (
        f'<p class="resumen">{_html.escape(articulo.get("resumen") or "")}</p>'
        if articulo.get("resumen") else ""
    )

    asombro = int(articulo.get("asombro") or 0)
    asombro_razon = _html.escape(articulo.get("asombro_razon") or "", quote=True)
    novedad = int(articulo.get("novedad") or articulo.get("asombro") or 2)
    tags = articulo.get("tags") or []
    tags_json = _html.escape(_json.dumps(tags, ensure_ascii=False), quote=True)
    pregunta = _html.escape(str(articulo.get("pregunta") or ""), quote=True)
    tags_html = ""
    if tags:
        chips = "".join(
            f'<button class="article-tag" onclick="event.stopPropagation();filtrarTag(this)">{_html.escape(t)}</button>'
            for t in tags
        )
        tags_html = f'<div class="article-tags">{chips}</div>'
    return f"""
<div class="tarjeta-destacada"
     data-search="{_html.escape(search_data, quote=True)}"
     data-sesgo-fuente="{sesgo_fuente}" data-sesgo-ia="{sesgo_ia}"
     data-titulo="{da['titulo']}"   data-fuente="{da['fuente']}"
     data-fecha="{da['fecha']}"     data-enlace="{da['enlace']}"
     data-resumen="{da['resumen']}" data-critica="{da['critica']}"
     data-categoria="{da['categoria']}" data-sentimiento="{da['sentimiento']}"
     data-asombro="{asombro}" data-asombro-razon="{asombro_razon}"
     data-novedad="{novedad}" data-tags="{tags_json}" data-pregunta="{pregunta}"
     onclick="if(!event.target.closest('a,.bookmark-btn,.leer-btn,.article-tag'))abrirArticulo(this)">
  <div class="tarjeta-meta">
    <div class="fuente-bloque">
      <span class="categoria-label">{categoria}</span>
      <span class="fuente-nombre">{articulo["fuente"]}</span>
      <span class="fecha">{articulo["fecha"]}</span>
    </div>
    <div class="badges">
      <span class="badge-etiqueta">Fuente:</span>
      {badge(sesgo_fuente)}
      {badge_sentimiento(sentimiento)}
      {verified_html}
      {novedad_html}
      <button class="leer-btn" title="Escuchar" onclick="leerArticuloTarjeta(event,this)">🔊</button>
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
  {resumen_html}
  {critica_html}
  {tags_html}
</div>"""


def tarjeta_asombro(articulo: dict) -> str:
    score        = int(articulo.get("asombro") or 0)
    razon        = (articulo.get("asombro_razon") or articulo.get("critica") or "").strip()
    categoria    = articulo.get("_cat", "")
    sesgo_ia     = articulo.get("sesgo_ia") or "desconocido"
    sesgo_fuente = articulo.get("sesgo_fuente") or "desconocido"
    importante   = "true" if articulo.get("importante") else "false"
    estrellas    = "✦" * score + "✧" * (3 - score)
    titulo_mostrar = articulo.get("titulo_es") or articulo["titulo"]
    search_data  = f'{titulo_mostrar.lower()} {articulo["fuente"].lower()}'
    da = _escape(articulo, ["fuente", "fecha", "enlace", "resumen", "sentimiento"])
    da["titulo"] = _html.escape(titulo_mostrar, quote=True)
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
     onclick="if(!event.target.closest('a,.bookmark-btn,.leer-btn'))abrirArticulo(this)">
  <div class="asombro-score">{estrellas}</div>
  <span class="asombro-cat">{_html.escape(categoria)}</span>
  <h3 class="asombro-titulo">
    <a href="{_html.escape(articulo['enlace'])}" target="_blank" rel="noopener"
       onclick="event.stopPropagation()">{_html.escape(articulo['titulo'])}</a>
  </h3>
  <div class="asombro-fuente">{_html.escape(articulo['fuente'])} · {_html.escape(articulo['fecha'])}</div>
  {razon_html}
  <p class="asombro-resumen">{resumen_corto}</p>
  <button class="leer-btn" title="Escuchar" onclick="leerArticuloTarjeta(event,this)">🔊</button>
  <button class="bookmark-btn" title="Guardar para leer"
          data-enlace="{da['enlace']}" data-titulo="{da['titulo']}"
          data-fuente="{da['fuente']}" data-fecha="{da['fecha']}"
          onclick="toggleBookmark(event,this)">&#9733;</button>
</div>"""


def _edad_info(fecha_str: str) -> tuple[str, str]:
    """Devuelve (etiqueta, clase_css) según la antigüedad de un artículo."""
    from datetime import datetime
    try:
        dias = (datetime.now().date() - datetime.strptime(fecha_str[:10], "%Y-%m-%d").date()).days
    except Exception:
        return "", "edad-antigua"
    if dias == 0:
        return "hoy", "edad-hoy"
    if dias == 1:
        return "ayer", "edad-ayer"
    return f"{dias}d", "edad-antigua"


def tarjeta_sintesis(grupo: dict) -> str:
    """Tarjeta de síntesis con comparador de ángulos por sesgo político e indicadores de frescura."""
    from datetime import datetime

    # Ordenar artículos del más reciente al más antiguo
    articulos = sorted(
        grupo["articulos"],
        key=lambda a: a.get("fecha", ""),
        reverse=True,
    )
    n = len(articulos)

    # Calcular frescura del grupo
    fechas = [a.get("fecha", "") for a in articulos if a.get("fecha")]
    max_fecha = max(fechas) if fechas else ""
    try:
        dias_grupo = (datetime.now().date() - datetime.strptime(max_fecha[:10], "%Y-%m-%d").date()).days
    except Exception:
        dias_grupo = 99

    if dias_grupo == 0:
        frescura_label, frescura_clase = "activo hoy", "sintesis-fresco"
    elif dias_grupo == 1:
        frescura_label, frescura_clase = "activo ayer", "sintesis-reciente"
    else:
        frescura_label, frescura_clase = f"hace {dias_grupo}d", "sintesis-archivo"

    card_clase = "sintesis-card en-archivo" if dias_grupo >= 2 else "sintesis-card"

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
        etiqueta, clase = _edad_info(art.get("fecha", ""))
        edad_html = f'<span class="sintesis-edad {clase}">{etiqueta}</span>' if etiqueta else ""
        fuentes_html += f"""
<div class="sintesis-fuente-item">
  <span class="sintesis-fuente-nombre">{art["fuente"]}</span>
  {badge(art.get("sesgo_fuente") or "desconocido")}
  {alt_badge}
  {edad_html}
  <a class="sintesis-fuente-link" href="{art['enlace']}" target="_blank" rel="noopener noreferrer">
    {art["titulo"]}
  </a>
</div>"""

    angulos_html = ""
    if hay_comparador:
        columnas = ""
        for nombre, arts in cols_con_datos.items():
            items = "".join(
                f'<div class="angulo-item">'
                f'<span class="angulo-edad {_edad_info(a.get("fecha",""))[1]}">{_edad_info(a.get("fecha",""))[0]}</span>'
                f'<a href="{a["enlace"]}" target="_blank" rel="noopener noreferrer">{a["titulo"]}</a>'
                f'</div>'
                for a in arts
            )
            columnas += f'<div class="angulo-col" data-col="{nombre.lower()}"><div class="angulo-label">{nombre}</div>{items}</div>'
        angulos_html = f'<div class="angulos-grid">{columnas}</div>'

    comparador_badge = (
        '<span style="font-size:.6rem;color:#a78bfa;font-weight:600">&#9670; Comparador activo</span>'
        if hay_comparador else ""
    )

    # Perspectivas extra (fuentes dinámicas de Google News — B-lite, sin IA)
    extra = grupo.get("perspectivas_extra") or []
    perspectivas_html = ""
    if extra:
        items = "".join(
            f"""<a class="persp-item" href="{a['enlace']}" target="_blank" rel="noopener noreferrer">
  <span class="persp-fuente">{_html.escape(a['fuente'])}</span>
  <span class="badges">{badge(a.get('sesgo_fuente') or 'desconocido')}</span>
  <span class="persp-titulo">{_html.escape(a['titulo'])}</span>
</a>"""
            for a in extra
        )
        perspectivas_html = f"""
<div class="perspectivas-extra">
  <div class="perspectivas-label">&#127758; M&#225;s perspectivas — medios de todo el mundo sobre esta historia</div>
  {items}
</div>"""

    n_extra = len(extra)
    toggle_label = f"&#9660; {n} fuente{'s' if n != 1 else ''}"
    if n_extra:
        toggle_label += f" + {n_extra} perspectiva{'s' if n_extra != 1 else ''}"

    detalle_primario = angulos_html if hay_comparador else f'<div class="sintesis-fuentes">{fuentes_html}</div>'

    return f"""
<div class="{card_clase}" data-search="{grupo['titulo'].lower()} {' '.join(a['fuente'].lower() for a in articulos)}">
  <div class="sintesis-meta">
    <span class="sintesis-fuentes-count">{n} fuente{"s" if n != 1 else ""}</span>
    <div class="sintesis-meta-right">
      <span class="sintesis-frescura {frescura_clase}">{frescura_label}</span>
      {comparador_badge}
    </div>
  </div>
  <div class="sintesis-titulo">{grupo["titulo"]}</div>
  <div class="sintesis-texto">{grupo["sintesis"]}</div>
  <button class="sintesis-toggle" onclick="toggleSintesis(this)">{toggle_label}</button>
  <div class="sintesis-detalle">
    {detalle_primario}
    {perspectivas_html}
  </div>
</div>"""
