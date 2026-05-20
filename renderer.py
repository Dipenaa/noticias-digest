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


# ---------------------------------------------------------------------------
# CSS embebido (tema oscuro, diseño en tarjetas)
# ---------------------------------------------------------------------------

_CSS = """
/* ── Variables de diseño — tema Bosque Vivo ──────────────────────────── */
:root {
  --bg:          #060e08;   /* verde casi negro */
  --surface:     #0c1a10;   /* superficie de tarjetas — bosque oscuro */
  --surface-2:   #132018;   /* hover / elevado */
  --border:      #2a5435;   /* borde visible — verde selva */
  --border-sub:  #162b1c;   /* borde sutil */
  --txt-1:       #edfaf1;   /* texto principal — blanco ligeramente verde */
  --txt-2:       #86efac;   /* texto secundario — verde suave */
  --txt-3:       #4a7a58;   /* texto muted — verde apagado */
  --accent:      #22c55e;   /* esmeralda vivo */
  --accent-blue: #34d399;   /* teal-verde (reemplaza azul) */
  --accent-green:#4ade80;   /* verde claro */
  --accent-gold: #fbbf24;   /* dorado — contraste cálido */
  --r:           0.5rem;    /* radio base de bordes */
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: system-ui, 'Segoe UI', -apple-system, sans-serif;
  background:
    radial-gradient(ellipse 80% 40% at 15% 10%, rgba(34,197,94,0.07) 0%, transparent 60%),
    radial-gradient(ellipse 60% 50% at 85% 80%, rgba(52,211,153,0.06) 0%, transparent 60%),
    radial-gradient(ellipse 40% 30% at 50% 50%, rgba(16,185,129,0.03) 0%, transparent 70%),
    var(--bg);
  color: var(--txt-1);
  line-height: 1.65;
  font-size: 15px;
  -webkit-font-smoothing: antialiased;
}

/* ── Cabecera ────────────────────────────────────────────────────────── */
header {
  background: linear-gradient(135deg, rgba(10,22,13,0.97) 0%, rgba(6,14,8,0.97) 100%);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border-sub);
  box-shadow: 0 1px 0 rgba(34,197,94,0.15), 0 4px 24px rgba(0,0,0,0.5);
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
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #16a34a 0%, #22c55e 50%, #4ade80 100%);
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
  box-shadow: 0 0 12px rgba(34,197,94,0.45);
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
  width: 4px;
  height: 1.2rem;
  background: linear-gradient(180deg, #4ade80, #22c55e, #16a34a);
  border-radius: 9999px;
  flex-shrink: 0;
  box-shadow: 0 0 6px rgba(34,197,94,0.5);
}

.seccion-titulo {
  font-size: 1rem;
  font-weight: 700;
  color: var(--txt-1);
  letter-spacing: -0.02em;
}

/* ── Bloque de análisis crítico general ──────────────────────────────── */
.analisis-general {
  background: #071409;
  border: 1px solid #1e4827;
  border-left: 3px solid var(--accent);
  border-radius: var(--r);
  padding: 0.9rem 1.2rem;
  margin-bottom: 1.5rem;
  color: #86efac;
  font-size: 0.855rem;
  line-height: 1.7;
}
.analisis-general-titulo {
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #4ade80;
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
  border-color: var(--accent);
  box-shadow: 0 0 0 1px rgba(34,197,94,0.3), 0 0 20px rgba(34,197,94,0.08), 0 12px 32px rgba(0,0,0,0.5);
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
.titulo a:hover { color: var(--accent-green); }

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
  background: linear-gradient(135deg, #071409 0%, #091c0c 100%);
  border: 1px solid #1a4a27;
  border-left: 2px solid #22c55e;
  border-radius: calc(var(--r) - 1px);
  padding: 0.55rem 0.875rem;
  font-size: 0.77rem;
  color: #86efac;
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

/* ── Contenido de pestañas (oculto por defecto; JS muestra el activo) ── */
.tab-content { display: none; }

/* ── Barra de pestañas ───────────────────────────────────────────────── */
.tab-bar {
  background: linear-gradient(180deg, rgba(8,16,10,0.98) 0%, rgba(6,14,8,0.98) 100%);
  border-bottom: 1px solid var(--border-sub);
  padding: 0 2rem;
  display: flex;
  gap: 0;
  position: sticky;
  top: 60px;
  z-index: 150;
}

.tab-btn {
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  color: #7ab08a;
  cursor: pointer;
  font-size: 0.82rem;
  font-weight: 500;
  font-family: inherit;
  letter-spacing: 0.01em;
  padding: 0.7rem 1.1rem;
  transition: color 0.15s, border-color 0.15s;
  margin-bottom: -1px;
}
.tab-btn:hover { color: #a7d9b5; }
.tab-btn.active {
  color: var(--txt-1);
  border-bottom-color: var(--accent);
}

/* ── Navegación de categorías (solo en pestaña Todas) ────────────────── */
#cat-nav {
  top: 140px;   /* debajo de header (60px) + tab-bar (40px) + search-bar (40px) */
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
  box-shadow: 0 0 0 1px rgba(34,197,94,0.4), 0 0 30px rgba(34,197,94,0.1), 0 16px 40px rgba(0,0,0,0.5);
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
  top: 100px;   /* debajo de header (60px) + tab-bar (40px) */
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
  background: linear-gradient(160deg, #0c1a10 0%, #0a1a0d 100%);
  border: 1px solid var(--border-sub);
  border-top: 3px solid #22c55e;
  border-radius: var(--r);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  transition: border-color 0.18s, box-shadow 0.18s;
}
.sintesis-card:hover {
  border-color: var(--accent);
  box-shadow: 0 0 0 1px rgba(34,197,94,0.25), 0 0 24px rgba(34,197,94,0.08), 0 12px 32px rgba(0,0,0,0.4);
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
  background: #052e16;
  color: #4ade80;
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
  border: 1px solid #166534;
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
.sintesis-fuente-link:hover { color: var(--accent-green); }

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
  background: linear-gradient(135deg, #22c55e, #4ade80);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
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

/* ── Vista inmersiva (drawer lateral) ───────────────────────────────── */
.drawer-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.65);
  z-index: 500;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.25s;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}
.drawer-overlay.open { opacity: 1; pointer-events: all; }

.drawer {
  position: fixed;
  top: 0;
  right: 0;
  height: 100%;
  width: min(560px, 100vw);
  background: var(--surface);
  border-left: 1px solid var(--border);
  z-index: 501;
  display: flex;
  flex-direction: column;
  transform: translateX(100%);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.drawer.open { transform: translateX(0); }

.drawer-header {
  padding: 1.1rem 1.5rem;
  border-bottom: 1px solid var(--border-sub);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  flex-shrink: 0;
}
.drawer-header-meta { display: flex; flex-direction: column; gap: 0.3rem; min-width: 0; }
.drawer-categoria {
  font-size: 0.6rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--accent);
}
.drawer-fuente-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.drawer-reading {
  font-size: 0.65rem;
  color: var(--txt-3);
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.drawer-close {
  background: none;
  border: 1px solid var(--border-sub);
  color: var(--txt-2);
  border-radius: var(--r);
  width: 30px;
  height: 30px;
  cursor: pointer;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background 0.12s, color 0.12s;
}
.drawer-close:hover { background: var(--surface-2); color: var(--txt-1); }

.drawer-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.drawer-badges { display: flex; align-items: center; gap: 0.35rem; flex-wrap: wrap; }
.drawer-titulo {
  font-size: 1.2rem;
  font-weight: 700;
  line-height: 1.4;
  letter-spacing: -0.025em;
  color: var(--txt-1);
}
.drawer-resumen {
  font-size: 0.88rem;
  color: var(--txt-2);
  line-height: 1.8;
}
.drawer-critica {
  background: #0a1a0a;
  border: 1px solid #14532d;
  border-radius: calc(var(--r) - 1px);
  padding: 0.875rem 1rem;
  font-size: 0.82rem;
  color: #4ade80;
  line-height: 1.65;
}

.drawer-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-sub);
  display: flex;
  gap: 0.75rem;
  flex-shrink: 0;
}
.drawer-btn {
  flex: 1;
  padding: 0.6rem 1rem;
  border-radius: var(--r);
  font-size: 0.82rem;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  border: none;
  transition: background 0.15s;
  text-decoration: none;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
}
.drawer-btn-primary { background: var(--accent); color: #fff; }
.drawer-btn-primary:hover { background: #4f46e5; }
.drawer-btn-secondary { background: var(--surface-2); color: var(--txt-1); border: 1px solid var(--border-sub); }
.drawer-btn-secondary:hover { background: var(--border); }

/* Clic en tarjeta abre el drawer */
.tarjeta, .tarjeta-destacada { cursor: pointer; }
.tarjeta:active, .tarjeta-destacada:active { transform: scale(0.995); }
.tarjeta .titulo a, .tarjeta-destacada .titulo a { cursor: pointer; }

/* ── Sentimiento ─────────────────────────────────────────────────────── */
.badge-sent {
  font-size: 0.55rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  padding: 0.15rem 0.45rem;
  border-radius: 9999px;
}
.badge-sent-alarmista { background: #450a0a; color: #fca5a5; }
.badge-sent-neutral   { background: #27272a; color: #71717a; }
.badge-sent-optimista { background: #052e16; color: #86efac; }

/* ── Badge multi-fuente verificado ───────────────────────────────────── */
.badge-verified {
  font-size: 0.55rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  background: #1e1b4b;
  color: #a5b4fc;
}

/* ── Bookmark ────────────────────────────────────────────────────────── */
.bookmark-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  color: var(--txt-3);
  padding: 0.1rem 0.2rem;
  border-radius: 4px;
  line-height: 1;
  transition: color 0.15s, transform 0.1s;
  flex-shrink: 0;
}
.bookmark-btn:hover { color: #fbbf24; transform: scale(1.15); }
.bookmark-btn.guardado { color: #fbbf24; }

/* ── Resaltado de palabras clave ─────────────────────────────────────── */
.tarjeta.kw-match, .tarjeta-destacada.kw-match {
  border-left: 3px solid #f59e0b;
}
.keywords-input {
  width: 200px;
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
.keywords-input::placeholder { color: var(--txt-3); }
.keywords-input:focus { border-color: #f59e0b; }
.kw-sep { color: var(--border); font-size: 1.1rem; user-select: none; }

/* ── Pestaña Asombro ─────────────────────────────────────────────────── */
#tab-asombro { padding: 1rem; }
.asombro-header { text-align: center; padding: 2rem 0 1.5rem; }
.asombro-header h2 { font-size: 1.4rem; font-weight: 700; color: var(--txt-1); margin-bottom: .5rem; }
.asombro-header p { font-size: .85rem; color: var(--txt-3); max-width: 520px; margin: 0 auto; line-height: 1.7; }
.asombro-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px,1fr)); gap: 1.25rem; max-width: 1400px; margin: 0 auto; }
.asombro-card {
  background: var(--surface);
  border: 1px solid var(--border-sub);
  border-radius: var(--r);
  padding: 1.25rem;
  cursor: pointer;
  transition: transform .15s, border-color .15s, box-shadow .15s;
}
.asombro-card:hover { transform: translateY(-2px); border-color: #7c3aed; box-shadow: 0 4px 20px rgba(124,58,237,.15); }
.asombro-score { font-size: 1rem; color: #a78bfa; margin-bottom: .45rem; letter-spacing: .1em; }
.asombro-cat { display: inline-block; font-size: .65rem; text-transform: uppercase; letter-spacing: .08em; color: #7c3aed; background: rgba(124,58,237,.1); border: 1px solid rgba(124,58,237,.3); border-radius: 9999px; padding: .1rem .5rem; margin-bottom: .6rem; }
.asombro-titulo { font-size: .95rem; font-weight: 600; color: var(--txt-1); margin-bottom: .35rem; line-height: 1.4; }
.asombro-titulo a { color: inherit; text-decoration: none; }
.asombro-titulo a:hover { color: #a78bfa; }
.asombro-fuente { font-size: .72rem; color: var(--txt-3); margin-bottom: .6rem; }
.asombro-razon { font-size: .8rem; color: #c4b5fd; font-style: italic; margin-bottom: .6rem; line-height: 1.5; }
.asombro-resumen { font-size: .8rem; color: var(--txt-2); line-height: 1.6; }
.asombro-empty { text-align: center; padding: 5rem 1rem; color: var(--txt-3); }
.asombro-empty-icon { font-size: 3rem; margin-bottom: 1rem; }
.tab-btn[data-tab="asombro"].active { border-bottom-color: #7c3aed !important; color: #a78bfa !important; }

/* ── Barra de ordenación ─────────────────────────────────────────────── */
.sort-bar {
  position: sticky;
  top: 140px;
  z-index: 89;
  background: var(--bg);
  padding: .35rem 1rem;
  display: flex;
  align-items: center;
  gap: .35rem;
  flex-wrap: wrap;
  border-bottom: 1px solid var(--border-sub);
}
.sort-label { font-size: .72rem; color: var(--txt-3); margin-right: .15rem; white-space: nowrap; }
.sort-btn {
  font-size: .7rem;
  padding: .18rem .55rem;
  border-radius: 9999px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--txt-2);
  cursor: pointer;
  transition: background .15s, color .15s;
  white-space: nowrap;
}
.sort-btn:hover { background: var(--surface-2); color: var(--txt-1); }
.sort-btn.active { background: var(--accent); color: #000; border-color: var(--accent); font-weight: 600; }

/* ── Pestaña Para Leer ───────────────────────────────────────────────── */
.para-leer-header { margin-bottom: 1.5rem; padding-bottom: .875rem; border-bottom: 1px solid var(--border-sub); }
.para-leer-header h2 { font-size: 1rem; font-weight: 700; color: var(--txt-1); letter-spacing: -.02em; margin-bottom: .3rem; }
.para-leer-header p  { font-size: .78rem; color: var(--txt-3); }
.para-leer-empty { text-align: center; padding: 4rem 0; color: var(--txt-3); font-size: .875rem; line-height: 1.7; }
.tab-count { font-size: .6rem; background: var(--accent); color: #fff; border-radius: 9999px; padding: .1rem .45rem; margin-left: .3rem; vertical-align: middle; }

/* ── Comparador de ángulos (dentro de síntesis) ──────────────────────── */
.angulos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: .75rem;
  border-top: 1px solid var(--border-sub);
  padding-top: .875rem;
}
.angulo-col { display: flex; flex-direction: column; gap: .4rem; }
.angulo-label {
  font-size: .58rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .08em;
  color: var(--txt-3);
  margin-bottom: .1rem;
}
.angulo-item { font-size: .75rem; }
.angulo-item a { color: var(--txt-2); text-decoration: none; line-height: 1.4; }
.angulo-item a:hover { color: var(--txt-1); }

/* ── Banner IA faltante ──────────────────────────────────────────────── */
#ia-banner {
  display: none;
  align-items: center;
  gap: .75rem;
  background: #1c1917;
  border: 1px solid #78350f;
  border-radius: var(--r);
  padding: .6rem 1rem;
  margin: .75rem var(--pad-x);
  font-size: .8rem;
  color: #fbbf24;
}
#ia-banner .ia-msg { flex: 1; }
#ia-banner .ia-regen {
  background: #92400e;
  color: #fef3c7;
  border: none;
  border-radius: var(--r);
  padding: .35rem .875rem;
  font-size: .78rem;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  white-space: nowrap;
  transition: background .15s;
}
#ia-banner .ia-regen:hover { background: #b45309; }
#ia-banner .ia-regen:disabled { opacity: .5; cursor: default; }
#ia-banner .ia-close {
  background: none;
  border: none;
  color: #92400e;
  cursor: pointer;
  font-size: 1.1rem;
  line-height: 1;
  padding: 0 .15rem;
}
"""


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
  <div class="drawer-footer">
    <a class="drawer-btn drawer-btn-primary" id="d-btn-leer" href="#"
       target="_blank" rel="noopener noreferrer">
      Leer art&#237;culo completo &#8599;
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
