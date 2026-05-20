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
import os
import webbrowser
from datetime import datetime

from analyzer import COLORES_SESGO
from config import ARCHIVO_SALIDA


from styles import _CSS


# ---------------------------------------------------------------------------
# Constructores de bloques HTML
# ---------------------------------------------------------------------------

CLASES_SENTIMIENTO = {
    "alarmista": "badge-sent-alarmista",
    "neutral":   "badge-sent-neutral",
    "optimista": "badge-sent-optimista",
}
ICONOS_SENTIMIENTO = {"alarmista": "⚠", "neutral": "◉", "optimista": "✦"}


def _badge(sesgo: str) -> str:
    color = COLORES_SESGO.get(sesgo, COLORES_SESGO["desconocido"])
    return f'<span class="badge" style="background:{color}">{sesgo.upper()}</span>'


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
        f'<div class="critica"><span class="critica-icono">💡</span>{critica}</div>'
        if critica else ""
    )
    verified_html = (
        '<span class="badge-verified" title="Confirmado por múltiples fuentes de distinto sesgo">&#10003; Multi-fuente</span>'
        if articulo.get("enlace") in verificados else ""
    )
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
  <p class="resumen">{articulo.get("resumen", "")}</p>
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


def _leyenda() -> str:
    """Bloque de leyenda con todos los niveles de sesgo y sus colores. Badges son clicables para filtrar."""
    items = []
    for s, color in COLORES_SESGO.items():
        items.append(
            f'<span class="badge" style="background:{color}" '
            f'onclick="filtrarPorSesgo(\'{s}\',this)" '
            f'title="Filtrar por {s}">{s.upper()}</span>'
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
        f'<div class="critica"><span class="critica-icono">💡</span>{critica}</div>'
        if critica else ""
    )
    verified_html = (
        '<span class="badge-verified">&#10003; Multi-fuente</span>'
        if articulo.get("enlace") in verificados else ""
    )
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
  <p class="resumen">{articulo.get("resumen", "")}</p>
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
  <a class="sintesis-fuente-link" href="{art['enlace']}" target="_blank" rel="noopener noreferrer">
    {art["titulo"]}
  </a>
</div>"""

    # Comparador de ángulos
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

    return f"""
<div class="sintesis-card" data-search="{grupo['titulo'].lower()} {' '.join(a['fuente'].lower() for a in articulos)}">
  <div class="sintesis-meta">
    <span class="sintesis-fuentes-count">{n} fuente{"s" if n != 1 else ""}</span>
    {"" if not hay_comparador else '<span style="font-size:.6rem;color:#a78bfa;font-weight:600">&#9670; Comparador activo</span>'}
  </div>
  <div class="sintesis-titulo">{grupo["titulo"]}</div>
  <div class="sintesis-texto">{grupo["sintesis"]}</div>
  {angulos_html if hay_comparador else f'<div class="sintesis-fuentes">{fuentes_html}</div>'}
</div>"""


def _tab_sintesis(grupos: list[dict]) -> str:
    """Pestaña de síntesis cruzada de historias."""
    if not grupos:
        return """<div class="sin-sintesis">
  <p>No hay síntesis disponible.</p>
  <p style="margin-top:.5rem;font-size:.8rem">
    Ejecuta <code>python main.py</code> (con análisis IA) para generar síntesis automáticas.
  </p>
</div>"""

    cards = "\n".join(_synthesis_card(g) for g in grupos)
    return f"""
<div class="sintesis-header">
  <h2>Síntesis de historias</h2>
  <p>{len(grupos)} historia(s) detectada(s) en múltiples fuentes · perspectivas cruzadas generadas por Gemini</p>
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
      - Si Gemini marcó artículos como importantes (importante=True): esos.
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
    fuente_label = "seleccionadas por Gemini" if any(
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


def _tab_estadisticas() -> str:
    """Pestaña de estadísticas de sesgo y cobertura (datos calculados por JS en cliente)."""
    return """
<div class="stats-header">
  <h2>Estadísticas del digest</h2>
  <p>Distribución ideológica, cobertura por fuente y diversidad — calculado en tiempo real</p>
</div>

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
    <div class="stat-card-title">Sesgo según análisis IA (requiere Gemini)</div>
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
     onclick="if(!event.target.closest('a'))abrirArticulo(this)">
  <div class="asombro-score">{estrellas}</div>
  <span class="asombro-cat">{_html.escape(categoria)}</span>
  <h3 class="asombro-titulo">
    <a href="{_html.escape(articulo['enlace'])}" target="_blank" rel="noopener"
       onclick="event.stopPropagation()">{_html.escape(articulo['titulo'])}</a>
  </h3>
  <div class="asombro-fuente">{_html.escape(articulo['fuente'])} · {_html.escape(articulo['fecha'])}</div>
  {razon_html}
  <p class="asombro-resumen">{resumen_corto}</p>
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


def renderizar_html(
    noticias: dict[str, list[dict]],
    analisis: dict[str, str],
    alternativas: dict[str, list[dict]] | None = None,
    analisis_alt: dict[str, str] | None = None,
    grupos_sintesis: list[dict] | None = None,
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
    estadisticas        = _tab_estadisticas()
    asombro_html, n_asombro = _tab_asombro(noticias, alternativas or {})
    total_alt           = sum(len(a) for a in (alternativas or {}).values())
    n_sintesis          = len(grupos_sintesis) if grupos_sintesis else 0

    # colores de sesgo para el JS del cliente
    sesgo_colores_js = "{" + ",".join(
        f'"{k}":"{v}"' for k, v in COLORES_SESGO.items()
    ) + "}"

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
    <h1>Digest de Noticias</h1>
  </div>
  <div class="meta">
    {ahora}<br>
    {total} principales · {total_alt} alternativas · Gemini
  </div>
</header>

<div id="ia-banner">
  <span class="ia-msg">&#9888; <strong><span id="ia-banner-count">0</span> art&#237;culos</strong> sin an&#225;lisis IA &mdash; resumen, sesgo y s&#237;ntesis pueden estar incompletos</span>
  <button class="ia-regen" id="ia-regen-btn" onclick="lanzarAnalisisIA()">Regenerar an&#225;lisis IA</button>
  <button class="ia-close" onclick="document.getElementById('ia-banner').style.display='none'" title="Cerrar">&#215;</button>
</div>

<div class="tab-bar">
  <button class="tab-btn active" data-tab="destacadas" onclick="switchTab('destacadas')">
    &#9733; Destacadas
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
  Análisis por Google Gemini
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

<script>
var _tabActual    = 'destacadas';
var _filtroSesgo  = null;
var _statsReady   = false;
var _buscarTimer  = null;
var SESGO_COLORES = {sesgo_colores_js};

/* ── Navegación por pestañas ─────────────────────────────────────────── */
function switchTab(name) {{
  _tabActual = name;
  document.querySelectorAll('.tab-content').forEach(function(el) {{
    el.style.display = 'none';
  }});
  document.querySelectorAll('.tab-btn').forEach(function(el) {{
    el.classList.remove('active');
  }});
  var tabEl = document.getElementById('tab-' + name);
  if (tabEl) tabEl.style.display = 'block';
  var btnEl = document.querySelector('[data-tab="' + name + '"]');
  if (btnEl) btnEl.classList.add('active');

  var nav = document.getElementById('cat-nav');
  if (nav) nav.style.display = name === 'todas' ? 'flex' : 'none';

  // La barra de búsqueda y el filtro solo tienen sentido fuera de Estadísticas
  var noSearch = name === 'estadisticas' || name === 'para-leer';
  var barra = document.querySelector('.search-bar');
  if (barra) barra.style.display = noSearch ? 'none' : 'flex';
  var sortBar = document.getElementById('sort-bar');
  var noSort = noSearch || name === 'sintesis' || name === 'asombro';
  if (sortBar) sortBar.style.display = noSort ? 'none' : 'flex';

  try {{
    if (name === 'estadisticas') {{
      if (!_statsReady) {{ renderEstadisticas(); _statsReady = true; }}
    }} else if (name === 'para-leer') {{
      _renderizarParaLeer();
    }} else {{
      var q = document.getElementById('buscador');
      if (q && q.value) buscar(q.value); else _limpiarContador();
      _sincronizarBotonesBK();
      if (_kwActuales && _kwActuales.length) {{
        var kwIn = document.getElementById('kw-input');
        if (kwIn) aplicarKeywords(kwIn.value);
      }}
    }}
  }} catch(e) {{}}
  try {{ localStorage.setItem('digestTab', name); }} catch(e) {{}}
}}

/* ── Búsqueda ────────────────────────────────────────────────────────── */
function buscar(q) {{
  q = q.trim().toLowerCase();
  var tarjetas = document.querySelectorAll(
    '#tab-' + _tabActual + ' .tarjeta, ' +
    '#tab-' + _tabActual + ' .tarjeta-destacada, ' +
    '#tab-' + _tabActual + ' .sintesis-card'
  );
  var visibles = 0;
  tarjetas.forEach(function(t) {{
    var texto = (t.textContent || t.innerText).toLowerCase();
    var ds    = (t.dataset.search || '').toLowerCase();
    var okQ   = !q || texto.includes(q) || ds.includes(q);
    var okF   = true;
    if (_filtroSesgo && _tabActual === 'todas') {{
      // Usar el sesgo de la fuente (siempre disponible) para filtrar
      var sF = (t.dataset.sesgoFuente || '').toLowerCase();
      okF = (sF === _filtroSesgo);
    }}
    var ok   = okQ && okF;
    t.hidden = !ok;
    if (ok) visibles++;
  }});
  var total = tarjetas.length;
  var cnt   = document.getElementById('search-count');
  if (cnt) cnt.textContent = (q || _filtroSesgo) ? visibles + ' de ' + total + ' resultado(s)' : '';
}}

function _limpiarContador() {{
  var cnt = document.getElementById('search-count');
  if (cnt) cnt.textContent = '';
}}

/* ── Filtro de sesgo (leyenda clicable) ──────────────────────────────── */
function filtrarPorSesgo(sesgo, el) {{
  if (_filtroSesgo === sesgo) {{
    limpiarFiltro();
    return;
  }}
  _filtroSesgo = sesgo;
  document.querySelectorAll('.leyenda-items .badge').forEach(function(b) {{
    b.classList.remove('filtro-activo');
  }});
  el.classList.add('filtro-activo');

  var aviso = document.getElementById('filtro-aviso');
  var btn   = document.getElementById('filtro-clear');
  if (aviso) {{ aviso.textContent = 'Filtrando: ' + sesgo; aviso.style.display = ''; }}
  if (btn)   btn.style.display = '';

  if (_tabActual !== 'todas') switchTab('todas');
  else buscar(document.getElementById('buscador').value);
}}

function limpiarFiltro() {{
  _filtroSesgo = null;
  document.querySelectorAll('.leyenda-items .badge').forEach(function(b) {{
    b.classList.remove('filtro-activo');
  }});
  var aviso = document.getElementById('filtro-aviso');
  var btn   = document.getElementById('filtro-clear');
  if (aviso) aviso.style.display = 'none';
  if (btn)   btn.style.display   = 'none';
  buscar(document.getElementById('buscador').value);
}}

/* ── Estadísticas ────────────────────────────────────────────────────── */
function renderEstadisticas() {{
  var tarjetas   = document.querySelectorAll('#tab-todas .tarjeta');
  var sesgosF    = {{}};  // por sesgo_fuente (siempre disponible)
  var sesgosIA   = {{}};  // por sesgo_ia (solo con análisis IA)
  var fuentes    = {{}};
  var categorias = {{}};

  tarjetas.forEach(function(t) {{
    // Leer directamente de los data attributes — fiable independientemente del DOM
    var sF  = (t.dataset.sesgoFuente || 'desconocido').toLowerCase();
    var sIA = (t.dataset.sesgoIa    || 'desconocido').toLowerCase();
    sesgosF[sF]  = (sesgosF[sF]  || 0) + 1;
    sesgosIA[sIA] = (sesgosIA[sIA] || 0) + 1;

    var fn = t.querySelector('.fuente-nombre');
    if (fn) {{ var f = fn.textContent.trim(); fuentes[f] = (fuentes[f] || 0) + 1; }}
  }});

  document.querySelectorAll('#tab-todas .seccion').forEach(function(s) {{
    var titulo = s.querySelector('.seccion-titulo');
    if (titulo) {{
      categorias[titulo.textContent.trim()] = s.querySelectorAll('.tarjeta').length;
    }}
  }});

  var total    = tarjetas.length;
  var nFuentes = Object.keys(fuentes).length;

  // Diversidad: basada en sesgo_fuente (siempre tiene datos reales)
  var sesgosRef = ['izquierda','centro-izquierda','centro','centro-derecha','derecha'];
  var nDiv = sesgosRef.filter(function(s) {{
    return (sesgosF[s] || 0) / Math.max(total, 1) >= 0.05;
  }}).length;
  var divPct = sesgosRef.length ? Math.round((nDiv / sesgosRef.length) * 100) + '%' : '—';

  // Sesgos detectados por IA (excluye desconocido)
  var sesgosActIA = Object.keys(sesgosIA).filter(function(s) {{
    return s !== 'desconocido' && sesgosIA[s] > 0;
  }}).length;

  document.getElementById('kpi-total').textContent      = total;
  document.getElementById('kpi-fuentes').textContent    = nFuentes;
  document.getElementById('kpi-diversidad').textContent = divPct;
  document.getElementById('kpi-sesgos').textContent     = sesgosActIA || '—';

  var sesgoOrden = ['izquierda','centro-izquierda','centro','centro-derecha','derecha','desconocido'];

  // Gráfico: sesgo de la fuente (siempre disponible)
  var maxSF = Math.max.apply(null, sesgoOrden.map(function(s) {{ return sesgosF[s]||0; }})) || 1;
  document.getElementById('stat-sesgo-chart').innerHTML = sesgoOrden.map(function(s) {{
    var n   = sesgosF[s] || 0;
    var pct = Math.round((n / maxSF) * 100);
    var col = SESGO_COLORES[s] || '#9ca3af';
    return '<div class="stat-bar-row">' +
      '<span class="stat-bar-label">' + s + '</span>' +
      '<div class="stat-bar-bg"><div class="stat-bar-fill" style="width:' + pct + '%;background:' + col + '"></div></div>' +
      '<span class="stat-bar-count">' + n + '</span>' +
      '</div>';
  }}).join('');

  // Gráfico: sesgo IA (puede estar todo en "desconocido" sin cuota)
  var maxSIA = Math.max.apply(null, sesgoOrden.map(function(s) {{ return sesgosIA[s]||0; }})) || 1;
  var iaHtml = sesgoOrden.map(function(s) {{
    var n   = sesgosIA[s] || 0;
    var pct = Math.round((n / maxSIA) * 100);
    var col = SESGO_COLORES[s] || '#9ca3af';
    return '<div class="stat-bar-row">' +
      '<span class="stat-bar-label">' + s + '</span>' +
      '<div class="stat-bar-bg"><div class="stat-bar-fill" style="width:' + pct + '%;background:' + col + '"></div></div>' +
      '<span class="stat-bar-count">' + n + '</span>' +
      '</div>';
  }}).join('');
  var iaEl = document.getElementById('stat-sesgo-ia-chart');
  if (iaEl) iaEl.innerHTML = sesgosActIA === 0
    ? '<span style="color:var(--txt-3);font-size:.78rem">Sin datos IA — ejecuta con GEMINI_API_KEY para ver análisis</span>'
    : iaHtml;

  // Top fuentes
  var topF = Object.entries(fuentes).sort(function(a,b){{ return b[1]-a[1]; }}).slice(0,12);
  var maxF = topF.length ? topF[0][1] : 1;
  document.getElementById('stat-fuentes-chart').innerHTML = topF.map(function(p) {{
    var pct = Math.round((p[1]/maxF)*100);
    return '<div class="stat-bar-row">' +
      '<span class="stat-bar-label">' + p[0] + '</span>' +
      '<div class="stat-bar-bg"><div class="stat-bar-fill" style="width:' + pct + '%;background:var(--accent)"></div></div>' +
      '<span class="stat-bar-count">' + p[1] + '</span>' +
      '</div>';
  }}).join('');

  // Categorías
  var catEntries = Object.entries(categorias);
  var maxC = Math.max.apply(null, catEntries.map(function(e){{ return e[1]; }})) || 1;
  document.getElementById('stat-cat-chart').innerHTML = catEntries.map(function(p) {{
    var pct = Math.round((p[1]/maxC)*100);
    return '<div class="stat-bar-row">' +
      '<span class="stat-bar-label">' + p[0] + '</span>' +
      '<div class="stat-bar-bg"><div class="stat-bar-fill" style="width:' + pct + '%;background:var(--accent-green)"></div></div>' +
      '<span class="stat-bar-count">' + p[1] + '</span>' +
      '</div>';
  }}).join('');
}}

/* ── Lista de lectura ────────────────────────────────────────────────── */
var _BK_KEY = 'digestBookmarks';

function _cargarBookmarks() {{
  try {{ return JSON.parse(localStorage.getItem(_BK_KEY) || '[]'); }} catch(e) {{ return []; }}
}}
function _guardarBookmarks(lista) {{
  try {{ localStorage.setItem(_BK_KEY, JSON.stringify(lista)); }} catch(e) {{}}
}}
function _actualizarContadorBK() {{
  var n    = _cargarBookmarks().length;
  var cnt  = document.getElementById('bookmark-count');
  if (!cnt) return;
  if (n > 0) {{ cnt.textContent = n; cnt.style.display = ''; }}
  else        cnt.style.display = 'none';
}}

function toggleBookmark(ev, btn) {{
  ev.stopPropagation();
  var d       = btn.dataset;
  var enlace  = d.enlace;
  var lista   = _cargarBookmarks();
  var idx     = lista.findIndex(function(x) {{ return x.enlace === enlace; }});
  if (idx >= 0) {{
    lista.splice(idx, 1);
    btn.classList.remove('guardado');
    btn.title = 'Guardar para leer';
  }} else {{
    lista.push({{ enlace: enlace, titulo: d.titulo, fuente: d.fuente, fecha: d.fecha }});
    btn.classList.add('guardado');
    btn.title = 'Quitar de la lista';
  }}
  _guardarBookmarks(lista);
  _actualizarContadorBK();
  if (_tabActual === 'para-leer') _renderizarParaLeer();
}}

function _renderizarParaLeer() {{
  var lista = _cargarBookmarks();
  var cont  = document.getElementById('para-leer-contenido');
  var desc  = document.getElementById('para-leer-desc');
  if (!cont) return;
  if (lista.length === 0) {{
    cont.innerHTML = '<div class="para-leer-empty">Todavía no has guardado ningún artículo.<br>Haz clic en ★ en cualquier tarjeta para añadirlo aquí.</div>';
    if (desc) desc.textContent = 'Artículos guardados con ★ — se conservan entre sesiones';
    return;
  }}
  if (desc) desc.textContent = lista.length + ' artículo(s) guardado(s)';
  cont.innerHTML = '<div class="grid">' + lista.map(function(item) {{
    var tit = item.titulo || '';
    var src = item.fuente || '';
    var fch = item.fecha  || '';
    var url = item.enlace || '#';
    return '<div class="tarjeta" style="cursor:default">' +
      '<div class="tarjeta-meta"><div class="fuente-bloque">' +
      '<span class="fuente-nombre">' + src + '</span>' +
      '<span class="fecha">' + fch + '</span>' +
      '</div>' +
      '<button class="bookmark-btn guardado" title="Quitar de la lista" data-enlace-rm="' + url.replace(/"/g,'&quot;') + '" onclick="_eliminarBookmark(this.dataset.enlaceRm,this)">&#9733;</button>' +
      '</div>' +
      '<div class="titulo"><a href="' + url + '" target="_blank" rel="noopener noreferrer">' + tit + '</a></div>' +
      '</div>';
  }}).join('') + '</div>';
}}

function _eliminarBookmark(enlace, btn) {{
  var lista = _cargarBookmarks().filter(function(x) {{ return x.enlace !== enlace; }});
  _guardarBookmarks(lista);
  _actualizarContadorBK();
  _renderizarParaLeer();
  // Quitar clase guardado del botón correspondiente en otras pestañas
  document.querySelectorAll('.bookmark-btn[data-enlace="' + enlace + '"]').forEach(function(b) {{
    b.classList.remove('guardado');
    b.title = 'Guardar para leer';
  }});
}}

function _sincronizarBotonesBK() {{
  var guardados = new Set(_cargarBookmarks().map(function(x) {{ return x.enlace; }}));
  document.querySelectorAll('.bookmark-btn').forEach(function(btn) {{
    if (guardados.has(btn.dataset.enlace)) {{
      btn.classList.add('guardado');
      btn.title = 'Quitar de la lista';
    }} else {{
      btn.classList.remove('guardado');
      btn.title = 'Guardar para leer';
    }}
  }});
}}

/* ── Resaltado de palabras clave ─────────────────────────────────────── */
var _kwActuales = [];

function aplicarKeywords(raw) {{
  _kwActuales = raw.split(',').map(function(s) {{ return s.trim().toLowerCase(); }}).filter(Boolean);
  try {{ localStorage.setItem('digestKeywords', raw); }} catch(e) {{}}
  document.querySelectorAll('.tarjeta, .tarjeta-destacada').forEach(function(t) {{
    if (_kwActuales.length === 0) {{
      t.classList.remove('kw-match');
    }} else {{
      var texto = (t.dataset.search || '').toLowerCase();
      var match = _kwActuales.some(function(kw) {{ return texto.includes(kw); }});
      t.classList.toggle('kw-match', match);
    }}
  }});
}}

/* ── Vista inmersiva ─────────────────────────────────────────────────── */
function abrirArticulo(el) {{
  var d         = el.dataset;
  var titulo    = d.titulo    || '';
  var fuente    = d.fuente    || '';
  var fecha     = d.fecha     || '';
  var enlace    = d.enlace    || '#';
  var resumen   = d.resumen   || '';
  var critica   = d.critica   || '';
  var sesgoF    = d.sesgoFuente || 'desconocido';
  var sesgoIA   = d.sesgoIa    || 'desconocido';

  // Categoría: leer del ancestro .seccion si existe
  var secEl = el.closest('.seccion');
  var cat   = secEl ? (secEl.querySelector('.seccion-titulo') || {{}}).textContent || '' : (d.categoria || '');

  // Tiempo de lectura estimado
  var palabras = (titulo + ' ' + resumen).split(/\\s+/).filter(Boolean).length;
  var minutos  = Math.max(1, Math.round(palabras / 200));

  document.getElementById('d-categoria').textContent = cat;
  document.getElementById('d-fuente').textContent    = fuente;
  document.getElementById('d-fecha').textContent     = fecha;
  document.getElementById('d-reading').textContent   = minutos + ' min lectura';
  document.getElementById('d-titulo').textContent    = titulo;
  document.getElementById('d-resumen').textContent   = resumen;

  var sfEl = document.getElementById('d-sesgo-f');
  sfEl.textContent = sesgoF.toUpperCase();
  sfEl.style.background = SESGO_COLORES[sesgoF] || '#9ca3af';

  var siaEl = document.getElementById('d-sesgo-ia');
  siaEl.textContent = sesgoIA.toUpperCase();
  siaEl.style.background = SESGO_COLORES[sesgoIA] || '#9ca3af';

  var sent     = (d.sentimiento || '').toLowerCase();
  var sentClss = {{'alarmista':'badge-sent-alarmista','neutral':'badge-sent-neutral','optimista':'badge-sent-optimista'}};
  var sentIcon = {{'alarmista':'⚠','optimista':'✦'}};
  var sentEl   = document.getElementById('d-sent');
  if (sentEl) {{
    sentEl.innerHTML = (sent && sent !== 'neutral')
      ? '<span class="badge-sent ' + (sentClss[sent]||'') + '">' + (sentIcon[sent]||'') + ' ' + sent.toUpperCase() + '</span>'
      : '';
  }}

  var criticaEl = document.getElementById('d-critica');
  if (critica) {{
    criticaEl.textContent  = '\U0001F4A1 ' + critica;
    criticaEl.style.display = '';
  }} else {{
    criticaEl.style.display = 'none';
  }}

  document.getElementById('d-btn-leer').href = enlace;
  document.getElementById('d-btn-traducir').href = 'https://translate.google.com/translate?sl=auto&tl=es&u=' + encodeURIComponent(enlace);

  document.getElementById('drawer-overlay').classList.add('open');
  document.getElementById('drawer').classList.add('open');
  document.body.style.overflow = 'hidden';
}}

function cerrarDrawer() {{
  document.getElementById('drawer-overlay').classList.remove('open');
  document.getElementById('drawer').classList.remove('open');
  document.body.style.overflow = '';
}}

function compartirArticulo() {{
  var titulo  = document.getElementById('d-titulo').textContent;
  var enlace  = document.getElementById('d-btn-leer').href;
  var btn     = document.getElementById('d-btn-compartir');
  if (navigator.share) {{
    navigator.share({{ title: titulo, url: enlace }}).catch(function() {{}});
  }} else {{
    navigator.clipboard.writeText(enlace).then(function() {{
      btn.textContent = '✓ Copiado';
      setTimeout(function() {{ btn.textContent = 'Copiar enlace'; }}, 2000);
    }}).catch(function() {{
      prompt('Copia este enlace:', enlace);
    }});
  }}
}}

document.addEventListener('keydown', function(e) {{
  if (e.key === 'Escape') cerrarDrawer();
}});

/* ── Lanzar análisis IA sin re-descargar feeds ───────────────────────── */
function lanzarAnalisisIA() {{
  var btn = document.getElementById('ia-regen-btn');
  btn.disabled = true;
  btn.textContent = 'Analizando…';
  // Intenta /analizar (solo IA); si no existe el endpoint, cae a /regenerar
  fetch('/analizar', {{method:'POST'}})
    .then(function(r) {{
      if (!r.ok) throw new Error('no-endpoint');
      return r.json();
    }})
    .then(function() {{
      btn.textContent = 'Esperando resultado…';
      // Sondea /estado cada 4 s hasta que generando === false
      var poll = setInterval(function() {{
        fetch('/estado').then(function(r){{return r.json();}}).then(function(s) {{
          if (!s.generando) {{
            clearInterval(poll);
            window.location.reload();
          }}
        }}).catch(function(){{ clearInterval(poll); window.location.reload(); }});
      }}, 4000);
    }})
    .catch(function() {{
      // Sin servidor Flask (archivo local) o /analizar no existe: regenerar completo
      window.location.href = '/regenerar';
    }});
}}

/* ── Inicio ──────────────────────────────────────────────────────────── */
(function() {{
  var last = 'destacadas';
  try {{
    var saved = localStorage.getItem('digestTab') || 'destacadas';
    // 'todas' muestra todo en scroll continuo — no restaurar como tab de inicio
    last = (saved === 'todas') ? 'destacadas' : saved;
  }} catch(e) {{}}

  // Restaurar palabras clave
  try {{
    var kw = localStorage.getItem('digestKeywords');
    if (kw) {{
      var kwInput = document.getElementById('kw-input');
      if (kwInput) {{ kwInput.value = kw; aplicarKeywords(kw); }}
    }}
  }} catch(e) {{}}

  // Actualizar contador de bookmarks
  try {{ _actualizarContadorBK(); }} catch(e) {{}}

  // Detectar artículos sin análisis IA y mostrar banner
  try {{
    var sinIA = document.querySelectorAll('[data-sesgo-ia="desconocido"]').length;
    if (sinIA > 0) {{
      var bannerCount = document.getElementById('ia-banner-count');
      var bannerEl    = document.getElementById('ia-banner');
      if (bannerCount) bannerCount.textContent = sinIA;
      if (bannerEl)    bannerEl.style.display = 'flex';
      if (window.location.protocol === 'file:') {{
        var regenBtn = document.getElementById('ia-regen-btn');
        if (regenBtn) {{
          regenBtn.textContent = 'Iniciar servidor Flask';
          regenBtn.onclick = function() {{
            alert('Inicia el servidor Flask (app.py) o el .bat del escritorio para regenerar el análisis IA.');
          }};
        }}
      }}
    }}
  }} catch(e) {{}}

  switchTab(last);
}})();
</script>

<script>
// ── Ordenación de artículos ───────────────────────────────────────────────
var _SESGO_ORD = {{
  'izquierda': 0, 'centro-izquierda': 1, 'centro': 2,
  'centro-derecha': 3, 'derecha': 4, 'desconocido': 5
}};
var _SENT_ORD = {{'alarmista': 0, 'neutral': 1, 'optimista': 2}};

function _parseFecha(s) {{
  if (!s || s === 'Fecha desconocida') return 0;
  var p = s.split(' '), f = (p[0]||'').split('/'), h = (p[1]||'00:00').split(':');
  return new Date(f[2], f[1]-1, f[0], h[0], h[1]).getTime();
}}

function sortCards(criterio, btn) {{
  document.querySelectorAll('.sort-btn').forEach(function(b) {{ b.classList.remove('active'); }});
  if (btn) btn.classList.add('active');

  var tab = document.querySelector('.tab-content[style*="block"]');
  if (!tab) return;

  tab.querySelectorAll('.grid, .grid-destacadas').forEach(function(grid) {{
    var cards = Array.from(grid.querySelectorAll(':scope > .tarjeta, :scope > .tarjeta-destacada'));
    if (cards.length < 2) return;

    cards.sort(function(a, b) {{
      switch (criterio) {{
        case 'fecha-desc':
          return _parseFecha(b.dataset.fecha) - _parseFecha(a.dataset.fecha);
        case 'fecha-asc':
          return _parseFecha(a.dataset.fecha) - _parseFecha(b.dataset.fecha);
        case 'importante':
          return (b.dataset.importante === 'true' ? 1 : 0) - (a.dataset.importante === 'true' ? 1 : 0);
        case 'sesgo-izq':
          return (_SESGO_ORD[a.dataset.sesgoIa] !== undefined ? _SESGO_ORD[a.dataset.sesgoIa] : 5)
               - (_SESGO_ORD[b.dataset.sesgoIa] !== undefined ? _SESGO_ORD[b.dataset.sesgoIa] : 5);
        case 'sesgo-der':
          return (_SESGO_ORD[b.dataset.sesgoIa] !== undefined ? _SESGO_ORD[b.dataset.sesgoIa] : 5)
               - (_SESGO_ORD[a.dataset.sesgoIa] !== undefined ? _SESGO_ORD[a.dataset.sesgoIa] : 5);
        case 'alarmista':
          return (_SENT_ORD[a.dataset.sentimiento] !== undefined ? _SENT_ORD[a.dataset.sentimiento] : 1)
               - (_SENT_ORD[b.dataset.sentimiento] !== undefined ? _SENT_ORD[b.dataset.sentimiento] : 1);
        default:
          return parseInt(a.dataset.order || 0) - parseInt(b.dataset.order || 0);
      }}
    }});

    cards.forEach(function(c) {{ grid.appendChild(c); }});
  }});
}}
</script>

<script>
if ('serviceWorker' in navigator) {{
  navigator.serviceWorker.register('/sw.js');
}}
</script>

</body>
</html>"""


def guardar_y_abrir(html: str) -> None:
    """Escribe el HTML en disco y lo abre en el navegador por defecto."""
    with open(ARCHIVO_SALIDA, "w", encoding="utf-8") as f:
        f.write(html)

    ruta = os.path.abspath(ARCHIVO_SALIDA)
    print(f"\n✅ Guardado en: {ruta}")

    webbrowser.open(f"file:///{ruta}")
    print("🌐 Abriendo en el navegador...")
