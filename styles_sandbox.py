"""
styles_sandbox.py — CSS del sandbox de diseño. Editar aquí sin tocar producción.
"""

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── Variables — Terminal Editorial ─────────────────────────────────────── */
:root {
  --bg:          #18181f;
  --surface:     #1f1f29;
  --surface-2:   #272735;
  --border:      rgba(255,255,255,0.09);
  --border-sub:  rgba(255,255,255,0.05);
  --txt-1:       #eaeaf5;
  --txt-2:       #8888aa;
  --txt-3:       #44445c;
  --accent:      #4f8ef7;
  --accent-blue: #7c72f0;
  --accent-green:#2dd4a0;
  --accent-gold: #f59e0b;
  --r:           6px;
  --font-serif:  'Playfair Display', Georgia, serif;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  background-color: var(--bg);
  color: var(--txt-1);
  line-height: 1.6;
  font-size: 15px;
  -webkit-font-smoothing: antialiased;
}

/* ── Cabecera ────────────────────────────────────────────────────────────── */
header {
  background: rgba(24,24,31,0.97);
  border-bottom: 1px solid var(--border-sub);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  padding: 0 2rem;
  height: 56px;
  position: sticky;
  top: 0;
  z-index: 200;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.header-logo { display: flex; align-items: center; gap: 0.75rem; }

.header-logo .icono {
  width: 28px; height: 28px;
  background: var(--accent);
  border-radius: 5px;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; flex-shrink: 0;
}

.header-logo h1 {
  font-size: 0.88rem; font-weight: 700;
  color: var(--txt-1); letter-spacing: -0.01em;
}

header .meta {
  font-size: 0.67rem; color: var(--txt-3);
  text-align: right; line-height: 1.6;
}

/* ── Navegación de categorías ────────────────────────────────────────────── */
nav {
  background: rgba(24,24,31,0.95);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  padding: 0 2rem;
  height: 36px;
  display: flex; align-items: center; gap: 0.15rem;
  border-bottom: 1px solid var(--border-sub);
  position: sticky; top: 56px; z-index: 100;
  overflow-x: auto;
}

nav a {
  color: var(--txt-3); text-decoration: none;
  padding: 0.2rem 0.6rem; border-radius: 3px;
  font-size: 0.7rem; font-weight: 500; letter-spacing: 0.01em;
  transition: background 0.12s, color 0.12s; white-space: nowrap;
}
nav a:hover { background: var(--surface-2); color: var(--txt-2); }

/* ── Layout principal ────────────────────────────────────────────────────── */
main { max-width: 1320px; margin: 0 auto; padding: 2.5rem 2rem; }

/* ── Leyenda de sesgo ────────────────────────────────────────────────────── */
.leyenda {
  background: none;
  border: none;
  border-bottom: 1px solid var(--border-sub);
  border-radius: 0;
  padding: 0 0 0.75rem; margin-bottom: 2.75rem;
  display: flex; align-items: center; gap: 0.875rem; flex-wrap: wrap;
}
.leyenda-titulo {
  font-size: 0.55rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.16em;
  color: var(--txt-3); white-space: nowrap;
}
.leyenda-items { display: flex; flex-wrap: wrap; gap: 0.3rem; align-items: center; }

/* ── Secciones ───────────────────────────────────────────────────────────── */
.seccion { margin-bottom: 5rem; scroll-margin-top: 100px; }

.seccion-header {
  display: flex; align-items: baseline;
  justify-content: space-between;
  padding-bottom: 0.875rem;
  border-bottom: 2px solid var(--border);
  margin-bottom: 1.75rem;
}

.seccion-acento { display: none; }

.seccion-titulo {
  font-size: 0.95rem; font-weight: 700;
  letter-spacing: -0.01em;
  color: var(--txt-1);
}

/* ── Análisis general ────────────────────────────────────────────────────── */
.analisis-general {
  background: none;
  border: none;
  border-left: 2px solid var(--border);
  border-radius: 0;
  padding: 0.4rem 0 0.4rem 1rem; margin-bottom: 1.75rem;
  color: var(--txt-3); font-size: 0.77rem; line-height: 1.7;
}
.analisis-general-titulo { display: none; }

/* ── Grid de tarjetas ────────────────────────────────────────────────────── */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
  gap: 0.75rem;
}

/* ── Tarjeta de artículo ─────────────────────────────────────────────────── */
.tarjeta {
  background: var(--surface);
  border: 1px solid var(--border-sub);
  border-radius: var(--r);
  padding: 1.5rem 1.75rem;
  display: flex; flex-direction: column; gap: 0.9rem;
  transition: background 0.15s, border-color 0.15s;
}
.tarjeta:hover { background: var(--surface-2); border-color: var(--border); }

/* Primera tarjeta de cada sección: ocupa toda la anchura */
.grid .tarjeta:first-child {
  grid-column: 1 / -1;
}
.grid .tarjeta:first-child .titulo {
  font-size: 1.35rem;
}
.grid .tarjeta:first-child .resumen {
  -webkit-line-clamp: 5;
  font-size: 0.85rem;
}

/* Meta: columna — fuente arriba, badges abajo */
.tarjeta-meta {
  display: flex; flex-direction: column;
  gap: 0.55rem;
}

/* Fila superior: nombre de fuente + fecha */
.fuente-bloque {
  display: flex; flex-direction: row;
  align-items: center; justify-content: space-between;
  gap: 0.5rem;
}

.fuente-nombre {
  font-size: 0.75rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.06em;
  color: var(--txt-1);
}
.fecha { font-size: 0.62rem; color: var(--txt-3); flex-shrink: 0; }

/* Fila de badges */
.badges { display: flex; align-items: center; gap: 0.45rem; flex-wrap: wrap; }

/* Base badge (leyenda filters, drawer, synthesis) — colored pill */
.badge {
  display: inline-block; font-size: 0.56rem; font-weight: 700;
  letter-spacing: 0.05em; padding: 0.15rem 0.5rem;
  border-radius: 3px; color: #fff;
}

/* "Fuente:" / "IA:" micro-labels */
.badge-etiqueta {
  font-size: 0.44rem; font-weight: 700;
  letter-spacing: 0.1em; text-transform: uppercase;
  color: var(--txt-3); display: inline-block;
}

/* ── Bias spectrum bars (card view only) ─────────────────────────────── */
/* Override the colored-pill badge with a positional spectrum bar */
.badges .badge {
  display: inline-block;
  background: none !important; /* override Python inline style */
  border: none;
  padding: 0;
  font-size: 0;                /* hide IZQ / CTR / DER text */
  position: relative;
  width: 52px;
  height: 10px;
  vertical-align: middle;
  flex-shrink: 0;
  cursor: help;
}

/* Spectrum track */
.badges .badge::before {
  content: '';
  position: absolute;
  left: 0; right: 0;
  top: 50%; transform: translateY(-50%);
  height: 2px;
  background: linear-gradient(to right,
    #4f8ef7 0%, #7baff7 25%, #6b7280 50%, #f07040 75%, #ef4444 100%
  );
  border-radius: 2px;
  opacity: 0.28;
}

/* Position dot */
.badges .badge::after {
  content: '';
  position: absolute;
  width: 8px; height: 8px;
  border-radius: 50%;
  top: 50%; transform: translateY(-50%);
  background: var(--dot-color, #6b7280);
  left: var(--dot-left, 22px);
  border: 1.5px solid var(--surface);
  box-shadow: 0 1px 4px rgba(0,0,0,0.4);
}

/* Dot position + color per sesgo level */
.badges .badge[title="izquierda"]        { --dot-left: 1px;  --dot-color: #4f8ef7; }
.badges .badge[title="centro-izquierda"] { --dot-left: 11px; --dot-color: #7baff7; }
.badges .badge[title="centro"]           { --dot-left: 22px; --dot-color: #7a7a8a; }
.badges .badge[title="centro-derecha"]   { --dot-left: 33px; --dot-color: #f07040; }
.badges .badge[title="derecha"]          { --dot-left: 43px; --dot-color: #ef4444; }
.badges .badge[title="desconocido"]::before { opacity: 0.08; }
.badges .badge[title="desconocido"]::after  { display: none; }

/* Drawer badges: also get spectrum bars (title set by JS patch in sandbox) */
.drawer-badges .badge {
  display: inline-block;
  background: none !important;
  border: none; padding: 0; font-size: 0;
  position: relative; width: 64px; height: 12px;
  vertical-align: middle; flex-shrink: 0; cursor: help;
}
.drawer-badges .badge::before {
  content: '';
  position: absolute; left: 0; right: 0;
  top: 50%; transform: translateY(-50%);
  height: 2px;
  background: linear-gradient(to right, #4f8ef7, #7baff7, #6b7280, #f07040, #ef4444);
  border-radius: 2px; opacity: 0.3;
}
.drawer-badges .badge::after {
  content: '';
  position: absolute; width: 10px; height: 10px;
  border-radius: 50%;
  top: 50%; transform: translateY(-50%);
  background: var(--dot-color, #6b7280);
  left: var(--dot-left, 27px);
  border: 2px solid #17171f;
  box-shadow: 0 1px 4px rgba(0,0,0,0.5);
}
.drawer-badges .badge[title="izquierda"]        { --dot-left: 1px;  --dot-color: #4f8ef7; }
.drawer-badges .badge[title="centro-izquierda"] { --dot-left: 14px; --dot-color: #7baff7; }
.drawer-badges .badge[title="centro"]           { --dot-left: 27px; --dot-color: #7a7a8a; }
.drawer-badges .badge[title="centro-derecha"]   { --dot-left: 40px; --dot-color: #f07040; }
.drawer-badges .badge[title="derecha"]          { --dot-left: 53px; --dot-color: #ef4444; }
.drawer-badges .badge[title="desconocido"]::before { opacity: 0.08; }
.drawer-badges .badge[title="desconocido"]::after  { display: none; }

/* ── Título del artículo ─────────────────────────────────────────────────── */
.titulo {
  font-family: var(--font-serif);
  font-size: 1.12rem; font-weight: 700;
  line-height: 1.3; letter-spacing: -0.01em;
}
.titulo a { color: var(--txt-1); text-decoration: none; transition: color 0.12s; }
.titulo a:hover { color: var(--accent); }

/* ── Resumen ─────────────────────────────────────────────────────────────── */
.resumen {
  font-size: 0.83rem; color: var(--txt-2); line-height: 1.7;
  display: -webkit-box; -webkit-line-clamp: 4;
  -webkit-box-orient: vertical; overflow: hidden; flex-grow: 1;
}

/* ── Crítica de IA — footer de la card ───────────────────────────────────── */
.critica {
  background: none;
  border: none;
  border-top: 1px solid var(--border-sub);
  border-radius: 0;
  padding: 0.75rem 0 0;
  font-size: 0.72rem; color: var(--txt-3); line-height: 1.6;
  margin-top: auto;
}
.critica::before {
  content: 'ANÁLISIS IA';
  display: block;
  font-size: 0.5rem; font-weight: 800;
  letter-spacing: 0.16em; color: var(--accent);
  margin-bottom: 0.35rem;
}
.critica-icono { display: none; }

/* ── Sin artículos ───────────────────────────────────────────────────────── */
.sin-articulos { color: var(--txt-3); font-size: 0.85rem; padding: 0.5rem 0; }

/* ── Footer ──────────────────────────────────────────────────────────────── */
footer {
  text-align: center; padding: 2rem;
  color: var(--txt-3); font-size: 0.62rem;
  border-top: 1px solid var(--border-sub); margin-top: 2rem;
  letter-spacing: 0.07em; text-transform: uppercase;
}

/* ── Pestañas (ocultas por defecto) ─────────────────────────────────────── */
.tab-content { display: none; }

/* ── Sidebar ─────────────────────────────────────────────────────────────── */
.tab-bar {
  position: fixed; left: 0; top: 0; bottom: 0; width: 210px;
  background: #111119;
  border-right: 1px solid var(--border-sub);
  padding: 3.5rem 0 5rem;
  display: flex; flex-direction: column; gap: 0;
  z-index: 100; overflow-y: auto; overflow-x: hidden;
}

.tab-bar::before {
  content: 'DIGEST';
  position: absolute; top: 0; left: 0; right: 0; height: 3.5rem;
  display: flex; align-items: center; padding: 0 1.25rem;
  font-weight: 800; font-size: 0.68rem; letter-spacing: 0.2em;
  color: var(--txt-1); border-bottom: 1px solid var(--border-sub);
}

.tab-bar-section {
  font-size: 0.52rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.16em;
  color: var(--txt-3); padding: 1.25rem 1.25rem 0.4rem; user-select: none;
}

.tab-btn {
  background: none; border: none;
  border-left: 2px solid transparent;
  color: var(--txt-3); cursor: pointer;
  font-size: 0.76rem; font-weight: 500; font-family: inherit;
  letter-spacing: 0.01em;
  padding: 0.5rem 1rem 0.5rem 1.1rem;
  text-align: left; width: 100%;
  transition: color 0.12s, background 0.12s, border-left-color 0.12s;
}
.tab-btn:hover { color: var(--txt-2); background: rgba(255,255,255,0.03); }
.tab-btn.active {
  color: var(--txt-1); font-weight: 600;
  border-left-color: var(--accent);
  background: rgba(79,142,247,0.07);
}

/* Desplazar contenido a la derecha del sidebar */
header, #ia-banner, .search-bar, .sort-bar, nav, main, footer {
  margin-left: 210px;
}

header    { top: 0; }
.search-bar { top: 56px; }
.sort-bar   { top: 104px; } /* 56px header + ~48px search-bar */
#cat-nav    { top: 92px; }

/* ── Mobile ──────────────────────────────────────────────────────────────── */
@media (max-width: 768px) {
  .tab-bar {
    position: fixed; left: 0; right: 0; bottom: 0; top: auto;
    width: 100%; height: auto; padding: 0;
    flex-direction: row; overflow-x: auto; overflow-y: hidden;
    border-right: none; border-top: 1px solid var(--border-sub);
    gap: 0; z-index: 200; background: #111119;
  }
  .tab-bar::before { display: none; }
  .tab-bar-section { display: none; }
  .tab-btn {
    padding: 0.7rem 0.875rem; border-left: none;
    border-top: 2px solid transparent; border-radius: 0;
    text-align: center; width: auto; margin: 0;
    white-space: nowrap; flex-shrink: 0; font-size: 0.7rem;
  }
  .tab-btn.active {
    border-left: none; border-top-color: var(--accent);
    background: none; color: var(--txt-1);
  }
  header, #ia-banner, .search-bar, .sort-bar, nav, main, footer { margin-left: 0; }
  main { padding-bottom: 4.5rem; }
  .search-bar { top: 56px; }
  .sort-bar   { top: 104px; }
  #cat-nav    { top: 104px; }
  /* En móvil, el ⌘K hint no tiene sentido */
  .search-bar::after { display: none; }
}

#cat-nav { top: 140px; }

/* ── Tarjeta destacada ───────────────────────────────────────────────────── */
.grid-destacadas {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(460px, 1fr));
  gap: 0.75rem;
  margin-bottom: 2rem;
}

.tarjeta-destacada {
  background: var(--surface);
  border: 1px solid var(--border-sub);
  border-radius: var(--r);
  padding: 2rem;
  display: flex; flex-direction: column; gap: 1rem;
  transition: background 0.15s, border-color 0.15s; position: relative;
}
.tarjeta-destacada:hover { background: var(--surface-2); border-color: var(--border); }

.tarjeta-destacada .categoria-label {
  font-size: 0.58rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.12em; color: var(--accent);
}

/* Fuente visible en destacadas también */
.tarjeta-destacada .fuente-nombre {
  font-size: 0.78rem; color: var(--txt-1); letter-spacing: 0.05em;
}

.tarjeta-destacada .titulo {
  font-size: clamp(1.2rem, 1.5vw, 1.5rem); font-weight: 700;
}

.tarjeta-destacada .resumen {
  font-size: 0.84rem; color: var(--txt-2); line-height: 1.7;
  display: block; overflow: visible; -webkit-line-clamp: unset;
}

.tarjeta-destacada .critica { font-size: 0.79rem; }

.destacadas-header {
  margin-bottom: 2rem; padding-bottom: 0.875rem;
  border-bottom: 2px solid var(--border);
}
.destacadas-header h2 {
  font-size: 0.95rem; font-weight: 700; color: var(--txt-1);
  letter-spacing: -0.01em; margin-bottom: 0.3rem;
}
.destacadas-header p { font-size: 0.73rem; color: var(--txt-3); }

.sin-destacadas { color: var(--txt-3); font-size: 0.875rem; padding: 3rem 0; text-align: center; }

/* ── Buscador ────────────────────────────────────────────────────────────── */

/* Ocultar el input de palabras clave y el separador — demasiado ruido */
.kw-sep      { display: none; }
.keywords-input { display: none; }

.search-bar {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.6rem 2rem;
  background: var(--bg);
  border-bottom: 1px solid var(--border-sub);
  position: sticky; z-index: 90;
}

/* Input principal — ocupa todo el ancho disponible */
.search-input {
  flex: 1;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 7px;
  color: var(--txt-1); font-family: inherit;
  font-size: 0.82rem;
  padding: 0.52rem 0.875rem 0.52rem 2.2rem;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s, background 0.2s;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2344445c' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='11' cy='11' r='8'/%3E%3Cpath d='m21 21-4.35-4.35'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: 0.78rem center;
  background-size: 14px 14px;
}
.search-input::placeholder { color: var(--txt-3); }
.search-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(79,142,247,0.1);
  background-color: var(--surface);
}

/* Contador de resultados */
.search-count {
  font-size: 0.64rem; color: var(--txt-3); white-space: nowrap;
  flex-shrink: 0;
}

/* ⌘K como último flex-item del bar — patrón Raycast/Linear */
.search-bar::after {
  content: '⌘K';
  font-size: 0.5rem; font-weight: 700; letter-spacing: 0.08em;
  color: var(--txt-3);
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 0.18rem 0.44rem;
  flex-shrink: 0;
  align-self: center;
  pointer-events: none;
}

.tarjeta[hidden], .tarjeta-destacada[hidden], .sintesis-card[hidden] { display: none !important; }

/* ── Síntesis ────────────────────────────────────────────────────────────── */
.sintesis-header {
  margin-bottom: 2rem; padding-bottom: 0.875rem;
  border-bottom: 2px solid var(--border);
}
.sintesis-header h2 {
  font-size: 0.95rem; font-weight: 700; color: var(--txt-1);
  letter-spacing: -0.01em; margin-bottom: 0.3rem;
}
.sintesis-header p { font-size: 0.73rem; color: var(--txt-3); }

.grid-sintesis {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
  gap: 0.75rem;
}

.sintesis-card {
  background: var(--surface);
  border: 1px solid var(--border-sub);
  border-radius: var(--r);
  padding: 1.75rem;
  display: flex; flex-direction: column; gap: 1rem;
  transition: background 0.15s, border-color 0.15s;
}
.sintesis-card:hover { background: var(--surface-2); border-color: var(--border); }

.sintesis-meta { display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; }

.sintesis-fuentes-count {
  font-size: 0.56rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.1em;
  background: rgba(79,142,247,0.08); color: var(--accent);
  padding: 0.13rem 0.5rem; border-radius: 3px;
  border: 1px solid rgba(79,142,247,0.2);
}

.sintesis-titulo {
  font-family: var(--font-serif);
  font-size: 1.2rem; font-weight: 700; color: var(--txt-1);
  line-height: 1.3; letter-spacing: -0.02em;
}

.sintesis-texto { font-size: 0.82rem; color: var(--txt-2); line-height: 1.75; white-space: pre-line; }

.sintesis-fuentes {
  border-top: 1px solid var(--border-sub);
  padding-top: 0.875rem; display: flex; flex-direction: column; gap: 0.4rem;
}

.sintesis-fuente-item { display: flex; align-items: baseline; gap: 0.5rem; font-size: 0.78rem; }

.sintesis-fuente-nombre {
  color: var(--txt-3); font-weight: 600; font-size: 0.6rem;
  text-transform: uppercase; letter-spacing: 0.09em;
  white-space: nowrap; min-width: 110px;
}

.sintesis-fuente-link { color: var(--txt-2); text-decoration: none; line-height: 1.4; transition: color 0.12s; }
.sintesis-fuente-link:hover { color: var(--txt-1); }

.sintesis-fuente-alt {
  font-size: 0.56rem; color: #f87171; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.06em; flex-shrink: 0;
}

.sin-sintesis {
  text-align: center; padding: 4rem 2rem; color: var(--txt-3);
  font-size: 0.875rem; line-height: 1.7; max-width: 480px; margin: 0 auto;
}
.sin-sintesis h3 { color: var(--txt-1); font-size: 1rem; margin-bottom: .75rem; }
.sin-sintesis-nota { font-size: .76rem; margin-bottom: 1.5rem; color: var(--txt-3); }
.sin-sintesis button {
  background: var(--accent); color: #fff; border: none; border-radius: 4px;
  padding: .6rem 1.4rem; font-size: .875rem; font-weight: 600;
  cursor: pointer; transition: opacity .15s;
}
.sin-sintesis button:hover { opacity: .85; }
.sin-sintesis button:disabled { opacity: .5; cursor: default; }

/* ── Libertaria ──────────────────────────────────────────────────────────── */
#tab-libertaria .seccion-acento { background: #ef4444; }
#tab-libertaria .seccion-titulo { color: var(--txt-3); }
#tab-libertaria .analisis-general {
  background: rgba(239,68,68,0.05);
  border-color: rgba(239,68,68,0.18); border-left-color: #ef4444;
  color: var(--txt-2);
}
#tab-libertaria .analisis-general-titulo { color: #ef4444; }

.libertaria-header {
  background: rgba(239,68,68,0.05);
  border: 1px solid rgba(239,68,68,0.14); border-left: 2px solid #ef4444;
  border-radius: var(--r); padding: 0.875rem 1.1rem;
  margin-bottom: 2rem; color: var(--txt-2);
  font-size: 0.82rem; line-height: 1.65;
}
.libertaria-header strong {
  color: #ef4444; display: block; margin-bottom: 0.3rem;
  font-size: 0.6rem; text-transform: uppercase; letter-spacing: 0.1em;
}

#tab-libertaria .tab-btn.active { border-left-color: #ef4444; }

/* ── Estadísticas ────────────────────────────────────────────────────────── */
.stats-header { margin-bottom: 2rem; padding-bottom: .75rem; border-bottom: 1px solid var(--border-sub); }
.stats-header h2 { font-size: 1rem; font-weight: 700; color: var(--txt-1); letter-spacing: -.02em; margin-bottom: .3rem; }
.stats-header p  { font-size: .73rem; color: var(--txt-3); }

.stats-fallidas {
  background: rgba(245,158,11,0.06); border: 1px solid rgba(245,158,11,0.18);
  border-radius: var(--r); padding: .7rem 1rem; margin-bottom: 1.5rem;
  font-size: .77rem; color: var(--accent-gold);
}
.stats-fallidas ul { margin: .4rem 0; padding-left: 1.2rem; color: var(--txt-2); }
.stats-fallidas span { font-size: .7rem; color: var(--txt-3); }

.stats-kpi-row {
  display: flex; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 2rem;
}
.stat-kpi {
  background: var(--surface); border: 1px solid var(--border-sub);
  border-radius: var(--r); padding: 1.25rem 1.5rem; min-width: 150px; flex: 1;
}
.stat-kpi-valor {
  font-size: 2.2rem; font-weight: 800; color: var(--accent);
  letter-spacing: -.04em; line-height: 1;
}
.stat-kpi-label {
  font-size: .6rem; color: var(--txt-3); margin-top: .4rem;
  text-transform: uppercase; letter-spacing: .08em;
}

.stats-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 0.75rem;
}
.stat-card {
  background: var(--surface); border: 1px solid var(--border-sub);
  border-radius: var(--r); padding: 1.25rem 1.5rem;
}
.stat-card-title {
  font-size: .56rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: .14em; color: var(--txt-3); margin-bottom: 1rem;
}
.stat-bar-row { display: flex; align-items: center; gap: .75rem; margin-bottom: .55rem; }
.stat-bar-label { font-size: .7rem; color: var(--txt-2); min-width: 120px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.stat-bar-bg { flex: 1; background: var(--surface-2); border-radius: 2px; height: 3px; min-width: 40px; }
.stat-bar-fill { height: 3px; border-radius: 2px; min-width: 2px; transition: width .6s cubic-bezier(.4,0,.2,1); }
.stat-bar-count { font-size: .67rem; color: var(--txt-3); min-width: 22px; text-align: right; }

/* ── Filtros de sesgo — barra segmentada ─────────────────────────────────── */
.leyenda-items {
  display: flex; gap: 0;
  background: var(--surface);
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid var(--border-sub);
}
.leyenda-items .badge {
  cursor: pointer; user-select: none;
  border-radius: 0;
  font-size: 0.5rem; padding: 0.22rem 0.6rem;
  opacity: 0.65;
  transition: opacity .15s, filter .15s;
  border-right: 1px solid rgba(0,0,0,0.15);
  flex-shrink: 0;
}
.leyenda-items .badge:last-child { border-right: none; }
.leyenda-items .badge:hover { opacity: 0.9; filter: brightness(1.15); }
.leyenda-items .badge.filtro-activo { opacity: 1; filter: brightness(1.2); box-shadow: inset 0 -2px 0 rgba(255,255,255,0.35); }
.leyenda-tip { font-size: .6rem; color: var(--txt-3); font-style: italic; }
.filtro-aviso { font-size: .66rem; color: var(--accent); font-weight: 600; }
.filtro-clear-btn {
  background: none; border: 1px solid var(--border);
  color: var(--txt-3); border-radius: 3px; padding: .12rem .5rem;
  font-size: .6rem; cursor: pointer; font-family: inherit; transition: background .12s;
}
.filtro-clear-btn:hover { background: var(--surface-2); color: var(--txt-1); }

/* ── Drawer lateral ──────────────────────────────────────────────────────── */
.drawer-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.65);
  z-index: 500; opacity: 0; pointer-events: none;
  transition: opacity 0.25s; backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}
.drawer-overlay.open { opacity: 1; pointer-events: all; }

.drawer {
  position: fixed; top: 0; right: 0; height: 100%;
  width: min(560px, 100vw);
  background: #17171f;
  border-left: 1px solid var(--border-sub);
  z-index: 501; display: flex; flex-direction: column;
  transform: translateX(100%);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.drawer.open { transform: translateX(0); }

.drawer-header {
  padding: 1.1rem 1.5rem; border-bottom: 1px solid var(--border-sub);
  display: flex; justify-content: space-between; align-items: flex-start;
  gap: 1rem; flex-shrink: 0;
}
.drawer-header-meta { display: flex; flex-direction: column; gap: 0.3rem; min-width: 0; }
.drawer-categoria { font-size: 0.56rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.14em; color: var(--accent); }
.drawer-fuente-row { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
.drawer-reading { font-size: 0.6rem; color: var(--txt-3); display: flex; align-items: center; gap: 0.25rem; }

.drawer-close {
  background: none; border: 1px solid var(--border-sub);
  color: var(--txt-3); border-radius: 4px; width: 28px; height: 28px;
  cursor: pointer; font-size: 0.82rem; display: flex;
  align-items: center; justify-content: center; flex-shrink: 0;
  transition: background 0.12s, color 0.12s;
}
.drawer-close:hover { background: var(--surface-2); color: var(--txt-1); }

.drawer-body {
  padding: 1.5rem; overflow-y: auto; flex: 1;
  display: flex; flex-direction: column; gap: 1.25rem;
}
.drawer-badges { display: flex; align-items: center; gap: 0.35rem; flex-wrap: wrap; }
.drawer-titulo {
  font-family: var(--font-serif);
  font-size: 1.45rem; font-weight: 700; line-height: 1.28;
  letter-spacing: -0.02em; color: var(--txt-1);
}
.drawer-resumen { font-size: 0.875rem; color: var(--txt-2); line-height: 1.85; }
.drawer-critica {
  background: none;
  border-top: 1px solid var(--border-sub);
  padding: 0.875rem 0 0;
  font-size: 0.8rem; color: var(--txt-3); line-height: 1.65;
}
.drawer-critica::before {
  content: 'ANÁLISIS IA';
  display: block; font-size: 0.5rem; font-weight: 800;
  letter-spacing: 0.16em; color: var(--accent); margin-bottom: 0.4rem;
}

.drawer-footer {
  padding: 1rem 1.5rem; border-top: 1px solid var(--border-sub);
  display: flex; gap: 0.625rem; flex-shrink: 0; flex-wrap: wrap;
}
.drawer-btn {
  flex: 1; padding: 0.55rem 1rem; border-radius: 4px;
  font-size: 0.76rem; font-weight: 600; font-family: inherit;
  cursor: pointer; border: none;
  transition: background 0.15s, opacity 0.15s;
  text-decoration: none; display: flex; align-items: center; justify-content: center; gap: 0.4rem;
}
.drawer-btn-primary { background: var(--accent); color: #fff; }
.drawer-btn-primary:hover { background: #2563eb; }
.drawer-btn-secondary { background: var(--surface-2); color: var(--txt-1); border: 1px solid var(--border-sub); }
.drawer-btn-secondary:hover { background: var(--border); }
.drawer-btn-translate { background: rgba(79,142,247,0.08); color: var(--accent); border: 1px solid rgba(79,142,247,0.2); }
.drawer-btn-translate:hover { background: rgba(79,142,247,0.14); }

.tarjeta, .tarjeta-destacada { cursor: pointer; }
.tarjeta:active, .tarjeta-destacada:active { transform: scale(0.999); }
.tarjeta .titulo a, .tarjeta-destacada .titulo a { cursor: pointer; }

/* ── Sentimiento ─────────────────────────────────────────────────────────── */
.badge-sent { font-size: 0.5rem; font-weight: 700; letter-spacing: 0.05em; padding: 0.12rem 0.4rem; border-radius: 3px; }
.badge-sent-alarmista { background: rgba(239,68,68,0.12); color: #f87171; }
.badge-sent-neutral   { background: rgba(255,255,255,0.05); color: var(--txt-3); }
.badge-sent-optimista { background: rgba(45,212,160,0.1); color: #4ade80; }

/* ── Badge verificado ────────────────────────────────────────────────────── */
.badge-verified {
  font-size: 0.5rem; font-weight: 700; letter-spacing: 0.07em;
  padding: 0.12rem 0.4rem; border-radius: 3px;
  background: rgba(79,142,247,0.1); color: var(--accent);
  border: 1px solid rgba(79,142,247,0.22);
}

/* ── Bookmark ────────────────────────────────────────────────────────────── */
.bookmark-btn {
  background: none; border: none; cursor: pointer;
  font-size: 0.82rem; color: var(--txt-3); padding: 0.1rem 0.2rem;
  border-radius: 3px; line-height: 1; transition: color 0.15s; flex-shrink: 0;
}
.bookmark-btn:hover { color: var(--accent-gold); }
.bookmark-btn.guardado { color: var(--accent-gold); }

/* ── Palabras clave ──────────────────────────────────────────────────────── */
.tarjeta.kw-match, .tarjeta-destacada.kw-match { border-left: 2px solid var(--accent-gold); }
.keywords-input {
  width: 180px; background: var(--surface);
  border: 1px solid var(--border-sub); border-radius: 4px;
  color: var(--txt-1); font-family: inherit; font-size: 0.76rem;
  padding: 0.35rem 0.75rem; outline: none; transition: border-color 0.15s;
}
.keywords-input::placeholder { color: var(--txt-3); }
.keywords-input:focus { border-color: var(--accent-gold); }
.kw-sep { color: var(--border); font-size: 1.1rem; user-select: none; }

/* ── Asombro ─────────────────────────────────────────────────────────────── */
#tab-asombro { padding: 1rem; }
.asombro-header { text-align: center; padding: 2rem 0 1.5rem; }
.asombro-header h2 {
  font-family: var(--font-serif);
  font-size: 1.6rem; font-weight: 700; color: var(--txt-1);
  margin-bottom: .5rem; letter-spacing: -.03em;
}
.asombro-header p { font-size: .82rem; color: var(--txt-3); max-width: 520px; margin: 0 auto; line-height: 1.7; }
.asombro-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(380px,1fr));
  gap: 0.75rem; max-width: 1400px; margin: 0 auto;
}
.asombro-card {
  background: var(--surface); border: 1px solid var(--border-sub);
  border-radius: var(--r); padding: 1.5rem; cursor: pointer;
  transition: background .15s, border-color .15s;
}
.asombro-card:hover { background: var(--surface-2); border-color: var(--border); }
.asombro-score { font-size: 0.88rem; color: #a78bfa; margin-bottom: .4rem; letter-spacing: .12em; }
.asombro-cat { display: inline-block; font-size: .56rem; text-transform: uppercase; letter-spacing: .1em; color: #a78bfa; background: rgba(167,139,250,0.1); border: 1px solid rgba(167,139,250,0.2); border-radius: 3px; padding: .1rem .4rem; margin-bottom: .6rem; }
.asombro-titulo { font-family: var(--font-serif); font-size: .95rem; font-weight: 700; color: var(--txt-1); margin-bottom: .35rem; line-height: 1.32; }
.asombro-titulo a { color: inherit; text-decoration: none; }
.asombro-titulo a:hover { color: #a78bfa; }
.asombro-fuente { font-size: .66rem; color: var(--txt-3); margin-bottom: .6rem; }
.asombro-razon { font-size: .77rem; color: #a78bfa; font-style: italic; margin-bottom: .6rem; line-height: 1.5; }
.asombro-resumen { font-size: .77rem; color: var(--txt-2); line-height: 1.6; }
.asombro-empty { text-align: center; padding: 5rem 1rem; color: var(--txt-3); }
.asombro-empty-icon { font-size: 3rem; margin-bottom: 1rem; }
.tab-btn[data-tab="asombro"].active { border-left-color: #7c3aed !important; }

/* ── Barra de ordenación ─────────────────────────────────────────────────── */
.sort-bar {
  position: sticky; z-index: 89; background: var(--bg);
  padding: .28rem 1rem; display: flex; align-items: center;
  gap: .28rem; flex-wrap: wrap; border-bottom: 1px solid var(--border-sub);
}
.sort-label { font-size: .66rem; color: var(--txt-3); margin-right: .15rem; white-space: nowrap; }
.sort-btn {
  font-size: .64rem; padding: .14rem .48rem; border-radius: 3px;
  border: 1px solid var(--border); background: transparent;
  color: var(--txt-3); cursor: pointer; transition: background .15s, color .15s; white-space: nowrap;
}
.sort-btn:hover { background: var(--surface-2); color: var(--txt-1); }
.sort-btn.active { background: var(--accent); color: #fff; border-color: var(--accent); font-weight: 600; }

/* ── Para Leer ───────────────────────────────────────────────────────────── */
.para-leer-header { margin-bottom: 1.5rem; padding-bottom: .75rem; border-bottom: 1px solid var(--border-sub); }
.para-leer-header h2 { font-size: 1rem; font-weight: 700; color: var(--txt-1); letter-spacing: -.02em; margin-bottom: .3rem; }
.para-leer-header p  { font-size: .73rem; color: var(--txt-3); }
.para-leer-empty { text-align: center; padding: 4rem 0; color: var(--txt-3); font-size: .875rem; line-height: 1.7; }
.tab-count { font-size: .52rem; background: var(--accent); color: #fff; border-radius: 3px; padding: .1rem .38rem; margin-left: .3rem; vertical-align: middle; }

/* ── Ángulos ─────────────────────────────────────────────────────────────── */
.angulos-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: .75rem; border-top: 1px solid var(--border-sub); padding-top: .875rem; }
.angulo-col { display: flex; flex-direction: column; gap: .4rem; }
.angulo-label { font-size: .54rem; font-weight: 700; text-transform: uppercase; letter-spacing: .12em; color: var(--txt-3); margin-bottom: .1rem; }
.angulo-item { font-size: .73rem; }
.angulo-item a { color: var(--txt-2); text-decoration: none; line-height: 1.4; }
.angulo-item a:hover { color: var(--txt-1); }

/* ── Banner IA ───────────────────────────────────────────────────────────── */
#ia-banner {
  display: none; align-items: center; gap: .75rem;
  background: rgba(79,142,247,0.05); border: 1px solid rgba(79,142,247,0.14);
  border-radius: 0; padding: .55rem 2rem;
  font-size: .77rem; color: var(--txt-2);
}
#ia-banner .ia-msg { flex: 1; }
#ia-banner .ia-regen {
  background: var(--accent); color: #fff; border: none; border-radius: 4px;
  padding: .3rem .875rem; font-size: .74rem; font-weight: 600;
  cursor: pointer; text-decoration: none; white-space: nowrap; transition: background .15s;
}
#ia-banner .ia-regen:hover { background: #2563eb; }
#ia-banner .ia-regen:disabled { opacity: .5; cursor: default; }
#ia-banner .ia-close { background: none; border: none; color: var(--txt-3); cursor: pointer; font-size: 1rem; line-height: 1; padding: 0 .15rem; }

/* ── Actualidad Absoluta ─────────────────────────────────────────────────── */
.actualidad-header { padding: 2rem 0 1.25rem; border-bottom: 1px solid var(--border-sub); margin-bottom: 1.75rem; }
.actualidad-header h2 {
  font-family: var(--font-serif);
  font-size: 1.6rem; font-weight: 700; color: var(--txt-1);
  margin: 0 0 .35rem; letter-spacing: -0.03em;
}
.actualidad-header > p { color: var(--txt-3); font-size: .82rem; margin: 0 0 1rem; }
.historial-filtros { display: flex; align-items: center; gap: .4rem; flex-wrap: wrap; }
.historial-filtro-label { font-size: .7rem; color: var(--txt-3); font-weight: 600; }
.historial-filtro-sep { color: var(--border); font-size: .85rem; margin: 0 .15rem; }
.historial-filter-btn {
  background: var(--surface); border: 1px solid var(--border-sub);
  color: var(--txt-3); border-radius: 3px; padding: .18rem .58rem;
  font-size: .68rem; font-weight: 600; cursor: pointer; transition: all .15s; white-space: nowrap;
}
.historial-filter-btn.active,
.historial-filter-btn:hover { background: var(--accent); border-color: var(--accent); color: #fff; }

.proceso-card,
.proceso-card-hero {
  background: var(--surface); border: 1px solid var(--border-sub);
  border-left-width: 3px; border-radius: var(--r); overflow: hidden;
  display: flex; flex-direction: column; transition: background .15s;
}
.proceso-card:hover, .proceso-card-hero:hover { background: var(--surface-2); }

.proceso-card[data-estado="escalada"],
.proceso-card-hero[data-estado="escalada"]   { border-left-color: #ef4444; }
.proceso-card[data-estado="estable"],
.proceso-card-hero[data-estado="estable"]    { border-left-color: var(--accent); }
.proceso-card[data-estado="resolucion"],
.proceso-card-hero[data-estado="resolucion"] { border-left-color: var(--accent-green); }
.proceso-card[data-estado="silencio"],
.proceso-card-hero[data-estado="silencio"]   { border-left-color: var(--txt-3); }

.proceso-card-hero { margin-bottom: 1.5rem; }
.proceso-card-hero .proceso-nombre  { font-size: 1.3rem; }
.proceso-card-hero .proceso-resumen { font-size: .9rem; }
.proceso-card-hero .proceso-sparkline { height: 70px; }
.proceso-card-hero .proceso-watermark { font-size: 9rem; opacity: .025; }

.proceso-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; padding-bottom: 3rem; }

.proceso-strip { display: flex; align-items: center; gap: .35rem; padding: .36rem .9rem; font-size: .61rem; font-weight: 700; letter-spacing: .07em; flex-shrink: 0; }
.proceso-strip-escalada   { background: rgba(239,68,68,0.08);  color: #f87171; }
.proceso-strip-estable    { background: rgba(79,142,247,0.07); color: var(--accent); }
.proceso-strip-resolucion { background: rgba(45,212,160,0.07); color: var(--accent-green); }
.proceso-strip-silencio   { background: rgba(255,255,255,0.04); color: var(--txt-3); }
.proceso-strip-icono   { font-size: .85rem; }
.proceso-strip-dot     { opacity: .2; }
.proceso-strip-horizonte { font-size: .58rem; letter-spacing: .05em; opacity: .75; }
.proceso-strip-arts    { margin-left: auto; opacity: .5; font-weight: 400; letter-spacing: 0; }

.proceso-body { position: relative; overflow: hidden; padding: .9rem 1rem .75rem; display: flex; flex-direction: column; gap: .55rem; flex: 1; }
.proceso-watermark { position: absolute; right: -.1rem; top: -.4rem; font-size: 6rem; font-weight: 900; line-height: 1; opacity: .025; color: var(--txt-1); pointer-events: none; user-select: none; }
.proceso-nombre { font-family: var(--font-serif); font-size: 1.05rem; font-weight: 700; color: var(--txt-1); line-height: 1.3; position: relative; letter-spacing: -0.02em; }
.proceso-descripcion { font-size: .77rem; color: var(--txt-2); line-height: 1.45; }
.proceso-imp-row { display: flex; align-items: center; gap: .5rem; }
.proceso-imp-track { flex: 1; height: 3px; background: var(--surface-2); border-radius: 2px; overflow: hidden; }
.proceso-imp-fill { height: 100%; border-radius: 2px; }
.proceso-imp-fill-escalada   { background: #ef4444; }
.proceso-imp-fill-estable    { background: var(--accent); }
.proceso-imp-fill-resolucion { background: var(--accent-green); }
.proceso-imp-fill-silencio   { background: var(--txt-3); }
.proceso-imp-num { font-size: .66rem; font-weight: 700; color: var(--txt-3); white-space: nowrap; }
.proceso-resumen { font-size: .82rem; color: var(--txt-1); line-height: 1.55; margin: 0; }
.proceso-articulos { list-style: none; margin: 0; padding: .5rem 0 0; border-top: 1px solid var(--border-sub); display: flex; flex-direction: column; gap: .25rem; }
.proceso-articulos li  { font-size: .7rem; color: var(--txt-3); line-height: 1.3; }
.proceso-articulos a   { color: var(--accent); text-decoration: none; }
.proceso-articulos a:hover { text-decoration: underline; }
.proceso-art-fuente    { font-size: .63rem; color: var(--txt-3); }
.proceso-footer { border-top: 1px solid var(--border-sub); padding: .6rem 1rem .75rem; display: flex; flex-direction: column; gap: .3rem; background: rgba(255,255,255,0.015); }
.proceso-trend-wrap { font-size: .73rem; font-weight: 600; min-height: 1.1em; }
.proceso-spark-label-row { display: flex; align-items: center; justify-content: space-between; }
.proceso-spark-label { font-size: .56rem; color: var(--txt-3); font-weight: 600; text-transform: uppercase; letter-spacing: .09em; }
.proceso-sparkline { display: flex; align-items: flex-end; gap: 2px; height: 48px; }
.spark-bar { flex: 1; border-radius: 2px 2px 0 0; min-height: 2px; cursor: default; transition: opacity .12s; }
.spark-bar:hover { opacity: .7 !important; }
.actualidad-empty { padding: 3rem 0; text-align: center; color: var(--txt-3); font-size: .88rem; }

/* ── Conexiones ──────────────────────────────────────────────────────────── */
.conexiones-panel {
  background: var(--surface); border: 1px solid var(--border-sub);
  border-left: 3px solid var(--accent-gold); border-radius: var(--r);
  padding: 1rem 1.1rem; margin-top: 1.5rem;
  display: flex; flex-direction: column; gap: .6rem;
}
.conexiones-titulo { font-size: .62rem; font-weight: 700; color: var(--accent-gold); text-transform: uppercase; letter-spacing: .1em; margin-bottom: .2rem; }
.conexion-item { display: flex; flex-direction: column; gap: .15rem; padding: .4rem 0; border-bottom: 1px solid var(--border-sub); }
.conexion-item:last-child { border-bottom: none; }
.conexion-nombres { font-size: .72rem; font-weight: 700; color: var(--txt-2); }
.conexion-rel { font-size: .78rem; color: var(--txt-1); line-height: 1.45; }

/* ── Briefing ────────────────────────────────────────────────────────────── */
.briefing-btn { background: var(--accent) !important; border-color: var(--accent) !important; color: #fff !important; }
.briefing-btn:hover { background: #2563eb !important; border-color: #2563eb !important; }
#briefing-panel {
  background: var(--surface); border: 1px solid var(--border-sub);
  border-left: 3px solid var(--accent); border-radius: var(--r);
  padding: 1.25rem 1.4rem; margin-bottom: 1.75rem; position: relative;
}
.briefing-header { display: flex; align-items: center; justify-content: space-between; font-size: .62rem; font-weight: 700; text-transform: uppercase; letter-spacing: .12em; color: var(--txt-3); margin-bottom: .9rem; padding-bottom: .6rem; border-bottom: 1px solid var(--border-sub); }
.briefing-close { background: none; border: none; cursor: pointer; color: var(--txt-3); font-size: 1rem; line-height: 1; }
.briefing-texto { font-size: .85rem; line-height: 1.7; color: var(--txt-1); }
.briefing-texto strong { display: block; margin-top: .8rem; margin-bottom: .25rem; font-size: .62rem; text-transform: uppercase; letter-spacing: .12em; color: var(--accent); }
.briefing-texto strong:first-child { margin-top: 0; }

/* ── Señal / Ruido ───────────────────────────────────────────────────────── */
.badge-senal { display: inline-flex; align-items: center; gap: .2rem; font-size: .56rem; font-weight: 700; padding: .12rem .38rem; border-radius: 3px; background: rgba(45,212,160,0.1); color: var(--accent-green); border: 1px solid rgba(45,212,160,0.2); white-space: nowrap; }
.badge-ruido { display: inline-flex; align-items: center; gap: .2rem; font-size: .56rem; font-weight: 600; padding: .12rem .38rem; border-radius: 3px; background: rgba(255,255,255,0.04); color: var(--txt-3); border: 1px solid var(--border-sub); white-space: nowrap; opacity: .8; }
.tarjeta:has(.badge-ruido) { opacity: .72; }

/* ── Alertas Vigilar ─────────────────────────────────────────────────────── */
#watch-panel { display: flex; flex-direction: column; gap: .6rem; margin-bottom: 1rem; }
.watch-alerta { display: flex; align-items: flex-start; gap: .8rem; background: rgba(234,88,12,0.06); border: 1px solid rgba(234,88,12,0.18); border-left: 4px solid #ea580c; border-radius: var(--r); padding: .75rem 1rem; }
.watch-icono { font-size: 1rem; flex-shrink: 0; margin-top: .05rem; }
.watch-alerta strong { font-size: .77rem; color: #fb923c; display: block; margin-bottom: .2rem; }
.watch-alerta p { font-size: .74rem; color: var(--txt-2); margin: 0; line-height: 1.4; }
.watch-confianza { margin-left: auto; font-size: .66rem; font-weight: 700; color: #ea580c; white-space: nowrap; flex-shrink: 0; }

/* ═══════════════════════════════════════════════════════════════════════════
   EFECTOS VISUALES
   ═══════════════════════════════════════════════════════════════════════════ */

/* ── Splash ──────────────────────────────────────────────────────────────── */
#splash {
  position: fixed; inset: 0; z-index: 9999;
  background: #0f0f16;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 2rem;
  cursor: pointer; transition: opacity 0.6s ease;
}
#splash.saliendo { opacity: 0; pointer-events: none; }
#splash.ido { display: none; }

.splash-eyebrow { font-size: 0.56rem; letter-spacing: 0.38em; text-transform: uppercase; color: rgba(255,255,255,0.2); font-weight: 700; animation: splashFadeUp 0.6s ease both; }
.splash-logo {
  font-family: 'Playfair Display', Georgia, serif;
  font-size: clamp(2.8rem, 7vw, 5rem); font-weight: 800;
  color: #fff; letter-spacing: -0.04em; line-height: 1;
  text-align: center; animation: splashFadeUp 0.6s ease 0.1s both;
}
.splash-divider {
  width: 28px; height: 1px; background: var(--accent);
  animation: splashFadeUp 0.6s ease 0.2s both;
}
.splash-headlines { display: flex; flex-direction: column; gap: 0.75rem; max-width: 520px; width: 88%; }
.splash-hl {
  font-size: clamp(0.76rem, 1.2vw, 0.86rem); color: rgba(255,255,255,0.38);
  line-height: 1.5; padding-left: 0.85rem;
  border-left: 1px solid rgba(79,142,247,0.45);
  animation: splashHlIn 0.5s cubic-bezier(0.16,1,0.3,1) both;
}
.splash-hl:nth-child(1) { animation-delay: 0.3s; }
.splash-hl:nth-child(2) { animation-delay: 0.42s; }
.splash-hl:nth-child(3) { animation-delay: 0.54s; }
.splash-hint { font-size: 0.52rem; color: rgba(255,255,255,0.12); letter-spacing: 0.24em; text-transform: uppercase; animation: splashFadeUp 0.6s ease 0.7s both; }
@keyframes splashFadeUp {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes splashHlIn {
  from { opacity: 0; transform: translateX(-10px); }
  to   { opacity: 1; transform: translateX(0); }
}

/* ── Staggered ───────────────────────────────────────────────────────────── */
@keyframes cardIn {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
.card-animate { animation: cardIn 0.38s cubic-bezier(0.16, 1, 0.3, 1) both; animation-delay: var(--card-delay, 0ms); }

@keyframes tabFadeIn {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}
.tab-anim { animation: tabFadeIn 0.18s ease both; }

/* ── Grain en sidebar ────────────────────────────────────────────────────── */
.tab-bar { overflow: hidden; }
.tab-bar::after {
  content: ''; position: absolute; inset: 0; pointer-events: none; z-index: 1;
  opacity: 0.04;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.82' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)'/%3E%3C/svg%3E");
  background-size: 220px 220px;
}
.tab-bar > * { position: relative; z-index: 2; }

/* ── Toggle modo claro ───────────────────────────────────────────────────── */
.dark-toggle {
  position: relative; margin: 1rem 0.75rem 0;
  background: none; border: 1px solid rgba(255,255,255,0.08);
  color: rgba(255,255,255,0.22); border-radius: 4px;
  padding: 0.3rem 0.75rem; font-size: 0.58rem; cursor: pointer;
  font-family: inherit; letter-spacing: 0.07em; text-align: center;
  transition: all 0.2s; white-space: nowrap; z-index: 3;
}
.dark-toggle:hover { border-color: rgba(255,255,255,0.25); color: rgba(255,255,255,0.55); }
@media (max-width: 768px) { .dark-toggle { display: none; } }

/* ── Modo claro (toggle) ─────────────────────────────────────────────────── */
body.dark {
  --bg:         #f5f4ef;
  --surface:    #ffffff;
  --surface-2:  #ededea;
  --border:     rgba(0,0,0,0.1);
  --border-sub: rgba(0,0,0,0.06);
  --txt-1:      #0f0f14;
  --txt-2:      #555568;
  --txt-3:      #9999aa;
  --accent:     #2563eb;
}
body.dark header { background: rgba(245,244,239,0.96); border-bottom-color: rgba(0,0,0,0.07); }
body.dark nav { background: rgba(245,244,239,0.95); }
body.dark .search-bar, body.dark .sort-bar { background: var(--bg); }
body.dark .tab-bar { background: #1a1a24; border-right-color: rgba(255,255,255,0.06); }
body.dark .analisis-general { background: rgba(37,99,235,0.05); border-color: rgba(37,99,235,0.15); color: var(--txt-2); }
body.dark .critica { background: none; color: var(--txt-2); }
body.dark .drawer { background: #f8f7f3; }
body.dark .drawer-critica { background: rgba(37,99,235,0.04); color: var(--txt-2); }
body.dark #ia-banner { background: rgba(37,99,235,0.05); color: var(--txt-2); border-color: rgba(37,99,235,0.14); }
body.dark .briefing-btn { background: var(--accent) !important; }
body.dark .grid, body.dark .grid-destacadas, body.dark .grid-sintesis,
body.dark .asombro-grid, body.dark .stats-kpi-row, body.dark .stats-grid { background: rgba(0,0,0,0.06); }
body.dark .badge-sent-alarmista { background: #fef2f2; color: #b91c1c; }
body.dark .badge-sent-neutral   { background: #f3f4f6; color: #6b7280; }
body.dark .badge-sent-optimista { background: #f0fdf4; color: #16a34a; }

/* ── Focus mode ──────────────────────────────────────────────────────────── */
body.drawer-open .tarjeta,
body.drawer-open .tarjeta-destacada,
body.drawer-open .asombro-card {
  opacity: 0.1; pointer-events: none;
  transition: opacity 0.35s; transform: none !important;
}

/* ── Tensiómetro ─────────────────────────────────────────────────────────── */
.tension-wrap { display: flex; align-items: center; gap: 0.4rem; margin-top: 0.2rem; }
.tension-dot { width: 5px; height: 5px; border-radius: 50%; flex-shrink: 0; animation: tensionPulse 2.5s ease-in-out infinite; }
@keyframes tensionPulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50%       { transform: scale(1.35); opacity: 0.6; }
}
.tension-label { font-size: 0.55rem; letter-spacing: 0.09em; text-transform: uppercase; font-weight: 700; }
"""
