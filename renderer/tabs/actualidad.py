"""Pestaña Actualidad Absoluta — grandes procesos globales en curso."""

import html as _html
import json

TAB_ID    = "actualidad"
TAB_LABEL = "Hilos"
TAB_ICON  = "🌍"

_ESTADO_META = {
    "escalada":   ("↑", "estado-escalada",   "Escalada"),
    "estable":    ("=", "estado-estable",     "Estable"),
    "resolucion": ("↓", "estado-resolucion",  "Resolviendo"),
    "silencio":   ("○", "estado-silencio",    "En silencio"),
}
_SESGO_ABREV = {
    "izquierda": "IZQ", "centro-izquierda": "C·IZQ",
    "centro": "CTR",
    "centro-derecha": "C·DER", "derecha": "DER",
    "desconocido": "?",
}
_HORIZONTE_LABEL = {
    "dias": "días", "semanas": "semanas", "meses": "meses", "anos": "años",
}


def _tendencia_html(pct: int) -> str:
    """Badge de tendencia de cobertura vs hace 7 días."""
    if pct > 15:
        return f'<span class="proceso-tendencia proceso-tendencia-sube">&#8593; +{pct}%</span>'
    if pct < -15:
        return f'<span class="proceso-tendencia proceso-tendencia-baja">&#8595; {pct}%</span>'
    return '<span class="proceso-tendencia proceso-tendencia-estable">&#8594;</span>'


def _dias_html(dias: int, fecha_inicio: str) -> str:
    """Badge de antigüedad del proceso."""
    if dias <= 1:
        return '<span class="proceso-edad">Nuevo hoy</span>'
    if dias < 7:
        return f'<span class="proceso-edad">{dias} días</span>'
    if dias < 30:
        semanas = dias // 7
        return f'<span class="proceso-edad">{semanas} sem.</span>'
    meses = dias // 30
    return f'<span class="proceso-edad">{meses} mes{"es" if meses > 1 else ""}</span>'


def _proceso_card(p: dict, hero: bool = False) -> str:
    estado    = p.get("estado", "estable")
    icono, cls_estado, label_estado = _ESTADO_META.get(estado, ("=", "estado-estable", "Estable"))
    importancia   = int(p.get("importancia") or 5)
    horizonte     = _HORIZONTE_LABEL.get(p.get("horizonte", "meses"), p.get("horizonte", "meses"))
    dias_activo   = int(p.get("dias_activo") or 1)
    tendencia_pct = int(p.get("tendencia_pct") or 0)
    fecha_inicio  = p.get("fecha_inicio", "")
    n_arts_hoy    = len(p.get("articulos") or [])
    proceso_id    = p.get("id", "")

    historial_json = _html.escape(
        json.dumps(p.get("historial", []), ensure_ascii=False), quote=True
    )

    # Artículos relacionados — siempre visibles, con badge de sesgo
    arts_html = ""
    for a in (p.get("articulos") or [])[:4]:
        titulo_a = _html.escape(a.get("titulo", ""))
        fuente_a = _html.escape(a.get("fuente", ""))
        enlace_a = _html.escape(a.get("enlace", "#"), quote=True)
        sesgo_a  = (a.get("sesgo_fuente") or "desconocido").replace(" ", "-")
        abrev_a  = _SESGO_ABREV.get(a.get("sesgo_fuente") or "desconocido", "?")
        arts_html += (
            f'<li>'
            f'<span class="proceso-art-badge sesgo-{sesgo_a}">{abrev_a}</span>'
            f'<a href="{enlace_a}" target="_blank" rel="noopener">{titulo_a}</a>'
            f'<span class="proceso-art-fuente">{fuente_a}</span>'
            f'</li>'
        )
    arts_section = f'<ul class="proceso-articulos">{arts_html}</ul>' if arts_html else ""

    resumen     = _html.escape(p.get("resumen_hoy", ""))
    descripcion = _html.escape(p.get("descripcion", ""))
    nombre      = _html.escape(p.get("nombre", ""))
    hero_cls    = " proceso-card-hero" if hero else ""
    imp_pct     = importancia * 10

    tendencia   = _tendencia_html(tendencia_pct)
    edad        = _dias_html(dias_activo, fecha_inicio)

    return f"""
<div class="proceso-card{hero_cls}"
     data-historial="{historial_json}"
     data-estado="{estado}"
     data-importancia="{importancia}">

  <div class="proceso-strip proceso-strip-{estado}">
    <span class="proceso-strip-estado">{icono} {label_estado.upper()}</span>
    <span class="proceso-strip-meta">
      {edad}
      {tendencia}
      <span class="proceso-strip-arts">{n_arts_hoy} art. hoy</span>
    </span>
  </div>

  <div class="proceso-body">
    <div class="proceso-imp-badge">{importancia}<span>/10</span></div>
    <div class="proceso-nombre">{nombre}</div>
    <div class="proceso-descripcion">{descripcion}</div>

    <div class="proceso-barra-wrap">
      <div class="proceso-barra-fill proceso-barra-{estado}" style="width:{imp_pct}%"></div>
    </div>

    <p class="proceso-resumen">{resumen}</p>

    {arts_section}
  </div>

  <div class="proceso-footer">
    <div class="proceso-spark-header">
      <span class="proceso-spark-label">Cobertura · {horizonte.upper()}</span>
      <span class="proceso-spark-dias">{dias_activo} días en seguimiento</span>
    </div>
    <canvas class="proceso-sparkline" id="spark-{proceso_id}" height="44"></canvas>
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
  <div class="conexiones-titulo">&#128280; Conexiones entre hilos</div>
  {items}
</div>"""


def render(procesos: list[dict] | None = None,
           conexiones: list[dict] | None = None, **_) -> str:
    procs = procesos or []

    if not procs:
        return """
<div class="actualidad-header">
  <h2>Hilos</h2>
  <p>Los grandes hilos del mundo, m&#225;s all&#225; de las noticias del d&#237;a.</p>
</div>
<div class="actualidad-empty">
  <p>No hay hilos identificados a&#250;n. Se generan autom&#225;ticamente con el digest.</p>
</div>"""

    ordered   = sorted(procs, key=lambda x: int(x.get("importancia") or 0), reverse=True)
    hero_html = _proceso_card(ordered[0], hero=True) if ordered else ""
    rest_html = "\n".join(_proceso_card(p) for p in ordered[1:]) if len(ordered) > 1 else ""
    grid_html = f'<div class="proceso-grid">{rest_html}</div>' if rest_html else ""
    conn_html = _conexiones_html(conexiones or [], procs)
    n = len(procs)

    return f"""
<div class="actualidad-header">
  <h2>Hilos</h2>
  <p>{n} hilo(s) en seguimiento &mdash; situaciones con impacto sostenido en el tiempo.</p>
  <div class="historial-filtros">
    <span class="historial-filtro-label">Ver:</span>
    <button class="historial-filter-btn" data-dias="7"  onclick="setHistorialDias(7)">7 d&#237;as</button>
    <button class="historial-filter-btn active" data-dias="15" onclick="setHistorialDias(15)">15 d&#237;as</button>
    <button class="historial-filter-btn" data-dias="30" onclick="setHistorialDias(30)">30 d&#237;as</button>
    <span class="historial-filtro-sep">|</span>
    <button class="historial-filter-btn" data-estado="escalada"  onclick="filtrarProcesos('escalada',this)">&#8593; Escalada</button>
    <button class="historial-filter-btn" data-estado="estable"   onclick="filtrarProcesos('estable',this)">=&nbsp;Estable</button>
    <button class="historial-filter-btn" data-estado="resolucion" onclick="filtrarProcesos('resolucion',this)">&#8595; Resuelve</button>
    <button class="historial-filter-btn" data-estado="todos"     onclick="filtrarProcesos('todos',this)">Todos</button>
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
