"""
styles.py — CSS embebido del digest de noticias.
Importado por renderer.py como constante _CSS.
"""

_CSS = """
/* ── Variables — Natural Studio (bio/sage) ───────────────────────────── */
:root {
  --bg:          #f4f2eb;   /* lino cálido, como papel natural */
  --surface:     #ffffff;
  --surface-2:   #eeeee6;   /* hover lino */
  --border:      rgba(60,90,60,0.14);
  --border-sub:  rgba(60,90,60,0.08);
  --txt-1:       #1c2419;   /* negro con alma verde */
  --txt-2:       #3a4a37;
  --txt-3:       #7a8c78;   /* sage gris */
  --accent:      #3d7a52;   /* sage verde natural */
  --accent-blue: #4a8a7a;   /* teal suave */
  --accent-green:#5aaa3a;   /* verde vivo */
  --accent-gold: #b8834a;   /* ámbar tierra */
  --r:           14px;
  --font-serif:  system-ui, -apple-system, 'Helvetica Neue', sans-serif;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: system-ui, -apple-system, 'Helvetica Neue', sans-serif;
  background-color: var(--bg);
  color: var(--txt-1);
  line-height: 1.65;
  font-size: 15px;
  -webkit-font-smoothing: antialiased;
}

/* ── Cabecera ────────────────────────────────────────────────────────── */
header {
  background: rgba(255,255,255,0.88);
  border-bottom: 1px solid var(--border-sub);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow: none;
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
  background: linear-gradient(135deg, #3d7a52 0%, #5aaa3a 100%);
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
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
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
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
main { max-width: 1340px; margin: 0 auto; padding: 3rem 2.5rem; }

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

.seccion-acento {
  width: 4px;
  height: 1.2rem;
  background: linear-gradient(180deg, #3d7a52, #5aaa3a);
  border-radius: 9999px;
  flex-shrink: 0;
}

.seccion-titulo {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--txt-1);
  letter-spacing: -0.02em;
}

/* ── Bloque de análisis crítico general ──────────────────────────────── */
.analisis-general {
  background: #edf5f0;
  border: 1px solid rgba(61,122,82,0.2);
  border-left: 3px solid var(--accent);
  border-radius: var(--r);
  padding: 0.9rem 1.2rem;
  margin-bottom: 1.5rem;
  color: #1c3828;
  font-size: 0.855rem;
  line-height: 1.7;
}
.analisis-general-titulo {
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--accent);
  margin-bottom: 0.45rem;
}

/* ── Grid de tarjetas ────────────────────────────────────────────────── */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 1rem;
}

/* ── Tarjeta de artículo ─────────────────────────────────────────────── */
.tarjeta {
  background: var(--surface);
  border: 1px solid var(--border-sub);
  border-radius: var(--r);
  padding: 1.25rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
  transition: box-shadow 0.2s, transform 0.15s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.tarjeta:hover {
  border-color: rgba(0,0,0,0.12);
  box-shadow: 0 8px 32px rgba(0,0,0,0.10);
  transform: translateY(-2px);
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
  color: var(--accent);
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
  font-size: 1.05rem;
  font-weight: 700;
  line-height: 1.35;
  letter-spacing: -0.02em;
}
.titulo a { color: var(--txt-1); text-decoration: none; transition: color 0.12s; }
.titulo a:hover { color: var(--accent); }

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

/* ── Crítica de IA ───────────────────────────────────────────────────── */
.critica {
  background: #edf5f0;
  border: 1px solid rgba(61,122,82,0.15);
  border-left: 2px solid var(--accent);
  border-radius: calc(var(--r) - 2px);
  padding: 0.55rem 0.875rem;
  font-size: 0.77rem;
  color: #1c3828;
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

/* ── Sidebar de navegación — natural dark forest ─────────────────────── */
.tab-bar {
  position: fixed;
  left: 0; top: 0; bottom: 0;
  width: 210px;
  background: linear-gradient(160deg, #1e3a2a 0%, #112416 60%, #0a160d 100%);
  border-right: none;
  border-bottom: none;
  padding: 4rem 0 2rem;
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  z-index: 100;
  overflow-y: auto;
}

.tab-bar::before {
  content: '⬛  Digest';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4rem;
  display: flex;
  align-items: center;
  padding: 0 1.25rem;
  font-weight: 700;
  font-size: 0.9rem;
  color: #ffffff;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  letter-spacing: -0.02em;
}

.tab-bar-section {
  font-size: 0.6rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: rgba(255,255,255,0.35);
  padding: 1rem 1.25rem 0.4rem;
  user-select: none;
}

.tab-btn {
  background: none;
  border: none;
  border-left: 3px solid transparent;
  color: rgba(255,255,255,0.55);
  cursor: pointer;
  font-size: 0.82rem;
  font-weight: 500;
  font-family: inherit;
  letter-spacing: 0.005em;
  padding: 0.6rem 1rem 0.6rem 1.1rem;
  margin: 0 0.5rem 0 0;
  border-radius: 0 0.5rem 0.5rem 0;
  text-align: left;
  width: calc(100% - 0.5rem);
  transition: color 0.15s, background 0.15s, border-left-color 0.15s;
}
.tab-btn:hover {
  color: rgba(255,255,255,0.9);
  background: rgba(255,255,255,0.07);
}
.tab-btn.active {
  color: #ffffff;
  font-weight: 600;
  border-left-color: #5aaa3a;
  background: rgba(90,170,58,0.18);
}

/* Desplazar todo el contenido a la derecha del sidebar */
header,
#ia-banner,
.search-bar,
.sort-bar,
nav,
main,
footer {
  margin-left: 210px;
}

/* Ajustar posiciones sticky */
header    { top: 0; }
.search-bar { top: 64px; }
.sort-bar   { top: 64px; }
#cat-nav    { top: 105px; }

/* Mobile — sidebar se convierte en tab bar horizontal inferior */
@media (max-width: 768px) {
  .tab-bar {
    position: fixed;
    left: 0; right: 0; bottom: 0; top: auto;
    width: 100%;
    height: auto;
    padding: 0;
    flex-direction: row;
    overflow-x: auto;
    overflow-y: hidden;
    border-right: none;
    border-top: 1px solid rgba(255,255,255,0.1);
    gap: 0;
    z-index: 200;
  }
  .tab-bar::before { display: none; }
  .tab-bar-section { display: none; }
  .tab-btn {
    padding: 0.6rem 0.75rem;
    border-left: none;
    border-top: 2px solid transparent;
    border-radius: 0;
    text-align: center;
    width: auto;
    margin: 0;
    white-space: nowrap;
    flex-shrink: 0;
    font-size: 0.75rem;
  }
  .tab-btn.active {
    border-left: none;
    border-top-color: var(--accent);
    background: none;
    color: #fff;
  }
  header, #ia-banner, .search-bar, .sort-bar, nav, main, footer {
    margin-left: 0;
  }
  main { padding-bottom: 4rem; }
  .search-bar { top: 60px; }
  .sort-bar   { top: 100px; }
  #cat-nav    { top: 100px; }
}

/* ── Navegación de categorías (solo en pestaña Todas) ────────────────── */
#cat-nav {
  top: 140px;
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
  padding: 1.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
  transition: box-shadow 0.2s, transform 0.15s;
  position: relative;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.tarjeta-destacada:hover {
  box-shadow: 0 12px 40px rgba(0,0,0,0.12);
  transform: translateY(-2px);
}

.tarjeta-destacada .categoria-label {
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--accent);
  margin-bottom: -0.25rem;
}

.tarjeta-destacada .titulo {
  font-size: clamp(1.2rem, 1.5vw, 1.5rem);
  font-weight: 700;
  line-height: 1.25;
  letter-spacing: -0.025em;
}

.tarjeta-destacada .resumen {
  font-size: 0.855rem;
  color: var(--txt-2);
  line-height: 1.7;
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
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--txt-1);
  letter-spacing: -0.03em;
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
  top: 100px;
  z-index: 90;
}

.search-input {
  flex: 1;
  max-width: 480px;
  background: var(--surface);
  border: 1px solid var(--border-sub);
  border-radius: 9999px;
  color: var(--txt-1);
  font-family: inherit;
  font-size: 0.82rem;
  padding: 0.4rem 1rem;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.search-input::placeholder { color: var(--txt-3); }
.search-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(61,122,82,0.15);
}

.search-count {
  font-size: 0.72rem;
  color: var(--txt-3);
  white-space: nowrap;
}

.tarjeta[hidden], .tarjeta-destacada[hidden], .sintesis-card[hidden] {
  display: none !important;
}

/* ── Pestaña Síntesis ────────────────────────────────────────────────── */
.sintesis-header {
  margin-bottom: 2rem;
  padding-bottom: 0.875rem;
  border-bottom: 1px solid var(--border-sub);
}
.sintesis-header h2 { font-size: 1.4rem; font-weight: 800; color: var(--txt-1); letter-spacing: -0.03em; margin-bottom: 0.3rem; }
.sintesis-header p  { font-size: 0.78rem; color: var(--txt-3); }

.grid-sintesis {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(480px, 1fr));
  gap: 1.25rem;
}

.sintesis-card {
  background: var(--surface);
  border: 1px solid var(--border-sub);
  border-radius: var(--r);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  transition: box-shadow 0.18s, transform 0.15s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.sintesis-card:hover {
  box-shadow: 0 8px 32px rgba(0,0,0,0.10);
  transform: translateY(-1px);
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
  background: rgba(61,122,82,0.08);
  color: var(--accent);
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
  border: 1px solid rgba(61,122,82,0.2);
}

.sintesis-titulo {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--txt-1);
  line-height: 1.3;
  letter-spacing: -0.02em;
}

.sintesis-texto {
  font-size: 0.855rem;
  color: var(--txt-2);
  line-height: 1.75;
  white-space: pre-line;
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
.sintesis-fuente-link:hover { color: var(--accent); }

.sintesis-fuente-alt {
  font-size: 0.6rem;
  color: #dc2626;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  flex-shrink: 0;
}

.sin-sintesis {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--txt-3);
  font-size: 0.875rem;
  line-height: 1.7;
  max-width: 480px;
  margin: 0 auto;
}
.sin-sintesis h3 { color: var(--txt-1); font-size: 1rem; margin-bottom: .75rem; }
.sin-sintesis-nota { font-size: .78rem; margin-bottom: 1.5rem; color: var(--txt-3); }
.sin-sintesis button {
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: 9999px;
  padding: .65rem 1.4rem;
  font-size: .875rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity .15s;
}
.sin-sintesis button:hover { opacity: .85; }
.sin-sintesis button:disabled { opacity: .5; cursor: default; }

/* ── Pestaña Prensa Libertaria — acento rojo ─────────────────────────── */
#tab-libertaria .seccion-acento {
  background: linear-gradient(180deg, #dc2626, #f97316);
}

#tab-libertaria .seccion-titulo { color: var(--txt-1); }

#tab-libertaria .analisis-general {
  background: #fff8f5;
  border-color: #fbd5c5;
  border-left-color: #dc2626;
  color: #7f1d1d;
}
#tab-libertaria .analisis-general-titulo { color: #dc2626; }

.libertaria-header {
  background: #fff8f5;
  border: 1px solid #fbd5c5;
  border-left: 4px solid #dc2626;
  border-radius: var(--r);
  padding: 1rem 1.25rem;
  margin-bottom: 2.5rem;
  color: #7f1d1d;
  font-size: 0.85rem;
  line-height: 1.65;
}
.libertaria-header strong { color: #dc2626; display: block; margin-bottom: 0.3rem; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.08em; }

#tab-libertaria .tab-btn.active { border-left-color: #dc2626; color: #dc2626; }

/* ── Pestaña Estadísticas ────────────────────────────────────────────── */
.stats-header { margin-bottom: 2rem; padding-bottom: .875rem; border-bottom: 1px solid var(--border-sub); }
.stats-header h2 { font-size: 1rem; font-weight: 700; color: var(--txt-1); letter-spacing: -.02em; margin-bottom: .3rem; }
.stats-header p  { font-size: .78rem; color: var(--txt-3); }
.stats-fallidas {
  background: rgba(251,191,36,.07);
  border: 1px solid rgba(251,191,36,.25);
  border-radius: var(--r);
  padding: .75rem 1rem;
  margin-bottom: 1.5rem;
  font-size: .8rem;
  color: #fbbf24;
}
.stats-fallidas ul { margin: .4rem 0; padding-left: 1.2rem; color: var(--txt-2); }
.stats-fallidas span { font-size: .75rem; color: var(--txt-3); }

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
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.stat-kpi-valor {
  font-size: 2.2rem;
  font-weight: 800;
  background: linear-gradient(135deg, var(--accent), var(--accent-green));
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
  box-shadow: 0 0 0 2px var(--bg), 0 0 0 4px var(--accent);
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
  background: rgba(0, 0, 0, 0.4);
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
  border-left: 1px solid var(--border-sub);
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
  border-radius: 9999px;
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
  background: #edf5f0;
  border: 1px solid rgba(61,122,82,0.15);
  border-radius: calc(var(--r) - 2px);
  padding: 0.875rem 1rem;
  font-size: 0.82rem;
  color: #1c3828;
  line-height: 1.65;
}

.drawer-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-sub);
  display: flex;
  gap: 0.75rem;
  flex-shrink: 0;
  flex-wrap: wrap;
}
.drawer-btn {
  flex: 1;
  padding: 0.6rem 1rem;
  border-radius: 9999px;
  font-size: 0.82rem;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  border: none;
  transition: background 0.15s, opacity 0.15s;
  text-decoration: none;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
}
.drawer-btn-primary { background: var(--accent); color: #fff; }
.drawer-btn-primary:hover { background: #2a5c3b; }
.drawer-btn-secondary { background: var(--surface-2); color: var(--txt-1); border: 1px solid var(--border-sub); }
.drawer-btn-secondary:hover { background: var(--border-sub); }
.drawer-btn-translate { background: rgba(61,122,82,0.08); color: var(--accent); border: 1px solid rgba(61,122,82,0.2); }
.drawer-btn-translate:hover { background: rgba(61,122,82,0.14); }

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
.badge-sent-alarmista { background: #fef2f2; color: #b91c1c; }
.badge-sent-neutral   { background: #f3f4f6; color: #6b7280; }
.badge-sent-optimista { background: #f0fdf4; color: #16a34a; }

/* ── Badge multi-fuente verificado ───────────────────────────────────── */
.badge-verified {
  font-size: 0.55rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  background: rgba(61,122,82,0.08);
  color: var(--accent);
  border: 1px solid rgba(61,122,82,0.2);
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
.bookmark-btn:hover { color: #ff9f0a; transform: scale(1.15); }
.bookmark-btn.guardado { color: #ff9f0a; }

/* ── Resaltado de palabras clave ─────────────────────────────────────── */
.tarjeta.kw-match, .tarjeta-destacada.kw-match {
  border-left: 3px solid #ff9f0a;
}
.keywords-input {
  width: 200px;
  background: var(--surface);
  border: 1px solid var(--border-sub);
  border-radius: 9999px;
  color: var(--txt-1);
  font-family: inherit;
  font-size: 0.82rem;
  padding: 0.4rem 0.875rem;
  outline: none;
  transition: border-color 0.15s;
}
.keywords-input::placeholder { color: var(--txt-3); }
.keywords-input:focus { border-color: #ff9f0a; }
.kw-sep { color: var(--border); font-size: 1.1rem; user-select: none; }

/* ── Pestaña Asombro — acento violeta (conservado) ───────────────────── */
#tab-asombro { padding: 1rem; }
.asombro-header { text-align: center; padding: 2rem 0 1.5rem; }
.asombro-header h2 { font-size: 1.4rem; font-weight: 800; color: var(--txt-1); margin-bottom: .5rem; letter-spacing: -.03em; }
.asombro-header p { font-size: .85rem; color: var(--txt-3); max-width: 520px; margin: 0 auto; line-height: 1.7; }
.asombro-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px,1fr)); gap: 1.25rem; max-width: 1400px; margin: 0 auto; }
.asombro-card {
  background: var(--surface);
  border: 1px solid var(--border-sub);
  border-radius: var(--r);
  padding: 1.25rem;
  cursor: pointer;
  transition: transform .15s, box-shadow .15s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.asombro-card:hover { transform: translateY(-2px); box-shadow: 0 8px 32px rgba(124,58,237,.15); }
.asombro-score { font-size: 1rem; color: #7c3aed; margin-bottom: .45rem; letter-spacing: .1em; }
.asombro-cat { display: inline-block; font-size: .65rem; text-transform: uppercase; letter-spacing: .08em; color: #7c3aed; background: rgba(124,58,237,.08); border: 1px solid rgba(124,58,237,.25); border-radius: 9999px; padding: .1rem .5rem; margin-bottom: .6rem; }
.asombro-titulo { font-size: .95rem; font-weight: 700; color: var(--txt-1); margin-bottom: .35rem; line-height: 1.4; letter-spacing: -.01em; }
.asombro-titulo a { color: inherit; text-decoration: none; }
.asombro-titulo a:hover { color: #7c3aed; }
.asombro-fuente { font-size: .72rem; color: var(--txt-3); margin-bottom: .6rem; }
.asombro-razon { font-size: .8rem; color: #6d28d9; font-style: italic; margin-bottom: .6rem; line-height: 1.5; }
.asombro-resumen { font-size: .8rem; color: var(--txt-2); line-height: 1.6; }
.asombro-empty { text-align: center; padding: 5rem 1rem; color: var(--txt-3); }
.asombro-empty-icon { font-size: 3rem; margin-bottom: 1rem; }
.tab-btn[data-tab="asombro"].active { border-left-color: #7c3aed !important; color: #a78bfa !important; }

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
.sort-btn.active { background: var(--accent); color: #fff; border-color: var(--accent); font-weight: 600; }

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
  background: rgba(61,122,82,0.06);
  border: 1px solid rgba(61,122,82,0.2);
  border-radius: var(--r);
  padding: .6rem 1rem;
  margin: .75rem var(--pad-x);
  font-size: .8rem;
  color: #1c3828;
}
#ia-banner .ia-msg { flex: 1; }
#ia-banner .ia-regen {
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: 9999px;
  padding: .35rem .875rem;
  font-size: .78rem;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  white-space: nowrap;
  transition: background .15s;
}
#ia-banner .ia-regen:hover { background: #2a5c3b; }
#ia-banner .ia-regen:disabled { opacity: .5; cursor: default; }
#ia-banner .ia-close {
  background: none;
  border: none;
  color: #1c3828;
  cursor: pointer;
  font-size: 1.1rem;
  line-height: 1;
  padding: 0 .15rem;
}

/* ── Actualidad Absoluta ─────────────────────────────────────────────────── */
.actualidad-header {
  padding: 2rem 0 1.25rem;
  border-bottom: 1px solid var(--border-sub);
  margin-bottom: 1.75rem;
}
.actualidad-header h2 {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--txt-1);
  margin: 0 0 .35rem;
  letter-spacing: -0.035em;
}
.actualidad-header > p {
  color: var(--txt-3);
  font-size: .85rem;
  margin: 0 0 1rem;
}
.historial-filtros {
  display: flex;
  align-items: center;
  gap: .4rem;
  flex-wrap: wrap;
}
.historial-filtro-label {
  font-size: .75rem;
  color: var(--txt-3);
  font-weight: 600;
}
.historial-filtro-sep {
  color: var(--border);
  font-size: .85rem;
  margin: 0 .15rem;
}
.historial-filter-btn {
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--txt-2);
  border-radius: 999px;
  padding: .22rem .65rem;
  font-size: .72rem;
  font-weight: 600;
  cursor: pointer;
  transition: all .15s;
  white-space: nowrap;
}
.historial-filter-btn.active,
.historial-filter-btn:hover {
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
}
/* Cards — estructura compartida */
.proceso-card,
.proceso-card-hero {
  background: var(--surface);
  border: 1px solid var(--border-sub);
  border-left-width: 4px;
  border-radius: var(--r);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: box-shadow .15s, transform .1s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.proceso-card:hover,
.proceso-card-hero:hover {
  box-shadow: 0 8px 32px rgba(0,0,0,0.10);
  transform: translateY(-1px);
}
/* Borde izquierdo por estado */
.proceso-card[data-estado="escalada"],
.proceso-card-hero[data-estado="escalada"]   { border-left-color: #dc2626; }
.proceso-card[data-estado="estable"],
.proceso-card-hero[data-estado="estable"]    { border-left-color: #3b9eff; }
.proceso-card[data-estado="resolucion"],
.proceso-card-hero[data-estado="resolucion"] { border-left-color: #34c759; }
.proceso-card[data-estado="silencio"],
.proceso-card-hero[data-estado="silencio"]   { border-left-color: #9ca3af; }
/* Hero más grande */
.proceso-card-hero { margin-bottom: 1.5rem; }
.proceso-card-hero .proceso-nombre  { font-size: 1.3rem; }
.proceso-card-hero .proceso-resumen { font-size: .9rem; }
.proceso-card-hero .proceso-sparkline { height: 70px; }
.proceso-card-hero .proceso-watermark { font-size: 9rem; opacity: .04; }
/* Grid */
.proceso-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.25rem;
  padding-bottom: 3rem;
}
/* Strip de estado */
.proceso-strip {
  display: flex;
  align-items: center;
  gap: .35rem;
  padding: .42rem .9rem;
  font-size: .67rem;
  font-weight: 700;
  letter-spacing: .07em;
  flex-shrink: 0;
}
.proceso-strip-escalada   { background: rgba(220,38,38,.08);  color: #991b1b; }
.proceso-strip-estable    { background: rgba(59,158,255,.07); color: #1a4f80; }
.proceso-strip-resolucion { background: rgba(52,199,89,.08);  color: #166534; }
.proceso-strip-silencio   { background: rgba(107,114,128,.07); color: #374151; }
.proceso-strip-icono   { font-size: .85rem; }
.proceso-strip-dot     { opacity: .35; }
.proceso-strip-horizonte { font-size: .6rem; letter-spacing: .05em; opacity: .8; }
.proceso-strip-arts    { margin-left: auto; opacity: .65; font-weight: 400; letter-spacing: 0; }
/* Body */
.proceso-body {
  position: relative;
  overflow: hidden;
  padding: .9rem 1rem .75rem;
  display: flex;
  flex-direction: column;
  gap: .55rem;
  flex: 1;
}
.proceso-watermark {
  position: absolute;
  right: -.1rem;
  top: -.4rem;
  font-size: 6rem;
  font-weight: 900;
  line-height: 1;
  opacity: .05;
  color: var(--txt-1);
  pointer-events: none;
  user-select: none;
}
.proceso-nombre {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--txt-1);
  line-height: 1.3;
  position: relative;
  letter-spacing: -0.02em;
}
.proceso-descripcion {
  font-size: .79rem;
  color: var(--txt-2);
  line-height: 1.45;
}
.proceso-imp-row {
  display: flex;
  align-items: center;
  gap: .5rem;
}
.proceso-imp-track {
  flex: 1;
  height: 5px;
  background: var(--border-sub);
  border-radius: 3px;
  overflow: hidden;
}
.proceso-imp-fill {
  height: 100%;
  border-radius: 3px;
}
.proceso-imp-fill-escalada   { background: linear-gradient(90deg, #dc2626, #f87171); }
.proceso-imp-fill-estable    { background: linear-gradient(90deg, #3b9eff, #93c5fd); }
.proceso-imp-fill-resolucion { background: linear-gradient(90deg, #2dd4a0, #6ee7b7); }
.proceso-imp-fill-silencio   { background: linear-gradient(90deg, #6b7280, #d1d5db); }
.proceso-imp-num {
  font-size: .7rem;
  font-weight: 700;
  color: var(--txt-3);
  white-space: nowrap;
}
.proceso-resumen {
  font-size: .83rem;
  color: var(--txt-1);
  line-height: 1.55;
  margin: 0;
}
.proceso-articulos {
  list-style: none;
  margin: 0;
  padding: .55rem 0 0;
  border-top: 1px solid var(--border-sub);
  display: flex;
  flex-direction: column;
  gap: .28rem;
}
.proceso-articulos li  { font-size: .72rem; color: var(--txt-3); line-height: 1.3; }
.proceso-articulos a   { color: var(--accent); text-decoration: none; }
.proceso-articulos a:hover { text-decoration: underline; }
.proceso-art-fuente    { font-size: .67rem; color: var(--txt-3); }
/* Footer con sparkline */
.proceso-footer {
  border-top: 1px solid var(--border-sub);
  padding: .65rem 1rem .8rem;
  display: flex;
  flex-direction: column;
  gap: .3rem;
  background: rgba(0,0,0,0.012);
}
.proceso-trend-wrap {
  font-size: .75rem;
  font-weight: 600;
  min-height: 1.1em;
}
.proceso-spark-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.proceso-spark-label {
  font-size: .6rem;
  color: var(--txt-3);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .07em;
}
.proceso-sparkline {
  display: flex;
  align-items: flex-end;
  gap: 2px;
  height: 48px;
}
.spark-bar {
  flex: 1;
  border-radius: 2px 2px 0 0;
  min-height: 2px;
  cursor: default;
  transition: opacity .12s, transform .1s;
  transform-origin: bottom;
}
.spark-bar:hover {
  opacity: .7 !important;
  transform: scaleY(1.07);
}
.actualidad-empty {
  padding: 3rem 0;
  text-align: center;
  color: var(--txt-3);
  font-size: .88rem;
}

/* ── Conexiones entre procesos ───────────────────────────────────────────── */
.conexiones-panel {
  background: var(--surface);
  border: 1px solid var(--border-sub);
  border-left: 4px solid var(--accent-gold);
  border-radius: var(--r);
  padding: 1rem 1.1rem;
  margin-top: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: .6rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.conexiones-titulo {
  font-size: .72rem;
  font-weight: 700;
  color: var(--accent-gold);
  text-transform: uppercase;
  letter-spacing: .07em;
  margin-bottom: .2rem;
}
.conexion-item {
  display: flex;
  flex-direction: column;
  gap: .15rem;
  padding: .4rem 0;
  border-bottom: 1px solid var(--border-sub);
}
.conexion-item:last-child { border-bottom: none; }
.conexion-nombres {
  font-size: .75rem;
  font-weight: 700;
  color: var(--txt-2);
}
.conexion-rel {
  font-size: .78rem;
  color: var(--txt-1);
  line-height: 1.45;
}

/* ── Briefing ────────────────────────────────────────────────────────────── */
.briefing-btn {
  background: #1a2e1a !important;
  border-color: #1a2e1a !important;
  color: #fff !important;
}
.briefing-btn:hover {
  background: var(--accent) !important;
  border-color: var(--accent) !important;
}
#briefing-panel {
  background: var(--surface);
  border: 1.5px solid var(--border-sub);
  border-radius: var(--r);
  padding: 1.25rem 1.4rem;
  margin-bottom: 1.75rem;
  position: relative;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.briefing-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: .72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .07em;
  color: var(--txt-2);
  margin-bottom: .9rem;
  padding-bottom: .6rem;
  border-bottom: 1px solid var(--border-sub);
}
.briefing-close {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--txt-3);
  font-size: 1.1rem;
  line-height: 1;
}
.briefing-texto {
  font-size: .87rem;
  line-height: 1.65;
  color: var(--txt-1);
}
.briefing-texto strong {
  display: block;
  margin-top: .8rem;
  margin-bottom: .25rem;
  font-size: .72rem;
  text-transform: uppercase;
  letter-spacing: .07em;
  color: var(--accent);
}
.briefing-texto strong:first-child { margin-top: 0; }

/* ── Ruido / Señal ───────────────────────────────────────────────────────── */
.badge-senal {
  display: inline-flex;
  align-items: center;
  gap: .2rem;
  font-size: .62rem;
  font-weight: 700;
  padding: .15rem .45rem;
  border-radius: 999px;
  background: #f0fdf4;
  color: #16a34a;
  border: 1px solid #bbf7d0;
  white-space: nowrap;
}
.badge-ruido {
  display: inline-flex;
  align-items: center;
  gap: .2rem;
  font-size: .62rem;
  font-weight: 600;
  padding: .15rem .45rem;
  border-radius: 999px;
  background: #f3f4f6;
  color: #6b7280;
  border: 1px solid #d1d5db;
  white-space: nowrap;
  opacity: .85;
}
.tarjeta:has(.badge-ruido) {
  opacity: .82;
}

/* ── Alertas Vigilar ─────────────────────────────────────────────────────── */
#watch-panel {
  display: flex;
  flex-direction: column;
  gap: .6rem;
  margin-bottom: 1rem;
}
.watch-alerta {
  display: flex;
  align-items: flex-start;
  gap: .8rem;
  background: #fff7ed;
  border: 1.5px solid #fed7aa;
  border-left: 5px solid #ea580c;
  border-radius: var(--r);
  padding: .75rem 1rem;
}
.watch-icono {
  font-size: 1.1rem;
  flex-shrink: 0;
  margin-top: .05rem;
}
.watch-alerta strong {
  font-size: .82rem;
  color: #9a3412;
  display: block;
  margin-bottom: .2rem;
}
.watch-alerta p {
  font-size: .78rem;
  color: #7c2d12;
  margin: 0;
  line-height: 1.4;
}
.watch-confianza {
  margin-left: auto;
  font-size: .7rem;
  font-weight: 700;
  color: #ea580c;
  white-space: nowrap;
  flex-shrink: 0;
}

/* ═══════════════════════════════════════════════════════════════════════════
   EFECTOS VISUALES Y ENGAGEMENT
   ═══════════════════════════════════════════════════════════════════════════ */

/* ── Splash de portada ───────────────────────────────────────────────────── */
#splash {
  position: fixed; inset: 0; z-index: 9999;
  background: #060f06;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 2rem;
  cursor: pointer; transition: opacity 0.7s ease;
}
#splash.saliendo { opacity: 0; pointer-events: none; }
#splash.ido { display: none; }

.splash-eyebrow {
  font-size: 0.62rem; letter-spacing: 0.35em; text-transform: uppercase;
  color: rgba(255,255,255,0.28); font-weight: 600;
  animation: splashFadeUp 0.6s ease both;
}
.splash-logo {
  font-family: 'Playfair Display', Georgia, serif;
  font-size: clamp(2.8rem, 7vw, 5rem); font-weight: 800;
  color: #fff; letter-spacing: -0.04em; line-height: 1;
  text-align: center;
  animation: splashFadeUp 0.6s ease 0.1s both;
}
.splash-divider {
  width: 36px; height: 2px;
  background: linear-gradient(90deg, #3d7a52, #5aaa3a);
  border-radius: 1px;
  animation: splashFadeUp 0.6s ease 0.2s both;
}
.splash-headlines {
  display: flex; flex-direction: column; gap: 0.75rem;
  max-width: 540px; width: 88%;
}
.splash-hl {
  font-size: clamp(0.8rem, 1.3vw, 0.92rem);
  color: rgba(255,255,255,0.6); line-height: 1.5;
  padding-left: 0.85rem;
  border-left: 2px solid rgba(61,122,82,0.6);
  animation: splashHlIn 0.5s cubic-bezier(0.16,1,0.3,1) both;
}
.splash-hl:nth-child(1) { animation-delay: 0.3s; }
.splash-hl:nth-child(2) { animation-delay: 0.42s; }
.splash-hl:nth-child(3) { animation-delay: 0.54s; }
.splash-hint {
  font-size: 0.58rem; color: rgba(255,255,255,0.18);
  letter-spacing: 0.2em; text-transform: uppercase;
  animation: splashFadeUp 0.6s ease 0.7s both;
}
@keyframes splashFadeUp {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes splashHlIn {
  from { opacity: 0; transform: translateX(-10px); }
  to   { opacity: 1; transform: translateX(0); }
}

/* ── Animación staggered de tarjetas ─────────────────────────────────────── */
@keyframes cardIn {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}
.card-animate {
  animation: cardIn 0.42s cubic-bezier(0.16, 1, 0.3, 1) both;
  animation-delay: var(--card-delay, 0ms);
}

/* ── Transición suave entre pestañas ─────────────────────────────────────── */
@keyframes tabFadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
.tab-anim {
  animation: tabFadeIn 0.2s ease both;
}

/* ── Grain texture en el sidebar ─────────────────────────────────────────── */
.tab-bar { overflow: hidden; }
.tab-bar::after {
  content: '';
  position: absolute; inset: 0; pointer-events: none; z-index: 1;
  opacity: 0.045;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.82' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)'/%3E%3C/svg%3E");
  background-size: 220px 220px;
}
.tab-bar > * { position: relative; z-index: 2; }

/* ── Dark mode toggle en sidebar ─────────────────────────────────────────── */
.dark-toggle {
  position: absolute; bottom: 1rem; left: 1rem; right: 0.75rem;
  background: none; border: 1px solid rgba(255,255,255,0.1);
  color: rgba(255,255,255,0.3); border-radius: 9999px;
  padding: 0.3rem 0.75rem; font-size: 0.62rem; cursor: pointer;
  font-family: inherit; letter-spacing: 0.04em; text-align: center;
  transition: all 0.2s; white-space: nowrap; z-index: 3; position: relative;
}
.dark-toggle:hover {
  border-color: rgba(255,255,255,0.35);
  color: rgba(255,255,255,0.7);
  background: rgba(255,255,255,0.05);
}
@media (max-width: 768px) { .dark-toggle { display: none; } }

/* ── Modo oscuro ─────────────────────────────────────────────────────────── */
body.dark {
  --bg:         #0b160b;
  --surface:    #111d11;
  --surface-2:  #172417;
  --border:     rgba(90,170,58,0.13);
  --border-sub: rgba(90,170,58,0.07);
  --txt-1: #dff0df;
  --txt-2: #a4c4a4;
  --txt-3: #5a7a5a;
}
body.dark header {
  background: rgba(11,22,11,0.97);
  border-bottom-color: rgba(90,170,58,0.1);
}
body.dark nav { background: rgba(11,22,11,0.97); }
body.dark .search-bar, body.dark .sort-bar { background: var(--bg); }
body.dark .analisis-general {
  background: #142014; border-color: rgba(61,122,82,0.22); color: var(--txt-2);
}
body.dark .critica { background: #142014; color: var(--txt-2); }
body.dark .drawer { background: #111d11; }
body.dark .drawer-header,
body.dark .drawer-footer { border-color: var(--border-sub); }
body.dark .drawer-critica { background: #142014; color: var(--txt-2); }
body.dark #ia-banner {
  background: rgba(61,122,82,0.07); color: var(--txt-2);
  border-color: rgba(61,122,82,0.18);
}
body.dark .briefing-btn { background: #0a140a !important; border-color: #0a140a !important; }
body.dark .leyenda { background: var(--surface); }
body.dark .sintesis-card { background: var(--surface); }
body.dark .proceso-card, body.dark .proceso-card-hero { background: var(--surface); }
body.dark .stat-kpi, body.dark .stat-card { background: var(--surface); }
body.dark .tarjeta, body.dark .tarjeta-destacada { background: var(--surface); }
body.dark footer { border-top-color: var(--border-sub); }

/* ── Focus mode: drawer abierto ──────────────────────────────────────────── */
body.drawer-open .tarjeta,
body.drawer-open .tarjeta-destacada,
body.drawer-open .asombro-card {
  opacity: 0.18;
  pointer-events: none;
  transition: opacity 0.35s;
  transform: none !important;
}

/* ── Tensiómetro del día ──────────────────────────────────────────────────── */
.tension-wrap {
  display: flex; align-items: center; gap: 0.45rem; margin-top: 0.2rem;
}
.tension-dot {
  width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0;
  animation: tensionPulse 2.5s ease-in-out infinite;
}
@keyframes tensionPulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50%       { transform: scale(1.4); opacity: 0.7; }
}
.tension-label {
  font-size: 0.6rem; letter-spacing: 0.06em;
  text-transform: uppercase; font-weight: 700;
}
"""
