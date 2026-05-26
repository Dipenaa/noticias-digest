"""
renderer.py — Genera el archivo HTML del digest de noticias.

Construye un documento HTML autocontenido (CSS incluido) con:
  - Cabecera fija con fecha y total de artículos
  - Navegación por sección
  - Leyenda de sesgo
  - Secciones con análisis crítico general + tarjetas de artículos
  - Etiquetas de sesgo (fuente estimada + IA)
  - Caja de crítica por artículo
"""

import html as _html
import json
import os
import webbrowser
from datetime import datetime

from analyzer import COLORES_SESGO
from config import ARCHIVO_SALIDA
from js import _JS


from styles import _CSS

def _safe_url(url: str) -> str:
    """Permite solo URLs http/https para evitar javascript: en hrefs."""
    return url if url.startswith(("https://", "http://")) else "#"


# ---------------------------------------------------------------------------
# Constructores de bloques HTML
# ---------------------------------------------------------------------------

CLASES_SENTIMIENTO = {
    "alarmista": "badge-sent-alarmista",
    "neutral":   "badge-sent-neutral",
    "optimista": "badge-sent-optimista",
}
ICONOS_SENTIMIENTO = {"alarmista": "⚠", "neutral": "◉", "optimista": "✦"}

_LABELS_SESGO = {
    "izquierda":        "IZQ",
    "centro-izquierda": "C·IZQ",
    "centro":           "CTR",
    "centro-derecha":   "C·DER",
    "derecha":          "DER",
    "desconocido":      "?",
}


def _badge(sesgo: str) -> str:
    color = COLORES_SESGO.get(sesgo, COLORES_SESGO["desconocido"])
    label = _LABELS_SESGO.get(sesgo, sesgo.upper())
    return f'<span class="badge" style="background:{color}" title="{sesgo}">{label}</span>'


def _badge_sentimiento(sentimiento: str) -> str:
    if not sentimiento or sentimiento == "neutral":
        return ""
    cls  = CLASES_SENTIMIENTO.get(sentimiento, "badge-sent-neutral")
    icon = ICONOS_SENTIMIENTO.get(sentimiento, "")
    return f'<span class="badge-sent {cls}" title="Tono: {sentimiento}">{icon} {sentimiento.upper()}</span>'


def _tarjeta(articulo: dict, verificados: frozenset = frozenset(), orden: int = 0) -> str:
    sesgo_fuente = articulo.get("sesgo_fuente") or "desconocido"
    sesgo_ia     = articulo.get("sesgo_ia")     or "desconocido"
    sentimiento  = articulo.get("sentimiento")  or ""
    critica      = (articulo.get("critica") or "").strip()
    critica_html = (
        f'<div class="critica"><span class="critica-icono">💡</span>{_html.escape(critica)}</div>'
        if critica else ""
    )
    verified_html = (
        '<span class="badge-verified" title="Confirmado por múltiples fuentes de distinto sesgo">&#10003; Multi-fuente</span>'
        if articulo.get("enlace") in verificados else ""
    )
    novedad_html = _badge_novedad(articulo)
    search_data = f'{articulo["titulo"].lower()} {articulo["fuente"].lower()} {(articulo.get("resumen") or "").lower()}'

    da = {k: _html.escape(str(v), quote=True) for k, v in {
        "titulo":      articulo["titulo"],
        "fuente":      articulo["fuente"],
        "fecha":       articulo["fecha"],
        "enlace":      articulo["enlace"],
        "resumen":     articulo.get("resumen") or "",
        "critica":     critica,
        "sentimiento": sentimiento,
    }.items()}

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
      {_badge(sesgo_fuente)}
      <span class="badge-etiqueta">IA:</span>
      {_badge(sesgo_ia)}
      {_badge_sentimiento(sentimiento)}
      {verified_html}
      {novedad_html}
      <button class="bookmark-btn" title="Guardar para leer"
              data-enlace="{da['enlace']}" data-titulo="{da['titulo']}"
              data-fuente="{da['fuente']}" data-fecha="{da['fecha']}"
              onclick="toggleBookmark(event,this)">&#9733;</button>
    </div>
  </div>
  <div class="titulo">
    <a href="{_safe_url(articulo['enlace'])}" target="_blank" rel="noopener noreferrer">
      {articulo["titulo"]}
    </a>
  </div>
  {critica_html}
</div>"""


def _seccion(categoria: str, articulos: list[dict], analisis: str,
             verificados: frozenset = frozenset()) -> str:
    id_seccion = categoria.lower().replace(" ", "-")

    if articulos:
        tarjetas = "\n".join(_tarjeta(a, verificados, i) for i, a in enumerate(articulos))
        contenido = f'<div class="grid">{tarjetas}</div>'
    else:
        contenido = '<p class="sin-articulos">No se encontraron artículos.</p>'

    analisis_html = ""
    if analisis:
        analisis_html = f"""
<div class="analisis-general">
  <div class="analisis-general-titulo">🔍 Análisis crítico de la sección</div>
  <p>{_html.escape(analisis)}</p>
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


def _leyenda() -> str:
    """Bloque de leyenda con todos los niveles de sesgo y sus colores. Badges son clicables para filtrar."""
    items = []
    for s, color in COLORES_SESGO.items():
        label = _LABELS_SESGO.get(s, s.upper())
        items.append(
            f'<span class="badge" style="background:{color}" '
            f'onclick="filtrarPorSesgo(\'{s}\',this)" '
            f'title="Filtrar por {s}">{label}</span>'
        )
    badges = " ".join(items)
    return f"""
<div class="leyenda">
  <span class="leyenda-titulo">Leyenda:</span>
  <div class="leyenda-items">{badges}</div>
  <span class="leyenda-tip">(clic para filtrar)</span>
  <span class="filtro-aviso" id="filtro-aviso" style="display:none"></span>
  <button class="filtro-clear-btn" id="filtro-clear" onclick="limpiarFiltro()" style="display:none">✕ Quitar filtro</button>
</div>"""


def _nav(categorias: list[str]) -> str:
    """Barra de navegación de categorías (solo visible en pestaña Todas)."""
    links = "".join(
        f'<a href="#{cat.lower().replace(" ", "-")}">{cat}</a>'
        for cat in categorias
    )
    return f'<nav id="cat-nav">{links}</nav>'


def _featured_card(articulo: dict, categoria: str,
                   verificados: frozenset = frozenset()) -> str:
    sesgo_fuente = articulo.get("sesgo_fuente") or "desconocido"
    sesgo_ia     = articulo.get("sesgo_ia")     or "desconocido"
    sentimiento  = articulo.get("sentimiento")  or ""
    critica      = (articulo.get("critica") or "").strip()
    critica_html = (
        f'<div class="critica"><span class="critica-icono">💡</span>{_html.escape(critica)}</div>'
        if critica else ""
    )
    verified_html = (
        '<span class="badge-verified">&#10003; Multi-fuente</span>'
        if articulo.get("enlace") in verificados else ""
    )
    novedad_html  = _badge_novedad(articulo)
    search_data_d = f'{articulo["titulo"].lower()} {articulo["fuente"].lower()} {categoria.lower()}'

    da = {k: _html.escape(str(v), quote=True) for k, v in {
        "titulo":      articulo["titulo"],
        "fuente":      articulo["fuente"],
        "fecha":       articulo["fecha"],
        "enlace":      articulo["enlace"],
        "resumen":     articulo.get("resumen") or "",
        "critica":     critica,
        "categoria":   categoria,
        "sentimiento": sentimiento,
    }.items()}

    return f"""
<div class="tarjeta-destacada"
     data-search="{_html.escape(search_data_d, quote=True)}"
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
      {_badge(sesgo_fuente)}
      <span class="badge-etiqueta">IA:</span>
      {_badge(sesgo_ia)}
      {_badge_sentimiento(sentimiento)}
      {verified_html}
      {novedad_html}
      <button class="bookmark-btn" title="Guardar para leer"
              data-enlace="{da['enlace']}" data-titulo="{da['titulo']}"
              data-fuente="{da['fuente']}" data-fecha="{da['fecha']}"
              onclick="toggleBookmark(event,this)">&#9733;</button>
    </div>
  </div>
  <div class="titulo">
    <a href="{_safe_url(articulo['enlace'])}" target="_blank" rel="noopener noreferrer">
      {articulo["titulo"]}
    </a>
  </div>
  {critica_html}
</div>"""


def _synthesis_card(grupo: dict) -> str:
    """Tarjeta de síntesis con comparador de ángulos por sesgo político."""
    articulos = grupo["articulos"]
    n = len(articulos)

    # Agrupar artículos por orientación política para el comparador
    _izq = ["izquierda", "centro-izquierda"]
    _der = ["centro-derecha", "derecha"]
    cols = {
        "Izquierda": [a for a in articulos if a.get("sesgo_fuente") in _izq],
        "Centro":    [a for a in articulos if a.get("sesgo_fuente") == "centro"],
        "Derecha":   [a for a in articulos if a.get("sesgo_fuente") in _der],
        "Alternativa": [a for a in articulos if a.get("alt")],
    }
    # Solo mostrar columnas con contenido y quitar ALT si ya sale en otras
    cols_con_datos = {k: v for k, v in cols.items() if v}
    hay_comparador = len(cols_con_datos) >= 2

    # Lista de todas las fuentes (vista clásica)
    fuentes_html = ""
    for art in articulos:
        alt_badge = '<span class="sintesis-fuente-alt">ALT</span>' if art.get("alt") else ""
        fuentes_html += f"""
<div class="sintesis-fuente-item">
  <span class="sintesis-fuente-nombre">{art["fuente"]}</span>
  {_badge(art.get("sesgo_fuente") or "desconocido")}
  {alt_badge}
  <a class="sintesis-fuente-link" href="{_safe_url(art['enlace'])}" target="_blank" rel="noopener noreferrer">
    {art["titulo"]}
  </a>
</div>"""

    # Comparador de ángulos
    angulos_html = ""
    if hay_comparador:
        columnas = ""
        for nombre, arts in cols_con_datos.items():
            items = "".join(
                f'<div class="angulo-item"><a href="{_safe_url(a["enlace"])}" target="_blank" rel="noopener noreferrer">{_html.escape(a["titulo"])}</a></div>'
                for a in arts
            )
            columnas += f'<div class="angulo-col"><div class="angulo-label">{nombre}</div>{items}</div>'
        angulos_html = f'<div class="angulos-grid">{columnas}</div>'

    return f"""
<div class="sintesis-card" data-search="{grupo['titulo'].lower()} {' '.join(a['fuente'].lower() for a in articulos)}">
  <div class="sintesis-meta">
    <span class="sintesis-fuentes-count">{n} fuente{"s" if n != 1 else ""}</span>
    {"" if not hay_comparador else '<span style="font-size:.6rem;color:#a78bfa;font-weight:600">&#9670; Comparador activo</span>'}
  </div>
  <div class="sintesis-titulo">{_html.escape(grupo["titulo"])}</div>
  <div class="sintesis-texto">{_html.escape(grupo["sintesis"])}</div>
  {angulos_html if hay_comparador else f'<div class="sintesis-fuentes">{fuentes_html}</div>'}
</div>"""


def _tab_sintesis(grupos: list[dict]) -> str:
    """Pestaña de síntesis cruzada de historias."""
    if not grupos:
        return """<div class="sin-sintesis">
  <h3>Síntesis cruzada</h3>
  <p>Detecta historias que aparecen en múltiples fuentes con perspectivas distintas y las analiza con Claude.</p>
  <p class="sin-sintesis-nota">La síntesis se genera automáticamente al regenerar el digest.</p>
</div>"""

    cards = "\n".join(_synthesis_card(g) for g in grupos)
    return f"""
<div class="sintesis-header">
  <h2>Síntesis de historias</h2>
  <p>{len(grupos)} historia(s) detectada(s) en múltiples fuentes · perspectivas cruzadas generadas por Claude</p>
</div>
<div class="grid-sintesis">
{cards}
</div>"""


def _tab_libertaria(alternativas: dict[str, list[dict]], analisis_alt: dict[str, str],
                    verificados: frozenset = frozenset()) -> str:
    if not alternativas or not any(alternativas.values()):
        return '<p class="sin-articulos" style="padding:3rem 0;text-align:center">No se encontraron artículos en fuentes alternativas.</p>'

    secciones = "\n".join(
        _seccion(cat, arts, analisis_alt.get(cat, ""), verificados)
        for cat, arts in alternativas.items()
    )

    aviso = """<div class="libertaria-header">
  <strong>⚡ Prensa Libertaria y Contrainformación</strong>
  Fuentes anarquistas, libertarias y de contrainformación. Perspectivas
  críticas con el orden establecido, el Estado y el capitalismo.
  Como en el resto del digest, el análisis de sesgo es orientativo.
</div>"""

    return aviso + "\n" + secciones


def _tab_destacadas(noticias: dict[str, list[dict]],
                    verificados: frozenset = frozenset()) -> str:
    """
    Genera el contenido de la pestaña Destacadas.

    Selección:
      - Si Claude marcó artículos como importantes (importante=True): esos.
      - Fallback (--sin-ia): el primer artículo de cada categoría.
    """
    seleccionados: list[tuple[str, dict]] = []

    for categoria, articulos in noticias.items():
        importantes = [a for a in articulos if a.get("importante")]
        if importantes:
            seleccionados.extend((categoria, a) for a in importantes)
        elif articulos:
            # fallback: primer artículo de la categoría
            seleccionados.append((categoria, articulos[0]))

    if not seleccionados:
        return '<p class="sin-destacadas">No hay artículos destacados disponibles.</p>'

    cards = "\n".join(_featured_card(a, cat, verificados) for cat, a in seleccionados)
    fuente_label = "seleccionadas por Claude" if any(
        a.get("importante") for arts in noticias.values() for a in arts
    ) else "primera noticia de cada sección (ejecuta con análisis IA para selección automática)"

    return f"""
<div class="destacadas-header">
  <h2>Noticias destacadas</h2>
  <p>{len(seleccionados)} artículo(s) · {fuente_label}</p>
</div>
<div class="grid-destacadas">
{cards}
</div>"""


def _tab_para_leer() -> str:
    """Pestaña de lista de lectura (contenido generado íntegramente por JS desde localStorage)."""
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


def _tab_estadisticas(fuentes_fallidas: list[str] | None = None) -> str:
    """Pestaña de estadísticas de sesgo y cobertura (datos calculados por JS en cliente)."""
    bloque_fallidas = ""
    if fuentes_fallidas:
        items = "".join(f"<li>{n}</li>" for n in fuentes_fallidas)
        bloque_fallidas = f"""
<div class="stats-fallidas">
  <strong>⚠ Fuentes sin artículos en esta generación ({len(fuentes_fallidas)})</strong>
  <ul>{items}</ul>
  <span>Puede ser una caída temporal del feed o URL incorrecta.</span>
</div>"""

    return f"""
<div class="stats-header">
  <h2>Estadísticas del digest</h2>
  <p>Distribución ideológica, cobertura por fuente y diversidad — calculado en tiempo real</p>
</div>
{bloque_fallidas}
<div class="stats-kpi-row">
  <div class="stat-kpi">
    <div class="stat-kpi-valor" id="kpi-total">—</div>
    <div class="stat-kpi-label">artículos totales</div>
  </div>
  <div class="stat-kpi">
    <div class="stat-kpi-valor" id="kpi-fuentes">—</div>
    <div class="stat-kpi-label">fuentes distintas</div>
  </div>
  <div class="stat-kpi">
    <div class="stat-kpi-valor" id="kpi-diversidad">—</div>
    <div class="stat-kpi-label">diversidad ideológica</div>
  </div>
  <div class="stat-kpi">
    <div class="stat-kpi-valor" id="kpi-sesgos">—</div>
    <div class="stat-kpi-label">sesgos detectados</div>
  </div>
</div>

<div class="stats-grid">
  <div class="stat-card">
    <div class="stat-card-title">Sesgo por fuente (siempre disponible)</div>
    <div id="stat-sesgo-chart"><span style="color:var(--txt-3);font-size:.8rem">Calculando…</span></div>
  </div>
  <div class="stat-card">
    <div class="stat-card-title">Sesgo según análisis IA</div>
    <div id="stat-sesgo-ia-chart"><span style="color:var(--txt-3);font-size:.8rem">Calculando…</span></div>
  </div>
  <div class="stat-card">
    <div class="stat-card-title">Top fuentes por volumen</div>
    <div id="stat-fuentes-chart"><span style="color:var(--txt-3);font-size:.8rem">Calculando…</span></div>
  </div>
  <div class="stat-card">
    <div class="stat-card-title">Artículos por categoría</div>
    <div id="stat-cat-chart"><span style="color:var(--txt-3);font-size:.8rem">Calculando…</span></div>
  </div>
</div>"""


# ---------------------------------------------------------------------------
# Punto de entrada público
# ---------------------------------------------------------------------------

def _asombro_card(articulo: dict) -> str:
    score        = int(articulo.get("asombro") or 0)
    razon        = (articulo.get("asombro_razon") or articulo.get("critica") or "").strip()
    categoria    = articulo.get("_cat", "")
    sesgo_ia     = articulo.get("sesgo_ia") or "desconocido"
    sesgo_fuente = articulo.get("sesgo_fuente") or "desconocido"
    importante   = "true" if articulo.get("importante") else "false"
    estrellas    = "✦" * score + "✧" * (3 - score)
    search_data  = f'{articulo["titulo"].lower()} {articulo["fuente"].lower()}'

    da = {k: _html.escape(str(v), quote=True) for k, v in {
        "titulo":      articulo["titulo"],
        "fuente":      articulo["fuente"],
        "fecha":       articulo["fecha"],
        "enlace":      articulo["enlace"],
        "resumen":     articulo.get("resumen") or "",
        "critica":     articulo.get("critica") or "",
        "sentimiento": articulo.get("sentimiento") or "",
    }.items()}

    razon_html = f'<p class="asombro-razon">💡 {_html.escape(razon)}</p>' if razon else ""
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
    <a href="{_safe_url(articulo['enlace'])}" target="_blank" rel="noopener"
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


def _tab_asombro(
    noticias:     dict[str, list[dict]],
    alternativas: dict[str, list[dict]],
) -> tuple[str, int]:
    """Pestaña Asombro. Devuelve (html, n_articulos)."""
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

    cards = "\n".join(_asombro_card(a) for a in candidatos)
    return (f"""
<div class="asombro-header">
  <h2>✨ Asombro</h2>
  <p>No las noticias más importantes del día — las que más te hacen pensar.<br>
     Artículos que revelan algo genuinamente fascinante sobre el mundo.</p>
</div>
<div class="asombro-grid">
{cards}
</div>""", len(candidatos))


_ESTADO_META = {
    "escalada":   ("&#8593;", "estado-escalada",   "Escalada"),
    "estable":    ("&#61;",   "estado-estable",    "Estable"),
    "resolucion": ("&#8595;", "estado-resolucion", "Resolviendo"),
    "silencio":   ("&#9675;", "estado-silencio",   "En silencio"),
}
_HORIZONTE_LABEL = {"dias": "días", "semanas": "semanas", "meses": "meses", "anos": "años"}


def _proceso_card(p: dict, hero: bool = False) -> str:
    estado = p.get("estado", "estable")
    icono, cls_estado, label_estado = _ESTADO_META.get(estado, ("=", "estado-estable", "Estable"))
    importancia = int(p.get("importancia") or 5)
    horizonte = _HORIZONTE_LABEL.get(p.get("horizonte", "meses"), p.get("horizonte", "meses"))
    historial_json = _html.escape(json.dumps(p.get("historial", []), ensure_ascii=False), quote=True)
    n_arts_hoy = len(p.get("articulos") or [])
    proceso_id = p.get("id", "")

    arts_html = ""
    for a in (p.get("articulos") or [])[:5]:
        titulo_a = _html.escape(a.get("titulo", ""))
        fuente_a = _html.escape(a.get("fuente", ""))
        enlace_a = _safe_url(a.get("enlace", "#"))
        arts_html += f'<li><a href="{enlace_a}" target="_blank" rel="noopener">{titulo_a}</a> <span class="proceso-art-fuente">— {fuente_a}</span></li>'
    arts_section = f'<ul class="proceso-articulos">{arts_html}</ul>' if arts_html else ""

    resumen     = _html.escape(p.get("resumen_hoy", ""))
    descripcion = _html.escape(p.get("descripcion", ""))
    nombre      = _html.escape(p.get("nombre", ""))
    hero_cls    = " proceso-card-hero" if hero else ""
    imp_pct     = importancia * 10

    return f"""
<div class="proceso-card{hero_cls}" data-historial="{historial_json}" data-estado="{estado}" data-importancia="{importancia}">
  <div class="proceso-strip proceso-strip-{estado}">
    <span class="proceso-strip-icono">{icono}</span>
    <span class="proceso-strip-label">{label_estado.upper()}</span>
    <span class="proceso-strip-dot">·</span>
    <span class="proceso-strip-horizonte">{horizonte.upper()}</span>
    <span class="proceso-strip-arts">{n_arts_hoy} art. hoy</span>
  </div>
  <div class="proceso-body">
    <div class="proceso-watermark">{importancia}</div>
    <div class="proceso-nombre">{nombre}</div>
    <div class="proceso-descripcion">{descripcion}</div>
    <div class="proceso-imp-row">
      <div class="proceso-imp-track">
        <div class="proceso-imp-fill proceso-imp-fill-{estado}" style="width:{imp_pct}%"></div>
      </div>
      <span class="proceso-imp-num">{importancia}/10</span>
    </div>
    <p class="proceso-resumen">{resumen}</p>
    {arts_section}
  </div>
  <div class="proceso-footer">
    <div class="proceso-trend-wrap" id="trend-{proceso_id}"></div>
    <div class="proceso-spark-label-row">
      <span class="proceso-spark-label">Cobertura</span>
    </div>
    <div class="proceso-sparkline"></div>
  </div>
</div>"""


def _conexiones_html(conexiones: list[dict], procesos: list[dict]) -> str:
    if not conexiones:
        return ""
    nombre_map = {p["id"]: p.get("nombre", p["id"]) for p in procesos}
    items = ""
    for c in conexiones:
        nom_a = _html.escape(nombre_map.get(c.get("proceso_a", ""), c.get("proceso_a", "")))
        nom_b = _html.escape(nombre_map.get(c.get("proceso_b", ""), c.get("proceso_b", "")))
        rel   = _html.escape(c.get("relacion", ""))
        items += f"""<div class="conexion-item">
  <span class="conexion-nombres">{nom_a} &#8594; {nom_b}</span>
  <span class="conexion-rel">{rel}</span>
</div>"""
    return f"""<div class="conexiones-panel">
  <div class="conexiones-titulo">&#128280; Conexiones entre procesos</div>
  {items}
</div>"""


def _tab_actualidad(procesos: list[dict], conexiones: list[dict] | None = None) -> str:
    if not procesos:
        return """
<div class="actualidad-header">
  <h2>Actualidad Absoluta</h2>
  <p>Los grandes procesos del mundo, m&#225;s all&#225; de las noticias del d&#237;a.</p>
</div>
<div class="actualidad-empty">
  <p>No hay procesos identificados a&#250;n. Se generan autom&#225;ticamente con el digest.</p>
</div>"""

    ordered = sorted(procesos, key=lambda x: int(x.get("importancia") or 0), reverse=True)
    hero_html = _proceso_card(ordered[0], hero=True) if ordered else ""
    rest_html = "\n".join(_proceso_card(p) for p in ordered[1:]) if len(ordered) > 1 else ""
    grid_html = f'<div class="proceso-grid">{rest_html}</div>' if rest_html else ""
    conn_html = _conexiones_html(conexiones or [], procesos)
    n = len(procesos)

    return f"""
<div class="actualidad-header">
  <h2>Actualidad Absoluta</h2>
  <p>{n} proceso(s) en curso &mdash; situaciones con impacto global sostenido.</p>
  <div class="historial-filtros">
    <span class="historial-filtro-label">Historial:</span>
    <button class="historial-filter-btn" data-dias="5" onclick="setHistorialDias(5)">5 d&#237;as</button>
    <button class="historial-filter-btn active" data-dias="10" onclick="setHistorialDias(10)">10 d&#237;as</button>
    <button class="historial-filter-btn" data-dias="15" onclick="setHistorialDias(15)">15 d&#237;as</button>
    <span class="historial-filtro-sep">|</span>
    <button class="historial-filter-btn" data-estado="escalada" onclick="filtrarProcesos('escalada',this)">&#8593; Escalada</button>
    <button class="historial-filter-btn" data-estado="estable" onclick="filtrarProcesos('estable',this)">= Estable</button>
    <button class="historial-filter-btn" data-estado="resolucion" onclick="filtrarProcesos('resolucion',this)">&#8595; Resuelve</button>
    <button class="historial-filter-btn" data-estado="todos" onclick="filtrarProcesos('todos',this)">Todos</button>
    <span class="historial-filtro-sep">|</span>
    <button class="historial-filter-btn briefing-btn" onclick="generarBriefing()">&#128196; Briefing</button>
  </div>
</div>

<div id="briefing-panel" style="display:none">
  <div class="briefing-header">
    <strong>&#128196; Memo de situaci&#243;n</strong>
    <button class="briefing-close" onclick="document.getElementById('briefing-panel').style.display='none'">&#215;</button>
  </div>
  <div id="briefing-texto" class="briefing-texto"></div>
</div>

{hero_html}
{grid_html}
{conn_html}"""


def _badge_novedad(articulo: dict) -> str:
    novedad = articulo.get("novedad", 2)
    if novedad == 3:
        return '<span class="badge-senal" title="Aporta información nueva">&#9670; Señal</span>'
    if novedad <= 1:
        return '<span class="badge-ruido" title="Repite información ya publicada">&#8762; Repetición</span>'
    return ""


def _alertas_watch_html(alertas: list[dict]) -> str:
    if not alertas:
        return ""
    items = "".join(
        f"""<div class="watch-alerta">
  <span class="watch-icono">&#9888;</span>
  <div>
    <strong>{_html.escape(a.get('condicion',''))}</strong>
    <p>{_html.escape(a.get('explicacion',''))}</p>
  </div>
  <span class="watch-confianza">{int(a.get('confianza',0)*100)}%</span>
</div>"""
        for a in alertas
    )
    return f'<div id="watch-panel">{items}</div>'


def renderizar_html(
    noticias: dict[str, list[dict]],
    analisis: dict[str, str],
    alternativas: dict[str, list[dict]] | None = None,
    analisis_alt: dict[str, str] | None = None,
    grupos_sintesis: list[dict] | None = None,
    fuentes_fallidas: list[str] | None = None,
    procesos: list[dict] | None = None,
    conexiones: list[dict] | None = None,
    alertas_watch: list[dict] | None = None,
) -> str:
    """
    Construye el HTML completo del digest.

    Parámetros:
        noticias → {categoría: [artículos enriquecidos]}
        analisis → {categoría: texto de análisis general}
    """
    ahora = datetime.now().strftime("%d/%m/%Y — %H:%M")
    total = sum(len(arts) for arts in noticias.values())

    secciones = "\n".join(
        _seccion(cat, arts, analisis.get(cat, ""))
        for cat, arts in noticias.items()
    )

    # URLs confirmadas por ≥2 fuentes de sesgos distintos (para badge multi-fuente)
    verificados: frozenset = frozenset()
    if grupos_sintesis:
        _sesgos_izq = {"izquierda", "centro-izquierda"}
        _sesgos_der = {"centro-derecha", "derecha"}
        candidatos: set[str] = set()
        for grupo in grupos_sintesis:
            arts = grupo.get("articulos", [])
            sesgos_presentes = {a.get("sesgo_fuente", "") for a in arts}
            tiene_izq = bool(sesgos_presentes & _sesgos_izq)
            tiene_der = bool(sesgos_presentes & _sesgos_der)
            if tiene_izq and tiene_der:
                for a in arts:
                    candidatos.add(a["enlace"])
        verificados = frozenset(candidatos)

    secciones = "\n".join(
        _seccion(cat, arts, analisis.get(cat, ""), verificados)
        for cat, arts in noticias.items()
    )

    destacadas          = _tab_destacadas(noticias, verificados)
    libertaria          = _tab_libertaria(alternativas or {}, analisis_alt or {}, verificados)
    sintesis            = _tab_sintesis(grupos_sintesis or [])
    para_leer           = _tab_para_leer()
    estadisticas        = _tab_estadisticas(fuentes_fallidas or [])
    asombro_html, n_asombro = _tab_asombro(noticias, alternativas or {})
    actualidad_html     = _tab_actualidad(procesos or [], conexiones or [])
    alertas_html        = _alertas_watch_html(alertas_watch or [])
    total_alt           = sum(len(a) for a in (alternativas or {}).values())
    n_sintesis          = len(grupos_sintesis) if grupos_sintesis else 0
    n_procesos          = len(procesos) if procesos else 0
    n_alertas           = len(alertas_watch) if alertas_watch else 0

    # colores de sesgo para el JS del cliente
    sesgo_colores_js = "{" + ",".join(
        f'"{k}":"{v}"' for k, v in COLORES_SESGO.items()
    ) + "}"

    # ── Tensiómetro del día ──────────────────────────────────────────────
    _all_arts = [art for arts in (noticias or {}).values() for art in arts]
    _sents = [art.get("sentimiento", "") for art in _all_arts if art.get("sentimiento")]
    _n_alar = sum(1 for s in _sents if s == "alarmista")
    _n_tot  = max(len(_sents), 1)
    _tension_pct = int(_n_alar / _n_tot * 100)
    if _tension_pct >= 40:
        _t_color, _t_txt = "#dc2626", "Día tenso"
    elif _tension_pct >= 20:
        _t_color, _t_txt = "#f97316", "Día activo"
    else:
        _t_color, _t_txt = "#3d7a52", "Día tranquilo"
    tension_html = (
        f'<div class="tension-wrap">'
        f'<span class="tension-dot" style="background:{_t_color}"></span>'
        f'<span class="tension-label" style="color:{_t_color}">{_t_txt}</span>'
        f'</div>'
    ) if _sents else ""

    _todos_arts = [a for arts in (noticias or {}).values() for a in arts]

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Digest de Noticias — {ahora}</title>
  <meta name="theme-color" content="#22c55e">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-title" content="Noticias Digest">
  <link rel="manifest" href="/manifest.json">
  <link rel="icon" href="/icon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&display=swap" rel="stylesheet">
  <style>{_CSS}</style>
</head>
<body>

<header>
  <div class="header-logo">
    <div class="icono">📰</div>
    <div>
      <div style="font-size:0.65rem;color:var(--txt-3);font-weight:600;letter-spacing:0.04em;margin-bottom:0.1rem" id="header-greeting"></div>
      <h1>Digest de Noticias</h1>
    </div>
  </div>
  <div class="meta">
    {ahora}<br>
    {total} principales · {total_alt} alternativas · Claude
    {tension_html}
  </div>
</header>

{alertas_html}

<div id="ia-banner">
  <span class="ia-msg">&#9888; <strong><span id="ia-banner-count">0</span> art&#237;culos</strong> sin an&#225;lisis IA &mdash; resumen, sesgo y s&#237;ntesis pueden estar incompletos</span>
  <button class="ia-close" onclick="document.getElementById('ia-banner').style.display='none'" title="Cerrar">&#215;</button>
</div>

<div class="tab-bar">
  <button class="tab-btn active" data-tab="destacadas" onclick="switchTab('destacadas')">
    &#9733; Destacadas
  </button>
  <button class="tab-btn" data-tab="actualidad" onclick="switchTab('actualidad')">
    &#127758; Actualidad{f'<span class="tab-count">{n_procesos}</span>' if n_procesos else ''}
  </button>
  <button class="tab-btn" data-tab="asombro" onclick="switchTab('asombro')">
    &#10024; Asombro{f'<span class="tab-count">{n_asombro}</span>' if n_asombro else ''}
  </button>
  <button class="tab-btn" data-tab="sintesis" onclick="switchTab('sintesis')">
    &#128279; S&#237;ntesis
    {f'<span style="font-size:.6rem;opacity:.7;margin-left:.3rem">{n_sintesis}</span>' if n_sintesis else ''}
  </button>
  <button class="tab-btn" data-tab="todas" onclick="switchTab('todas')">
    Todas las noticias
  </button>
  <button class="tab-btn" data-tab="libertaria" onclick="switchTab('libertaria')">
    &#9889; Prensa Libertaria
  </button>
  <button class="tab-btn" data-tab="para-leer" onclick="switchTab('para-leer')">
    &#9733; Para leer<span class="tab-count" id="bookmark-count" style="display:none"></span>
  </button>
  <button class="tab-btn" data-tab="estadisticas" onclick="switchTab('estadisticas')">
    &#128200; Estad&#237;sticas
  </button>
  <button class="dark-toggle" id="dark-toggle" onclick="toggleDark()">&#9790; Modo oscuro</button>
</div>

<div class="search-bar">
  <input class="search-input" id="buscador" type="search"
         placeholder="Buscar en noticias..." autocomplete="off"
         oninput="clearTimeout(_buscarTimer);_buscarTimer=setTimeout(function(){{buscar(document.getElementById('buscador').value)}},200)">
  <span class="kw-sep">|</span>
  <input class="keywords-input" id="kw-input" type="text"
         placeholder="Resaltar palabras clave..." autocomplete="off"
         oninput="aplicarKeywords(this.value)">
  <span class="search-count" id="search-count"></span>
</div>

<div class="sort-bar" id="sort-bar">
  <span class="sort-label">Ordenar:</span>
  <button class="sort-btn active" onclick="sortCards('defecto',this)">Por defecto</button>
  <button class="sort-btn" onclick="sortCards('fecha-desc',this)">Más recientes</button>
  <button class="sort-btn" onclick="sortCards('fecha-asc',this)">Más antiguos</button>
  <button class="sort-btn" onclick="sortCards('importante',this)">Destacados primero</button>
  <button class="sort-btn" onclick="sortCards('sesgo-izq',this)">Sesgo ← izquierda</button>
  <button class="sort-btn" onclick="sortCards('sesgo-der',this)">Sesgo → derecha</button>
  <button class="sort-btn" onclick="sortCards('alarmista',this)">Más alarmistas</button>
</div>

{_nav(list(noticias.keys()))}

<main>

  <div id="tab-destacadas" class="tab-content">
    {destacadas}
  </div>

  <div id="tab-todas" class="tab-content">
    {_leyenda()}
    {secciones}
  </div>

  <div id="tab-asombro" class="tab-content">
    {asombro_html}
  </div>

  <div id="tab-actualidad" class="tab-content">
    {actualidad_html}
  </div>

  <div id="tab-sintesis" class="tab-content">
    {sintesis}
  </div>

  <div id="tab-libertaria" class="tab-content">
    {libertaria}
  </div>

  <div id="tab-para-leer" class="tab-content">
    {para_leer}
  </div>

  <div id="tab-estadisticas" class="tab-content">
    {estadisticas}
  </div>

</main>

<footer>
  Sin publicidad · Sin algoritmos · Generado localmente ·
  Análisis por Claude (Anthropic)
</footer>

<!-- ── Vista inmersiva ─────────────────────────────────────────────── -->
<div class="drawer-overlay" id="drawer-overlay" onclick="cerrarDrawer()"></div>
<div class="drawer" id="drawer" role="dialog" aria-modal="true">
  <div class="drawer-header">
    <div class="drawer-header-meta">
      <span class="drawer-categoria" id="d-categoria"></span>
      <div class="drawer-fuente-row">
        <span class="fuente-nombre" id="d-fuente"></span>
        <span class="fecha" id="d-fecha"></span>
        <span class="drawer-reading">&#9201; <span id="d-reading"></span></span>
      </div>
      <div class="drawer-badges" style="margin-top:.4rem">
        <span class="badge-etiqueta">Fuente:</span>
        <span class="badge" id="d-sesgo-f"></span>
        <span class="badge-etiqueta" style="margin-left:.25rem">IA:</span>
        <span class="badge" id="d-sesgo-ia"></span>
        <span id="d-sent" style="margin-left:.25rem"></span>
      </div>
    </div>
    <button class="drawer-close" onclick="cerrarDrawer()" title="Cerrar (Esc)">&#x2715;</button>
  </div>
  <div class="drawer-body">
    <div class="drawer-titulo" id="d-titulo"></div>
    <p class="drawer-resumen" id="d-resumen"></p>
    <div class="drawer-critica" id="d-critica" style="display:none"></div>
  </div>
  <div class="drawer-footer" style="flex-wrap:wrap">
    <a class="drawer-btn drawer-btn-primary" id="d-btn-leer" href="#"
       target="_blank" rel="noopener noreferrer">
      Leer art&#237;culo &#8599;
    </a>
    <a class="drawer-btn drawer-btn-translate" id="d-btn-traducir" href="#"
       target="_blank" rel="noopener noreferrer">
      &#127760; Traducir
    </a>
    <button class="drawer-btn drawer-btn-secondary" id="d-btn-compartir"
            onclick="compartirArticulo()">
      Copiar enlace
    </button>
  </div>
</div>

<script>{_JS.replace('__SESGO_COLORES__', sesgo_colores_js)}</script>

</body>
</html>"""