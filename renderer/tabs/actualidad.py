"""Pestaña Actualidad Absoluta — grandes procesos globales en curso."""

import html as _html
import json

TAB_ID    = "actualidad"
TAB_LABEL = "&#127758; Actualidad"
TAB_ICON  = "🌍"

_ESTADO_META = {
    "escalada":   ("&#8593;", "estado-escalada",   "Escalada"),
    "estable":    ("&#61;",   "estado-estable",    "Estable"),
    "resolucion": ("&#8595;", "estado-resolucion", "Resolviendo"),
    "silencio":   ("&#9675;", "estado-silencio",   "En silencio"),
}
_HORIZONTE_LABEL = {"dias": "días", "semanas": "semanas", "meses": "meses", "anos": "años"}


def _proceso_card(p: dict, hero: bool = False) -> str:
    estado    = p.get("estado", "estable")
    icono, cls_estado, label_estado = _ESTADO_META.get(estado, ("=", "estado-estable", "Estable"))
    importancia    = int(p.get("importancia") or 5)
    horizonte      = _HORIZONTE_LABEL.get(p.get("horizonte", "meses"), p.get("horizonte", "meses"))
    historial_json = _html.escape(json.dumps(p.get("historial", []), ensure_ascii=False), quote=True)
    n_arts_hoy     = len(p.get("articulos") or [])
    proceso_id     = p.get("id", "")

    arts_html = ""
    for a in (p.get("articulos") or [])[:5]:
        titulo_a = _html.escape(a.get("titulo", ""))
        fuente_a = _html.escape(a.get("fuente", ""))
        enlace_a = _html.escape(a.get("enlace", "#"), quote=True)
        arts_html += f'<li><a href="{enlace_a}" target="_blank" rel="noopener">{titulo_a}</a> <span class="proceso-art-fuente">— {fuente_a}</span></li>'

    arts_section = f'<ul class="proceso-articulos">{arts_html}</ul>' if arts_html else ""
    resumen      = _html.escape(p.get("resumen_hoy", ""))
    descripcion  = _html.escape(p.get("descripcion", ""))
    nombre       = _html.escape(p.get("nombre", ""))
    hero_cls     = " proceso-card-hero" if hero else ""
    imp_pct      = importancia * 10

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


def render(procesos: list[dict] | None = None,
           conexiones: list[dict] | None = None, **_) -> str:
    procs = procesos or []

    if not procs:
        return """
<div class="actualidad-header">
  <h2>Actualidad Absoluta</h2>
  <p>Los grandes procesos del mundo, m&#225;s all&#225; de las noticias del d&#237;a.</p>
</div>
<div class="actualidad-empty">
  <p>No hay procesos identificados a&#250;n. Se generan autom&#225;ticamente con el digest.</p>
</div>"""

    ordered   = sorted(procs, key=lambda x: int(x.get("importancia") or 0), reverse=True)
    hero_html = _proceso_card(ordered[0], hero=True) if ordered else ""
    rest_html = "\n".join(_proceso_card(p) for p in ordered[1:]) if len(ordered) > 1 else ""
    grid_html = f'<div class="proceso-grid">{rest_html}</div>' if rest_html else ""
    conn_html = _conexiones_html(conexiones or [], procs)
    n = len(procs)

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
