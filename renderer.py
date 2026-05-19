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

import os
import webbrowser
from datetime import datetime

from analyzer import COLORES_SESGO
from config import ARCHIVO_SALIDA


# ---------------------------------------------------------------------------
# CSS embebido (tema oscuro, diseño en tarjetas)
# ---------------------------------------------------------------------------

_CSS = """
/* ── Variables de diseño ─────────────────────────────────────────────── */
:root {
  --bg:          #09090b;   /* negro casi puro */
  --surface:     #18181b;   /* superficie de tarjetas */
  --surface-2:   #27272a;   /* hover / elevado */
  --border:      #3f3f46;   /* borde visible */
  --border-sub:  #27272a;   /* borde sutil */
  --txt-1:       #fafafa;   /* texto principal — máximo contraste */
  --txt-2:       #a1a1aa;   /* texto secundario */
  --txt-3:       #52525b;   /* texto muted */
  --accent:      #6366f1;   /* índigo */
  --accent-blue: #3b82f6;
  --accent-green:#22c55e;
  --r:           0.5rem;    /* radio base de bordes */
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: system-ui, 'Segoe UI', -apple-system, sans-serif;
  background: var(--bg);
  color: var(--txt-1);
  line-height: 1.65;
  font-size: 15px;
  -webkit-font-smoothing: antialiased;
}

/* ── Cabecera ────────────────────────────────────────────────────────── */
header {
  background: rgba(24, 24, 27, 0.94);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border-sub);
  padding: 0.875rem 2rem;
  position: sticky;
  top: 0;
  z-index: 200;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.header-logo { display: flex; align-items: center; gap: 0.625rem; }

.header-logo .icono {
  width: 30px;
  height: 30px;
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent-blue) 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  flex-shrink: 0;
}

.header-logo h1 {
  font-size: 1rem;
  font-weight: 700;
  color: var(--txt-1);
  letter-spacing: -0.02em;
}

header .meta {
  font-size: 0.72rem;
  color: var(--txt-3);
  text-align: right;
  line-height: 1.6;
}

/* ── Navegación ──────────────────────────────────────────────────────── */
nav {
  background: rgba(9, 9, 11, 0.9);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  padding: 0.45rem 2rem;
  display: flex;
  gap: 0.2rem;
  flex-wrap: wrap;
  border-bottom: 1px solid var(--border-sub);
  position: sticky;
  top: 53px;
  z-index: 100;
}

nav a {
  color: var(--txt-3);
  text-decoration: none;
  padding: 0.28rem 0.75rem;
  border-radius: var(--r);
  font-size: 0.78rem;
  font-weight: 500;
  letter-spacing: 0.01em;
  transition: background 0.12s, color 0.12s;
}
nav a:hover { background: var(--surface-2); color: var(--txt-1); }

/* ── Layout principal ────────────────────────────────────────────────── */
main { max-width: 1340px; margin: 0 auto; padding: 2.5rem 2rem; }

/* ── Leyenda de sesgo ────────────────────────────────────────────────── */
.leyenda {
  background: var(--surface);
  border: 1px solid var(--border-sub);
  border-radius: var(--r);
  padding: 0.8rem 1.25rem;
  margin-bottom: 3rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}
.leyenda-titulo {
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--txt-3);
  white-space: nowrap;
}
.leyenda-items { display: flex; flex-wrap: wrap; gap: 0.4rem; align-items: center; }

/* ── Secciones ───────────────────────────────────────────────────────── */
.seccion { margin-bottom: 4rem; scroll-margin-top: 105px; }

.seccion-header {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding-bottom: 0.875rem;
  border-bottom: 1px solid var(--border-sub);
  margin-bottom: 1.25rem;
}

/* barra de color vertical que identifica la sección */
.seccion-acento {
  width: 3px;
  height: 1.1rem;
  background: linear-gradient(180deg, var(--accent), var(--accent-blue));
  border-radius: 9999px;
  flex-shrink: 0;
}

.seccion-titulo {
  font-size: 1rem;
  font-weight: 700;
  color: var(--txt-1);
  letter-spacing: -0.02em;
}

/* ── Bloque de análisis crítico general ──────────────────────────────── */
.analisis-general {
  background: #0d1a2d;
  border: 1px solid #1e3a5f;
  border-left: 3px solid var(--accent-blue);
  border-radius: var(--r);
  padding: 0.9rem 1.2rem;
  margin-bottom: 1.5rem;
  color: #93c5fd;
  font-size: 0.855rem;
  line-height: 1.7;
}
.analisis-general-titulo {
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #60a5fa;
  margin-bottom: 0.45rem;
}

/* ── Grid de tarjetas ────────────────────────────────────────────────── */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 0.75rem;
}

/* ── Tarjeta de artículo ─────────────────────────────────────────────── */
.tarjeta {
  background: var(--surface);
  border: 1px solid var(--border-sub);
  border-radius: var(--r);
  padding: 1.1rem 1.15rem;
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
  transition: border-color 0.18s, box-shadow 0.18s;
}
.tarjeta:hover {
  border-color: var(--border);
  box-shadow: 0 0 0 1px var(--border), 0 12px 32px rgba(0, 0, 0, 0.5);
}

.tarjeta-meta {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.fuente-bloque { display: flex; flex-direction: column; gap: 0.15rem; }

.fuente-nombre {
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.09em;
  color: var(--txt-2);
}
.fecha { font-size: 0.62rem; color: var(--txt-3); }

.badges { display: flex; align-items: center; gap: 0.25rem; flex-wrap: wrap; }
.badge-etiqueta { font-size: 0.58rem; color: var(--txt-3); }

.badge {
  display: inline-block;
  font-size: 0.58rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  padding: 0.18rem 0.52rem;
  border-radius: 9999px;
  color: #fff;
}

/* ── Título del artículo ─────────────────────────────────────────────── */
.titulo {
  font-size: 0.93rem;
  font-weight: 600;
  line-height: 1.45;
  letter-spacing: -0.015em;
}
.titulo a { color: var(--txt-1); text-decoration: none; transition: color 0.12s; }
.titulo a:hover { color: #93c5fd; }

/* ── Resumen ─────────────────────────────────────────────────────────── */
.resumen {
  font-size: 0.8rem;
  color: var(--txt-2);
  line-height: 1.65;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex-grow: 1;
}

/* ── Crítica de IA (verde) ───────────────────────────────────────────── */
.critica {
  background: #0a1a0a;
  border: 1px solid #14532d;
  border-radius: calc(var(--r) - 1px);
  padding: 0.55rem 0.875rem;
  font-size: 0.77rem;
  color: #4ade80;
  line-height: 1.55;
  margin-top: auto;
}
.critica-icono { margin-right: 0.3rem; opacity: 0.75; }

/* ── Sin artículos ───────────────────────────────────────────────────── */
.sin-articulos { color: var(--txt-3); font-size: 0.85rem; padding: 0.5rem 0; }

/* ── Footer ──────────────────────────────────────────────────────────── */
footer {
  text-align: center;
  padding: 2rem;
  color: var(--txt-3);
  font-size: 0.7rem;
  border-top: 1px solid var(--border-sub);
  margin-top: 2rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

/* ── Barra de pestañas ───────────────────────────────────────────────── */
.tab-bar {
  background: var(--bg);
  border-bottom: 1px solid var(--border-sub);
  padding: 0 2rem;
  display: flex;
  gap: 0;
  position: sticky;
  top: 53px;
  z-index: 150;
}

.tab-btn {
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--txt-3);
  cursor: pointer;
  font-size: 0.82rem;
  font-weight: 500;
  font-family: inherit;
  letter-spacing: 0.01em;
  padding: 0.7rem 1.1rem;
  transition: color 0.15s, border-color 0.15s;
  margin-bottom: -1px;
}
.tab-btn:hover { color: var(--txt-2); }
.tab-btn.active {
  color: var(--txt-1);
  border-bottom-color: var(--accent);
}

/* ── Navegación de categorías (solo en pestaña Todas) ────────────────── */
#cat-nav {
  top: 93px;   /* debajo de header + tab-bar */
}

/* ── Tarjeta destacada (portada) ─────────────────────────────────────── */
.grid-destacadas {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
  gap: 1.25rem;
  margin-bottom: 2rem;
}

.tarjeta-destacada {
  background: var(--surface);
  border: 1px solid var(--border-sub);
  border-radius: var(--r);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
  transition: border-color 0.18s, box-shadow 0.18s;
  position: relative;
}
.tarjeta-destacada:hover {
  border-color: var(--accent);
  box-shadow: 0 0 0 1px var(--accent), 0 16px 40px rgba(0,0,0,0.5);
}

/* Indicador de categoría en la tarjeta destacada */
.tarjeta-destacada .categoria-label {
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--accent);
  margin-bottom: -0.25rem;
}

.tarjeta-destacada .titulo {
  font-size: 1.15rem;
  font-weight: 700;
  line-height: 1.35;
  letter-spacing: -0.02em;
}

.tarjeta-destacada .resumen {
  font-size: 0.855rem;
  color: var(--txt-2);
  line-height: 1.7;
  /* sin clamp — muestra el resumen completo */
  display: block;
  overflow: visible;
  -webkit-line-clamp: unset;
}

.tarjeta-destacada .critica {
  font-size: 0.825rem;
}

/* Encabezado de la sección Destacadas */
.destacadas-header {
  margin-bottom: 2rem;
  padding-bottom: 0.875rem;
  border-bottom: 1px solid var(--border-sub);
}
.destacadas-header h2 {
  font-size: 1rem;
  font-weight: 700;
  color: var(--txt-1);
  letter-spacing: -0.02em;
  margin-bottom: 0.3rem;
}
.destacadas-header p {
  font-size: 0.78rem;
  color: var(--txt-3);
}

.sin-destacadas {
  color: var(--txt-3);
  font-size: 0.875rem;
  padding: 3rem 0;
  text-align: center;
}

/* ── Buscador ────────────────────────────────────────────────────────── */
.search-bar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 2rem;
  background: var(--bg);
  border-bottom: 1px solid var(--border-sub);
  position: sticky;
  top: 93px;   /* debajo de header + tab-bar */
  z-index: 90;
}

.search-input {
  flex: 1;
  max-width: 480px;
  background: var(--surface);
  border: 1px solid var(--border-sub);
  border-radius: var(--r);
  color: var(--txt-1);
  font-family: inherit;
  font-size: 0.82rem;
  padding: 0.4rem 0.875rem;
  outline: none;
  transition: border-color 0.15s;
}
.search-input::placeholder { color: var(--txt-3); }
.search-input:focus { border-color: var(--accent); }

.search-count {
  font-size: 0.72rem;
  color: var(--txt-3);
  white-space: nowrap;
}

.tarjeta[hidden], .tarjeta-destacada[hidden], .sintesis-card[hidden] {
  display: none !important;
}

/* ── Pestaña Síntesis — acento violeta ───────────────────────────────── */
.sintesis-header {
  margin-bottom: 2rem;
  padding-bottom: 0.875rem;
  border-bottom: 1px solid var(--border-sub);
}
.sintesis-header h2 { font-size: 1rem; font-weight: 700; color: var(--txt-1); letter-spacing: -0.02em; margin-bottom: 0.3rem; }
.sintesis-header p  { font-size: 0.78rem; color: var(--txt-3); }

.grid-sintesis {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(480px, 1fr));
  gap: 1.25rem;
}

.sintesis-card {
  background: var(--surface);
  border: 1px solid var(--border-sub);
  border-top: 3px solid #7c3aed;
  border-radius: var(--r);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  transition: border-color 0.18s, box-shadow 0.18s;
}
.sintesis-card:hover {
  border-color: #7c3aed;
  box-shadow: 0 0 0 1px #7c3aed40, 0 12px 32px rgba(0,0,0,0.4);
}

.sintesis-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.sintesis-fuentes-count {
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  background: #3b0764;
  color: #c4b5fd;
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
}

.sintesis-titulo {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--txt-1);
  line-height: 1.35;
  letter-spacing: -0.02em;
}

.sintesis-texto {
  font-size: 0.855rem;
  color: var(--txt-2);
  line-height: 1.75;
  white-space: pre-line;   /* respeta los saltos de párrafo de Gemini */
}

.sintesis-fuentes {
  border-top: 1px solid var(--border-sub);
  padding-top: 0.875rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.sintesis-fuente-item {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  font-size: 0.78rem;
}

.sintesis-fuente-nombre {
  color: var(--txt-3);
  font-weight: 600;
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  white-space: nowrap;
  min-width: 110px;
}

.sintesis-fuente-link {
  color: var(--txt-2);
  text-decoration: none;
  line-height: 1.4;
  transition: color 0.12s;
}
.sintesis-fuente-link:hover { color: #c4b5fd; }

.sintesis-fuente-alt {
  font-size: 0.6rem;
  color: #f87171;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  flex-shrink: 0;
}

.sin-sintesis {
  text-align: center;
  padding: 4rem 0;
  color: var(--txt-3);
  font-size: 0.875rem;
  line-height: 1.7;
}

/* ── Pestaña Prensa Libertaria — acento rojo ─────────────────────────── */
#tab-libertaria .seccion-acento {
  background: linear-gradient(180deg, #dc2626, #f97316);
}

#tab-libertaria .seccion-titulo { color: var(--txt-1); }

#tab-libertaria .analisis-general {
  background: #1a0a0a;
  border-color: #7f1d1d;
  border-left-color: #dc2626;
  color: #fca5a5;
}
#tab-libertaria .analisis-general-titulo { color: #f87171; }

.libertaria-header {
  background: #1a0a0a;
  border: 1px solid #7f1d1d;
  border-left: 4px solid #dc2626;
  border-radius: var(--r);
  padding: 1rem 1.25rem;
  margin-bottom: 2.5rem;
  color: #fca5a5;
  font-size: 0.85rem;
  line-height: 1.65;
}
.libertaria-header strong { color: #f87171; display: block; margin-bottom: 0.3rem; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.08em; }

#tab-libertaria .tab-btn.active { border-bottom-color: #dc2626; }

/* ── Pestaña Estadísticas ────────────────────────────────────────────── */
.stats-header { margin-bottom: 2rem; padding-bottom: .875rem; border-bottom: 1px solid var(--border-sub); }
.stats-header h2 { font-size: 1rem; font-weight: 700; color: var(--txt-1); letter-spacing: -.02em; margin-bottom: .3rem; }
.stats-header p  { font-size: .78rem; color: var(--txt-3); }

.stats-kpi-row {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 2rem;
}
.stat-kpi {
  background: var(--surface);
  border: 1px solid var(--border-sub);
  border-radius: var(--r);
  padding: 1.25rem 1.5rem;
  min-width: 150px;
}
.stat-kpi-valor {
  font-size: 2.2rem;
  font-weight: 800;
  color: var(--accent);
  letter-spacing: -.04em;
  line-height: 1;
}
.stat-kpi-label {
  font-size: .68rem;
  color: var(--txt-3);
  margin-top: .4rem;
  line-height: 1.4;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.25rem;
}
.stat-card {
  background: var(--surface);
  border: 1px solid var(--border-sub);
  border-radius: var(--r);
  padding: 1.25rem 1.5rem;
}
.stat-card-title {
  font-size: .62rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .1em;
  color: var(--txt-3);
  margin-bottom: 1rem;
}
.stat-bar-row {
  display: flex;
  align-items: center;
  gap: .75rem;
  margin-bottom: .55rem;
}
.stat-bar-label {
  font-size: .72rem;
  color: var(--txt-2);
  min-width: 120px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.stat-bar-bg {
  flex: 1;
  background: var(--surface-2);
  border-radius: 9999px;
  height: 5px;
  min-width: 40px;
}
.stat-bar-fill {
  height: 5px;
  border-radius: 9999px;
  min-width: 2px;
  transition: width .6s cubic-bezier(.4,0,.2,1);
}
.stat-bar-count {
  font-size: .7rem;
  color: var(--txt-3);
  min-width: 22px;
  text-align: right;
}

/* Filtro de sesgo en leyenda */
.leyenda-items .badge {
  cursor: pointer;
  transition: opacity .15s, box-shadow .15s;
  user-select: none;
}
.leyenda-items .badge:hover { opacity: .8; }
.leyenda-items .badge.filtro-activo {
  box-shadow: 0 0 0 2px #fff, 0 0 0 4px var(--accent);
}
.leyenda-tip {
  font-size: .65rem;
  color: var(--txt-3);
  font-style: italic;
}
.filtro-aviso {
  font-size: .7rem;
  color: var(--accent);
  font-weight: 600;
}
.filtro-clear-btn {
  background: none;
  border: 1px solid var(--border);
  color: var(--txt-2);
  border-radius: var(--r);
  padding: .15rem .55rem;
  font-size: .65rem;
  cursor: pointer;
  font-family: inherit;
  transition: background .12s;
}
.filtro-clear-btn:hover { background: var(--surface-2); color: var(--txt-1); }
"""


# ---------------------------------------------------------------------------
# Constructores de bloques HTML
# ---------------------------------------------------------------------------

def _badge(sesgo: str) -> str:
    """Genera la etiqueta coloreada de sesgo."""
    color = COLORES_SESGO.get(sesgo, COLORES_SESGO["desconocido"])
    return f'<span class="badge" style="background:{color}">{sesgo.upper()}</span>'


def _tarjeta(articulo: dict) -> str:
    """Construye la tarjeta HTML de un artículo individual."""
    critica = (articulo.get("critica") or "").strip()
    critica_html = (
        f'<div class="critica">'
        f'<span class="critica-icono">💡</span>{critica}'
        f'</div>'
        if critica else ""
    )

    sesgo_fuente = articulo.get("sesgo_fuente") or "desconocido"
    sesgo_ia     = articulo.get("sesgo_ia")     or "desconocido"
    search_data  = f'{articulo["titulo"].lower()} {articulo["fuente"].lower()} {(articulo.get("resumen") or "").lower()}'
    return f"""
<div class="tarjeta" data-search="{search_data}" data-sesgo-fuente="{sesgo_fuente}" data-sesgo-ia="{sesgo_ia}">
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


def _seccion(categoria: str, articulos: list[dict], analisis: str) -> str:
    """Construye la sección HTML de una categoría completa."""
    id_seccion = categoria.lower().replace(" ", "-")

    if articulos:
        tarjetas = "\n".join(_tarjeta(a) for a in articulos)
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


def _featured_card(articulo: dict, categoria: str) -> str:
    """Tarjeta grande para la pestaña Destacadas."""
    critica = (articulo.get("critica") or "").strip()
    critica_html = (
        f'<div class="critica"><span class="critica-icono">💡</span>{critica}</div>'
        if critica else ""
    )
    search_data_d = f'{articulo["titulo"].lower()} {articulo["fuente"].lower()} {categoria.lower()}'
    return f"""
<div class="tarjeta-destacada" data-search="{search_data_d}">
  <div class="tarjeta-meta">
    <div class="fuente-bloque">
      <span class="categoria-label">{categoria}</span>
      <span class="fuente-nombre">{articulo["fuente"]}</span>
      <span class="fecha">{articulo["fecha"]}</span>
    </div>
    <div class="badges">
      <span class="badge-etiqueta">Fuente:</span>
      {_badge(articulo.get("sesgo_fuente") or "desconocido")}
      <span class="badge-etiqueta">IA:</span>
      {_badge(articulo.get("sesgo_ia") or "desconocido")}
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
    """Tarjeta de síntesis para una historia cubierta por múltiples fuentes."""
    n = len(grupo["articulos"])
    fuentes_html = ""
    for art in grupo["articulos"]:
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

    return f"""
<div class="sintesis-card" data-search="{grupo['titulo'].lower()} {' '.join(a['fuente'].lower() for a in grupo['articulos'])}">
  <div class="sintesis-meta">
    <span class="sintesis-fuentes-count">{n} fuente{"s" if n != 1 else ""}</span>
  </div>
  <div class="sintesis-titulo">{grupo["titulo"]}</div>
  <div class="sintesis-texto">{grupo["sintesis"]}</div>
  <div class="sintesis-fuentes">
    {fuentes_html}
  </div>
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


def _tab_libertaria(alternativas: dict[str, list[dict]], analisis_alt: dict[str, str]) -> str:
    """Genera el contenido de la pestaña Prensa Libertaria."""
    if not alternativas or not any(alternativas.values()):
        return '<p class="sin-articulos" style="padding:3rem 0;text-align:center">No se encontraron artículos en fuentes alternativas.</p>'

    secciones = "\n".join(
        _seccion(cat, arts, analisis_alt.get(cat, ""))
        for cat, arts in alternativas.items()
    )

    aviso = """<div class="libertaria-header">
  <strong>⚡ Prensa Libertaria y Contrainformación</strong>
  Fuentes anarquistas, libertarias y de contrainformación. Perspectivas
  críticas con el orden establecido, el Estado y el capitalismo.
  Como en el resto del digest, el análisis de sesgo es orientativo.
</div>"""

    return aviso + "\n" + secciones


def _tab_destacadas(noticias: dict[str, list[dict]]) -> str:
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

    cards = "\n".join(_featured_card(a, cat) for cat, a in seleccionados)
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

    destacadas  = _tab_destacadas(noticias)
    libertaria  = _tab_libertaria(alternativas or {}, analisis_alt or {})
    sintesis    = _tab_sintesis(grupos_sintesis or [])
    estadisticas = _tab_estadisticas()
    total_alt   = sum(len(a) for a in (alternativas or {}).values())
    n_sintesis  = len(grupos_sintesis) if grupos_sintesis else 0

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

<div class="tab-bar">
  <button class="tab-btn active" data-tab="destacadas" onclick="switchTab('destacadas')">
    &#9733; Destacadas
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
  <button class="tab-btn" data-tab="estadisticas" onclick="switchTab('estadisticas')">
    &#128200; Estad&#237;sticas
  </button>
</div>

<div class="search-bar">
  <input class="search-input" id="buscador" type="search"
         placeholder="Buscar en noticias..." autocomplete="off"
         oninput="buscar(this.value)">
  <span class="search-count" id="search-count"></span>
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

  <div id="tab-sintesis" class="tab-content">
    {sintesis}
  </div>

  <div id="tab-libertaria" class="tab-content">
    {libertaria}
  </div>

  <div id="tab-estadisticas" class="tab-content">
    {estadisticas}
  </div>

</main>

<footer>
  Sin publicidad · Sin algoritmos · Generado localmente ·
  Análisis por Google Gemini
</footer>

<script>
var _tabActual    = 'destacadas';
var _filtroSesgo  = null;
var _statsReady   = false;
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
  document.getElementById('tab-' + name).style.display = 'block';
  document.querySelector('[data-tab="' + name + '"]').classList.add('active');

  var nav = document.getElementById('cat-nav');
  if (nav) nav.style.display = name === 'todas' ? 'flex' : 'none';

  // La barra de búsqueda y el filtro solo tienen sentido fuera de Estadísticas
  var barra = document.querySelector('.search-bar');
  if (barra) barra.style.display = name === 'estadisticas' ? 'none' : 'flex';

  if (name === 'estadisticas') {{
    if (!_statsReady) {{ renderEstadisticas(); _statsReady = true; }}
  }} else {{
    var q = document.getElementById('buscador').value;
    if (q) buscar(q); else _limpiarContador();
  }}
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

/* ── Inicio ──────────────────────────────────────────────────────────── */
(function() {{
  var last = 'destacadas';
  try {{ last = localStorage.getItem('digestTab') || 'destacadas'; }} catch(e) {{}}
  switchTab(last);
}})();
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
