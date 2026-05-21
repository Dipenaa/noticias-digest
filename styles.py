"""
styles.py — CSS embebido del digest de noticias.
Importado por renderer.py como constante _CSS.
"""

_CSS = """
/* ── Variables — tema Bosque Otoñal (Axios) ──────────────────────────── */
:root {
  --bg:          #f4f1eb;   /* blanco cálido, casi imperceptible */
  --surface:     #ffffff;   /* blanco puro para cards */
  --surface-2:   #f0ece4;   /* hover muy sutil */
  --border:      #d0c9bf;   /* borde visible cálido */
  --border-sub:  #e6e0d8;   /* borde sutil */
  --txt-1:       #1a1208;   /* casi negro cálido */
  --txt-2:       #4a3828;   /* marrón medio */
  --txt-3:       #8a7868;   /* marrón muted */
  --accent:      #2d5a2d;   /* verde bosque — principal */
  --accent-blue: #5a4030;   /* marrón tierra */
  --accent-green:#557820;   /* olivo */
  --accent-gold: #a06010;   /* ámbar oscuro */
  --r:           0.375rem;
  --font-serif:  'Playfair Display', Georgia, 'Times New Roman', serif;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: system-ui, 'Segoe UI', -apple-system, sans-serif;
  background-color: var(--bg);
  color: var(--txt-1);
  line-height: 1.65;
  font-size: 15px;
  -webkit-font-smoothing: antialiased;
}

/* ── Cabecera ────────────────────────────────────────────────────────── */
header {
  background: var(--surface);
  border-bottom: 1px solid var(--border-sub);
  box-shadow: 0 1px 4px rgba(0,0,0,0.07);
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
  background: linear-gradient(135deg, #2d5a2d 0%, #557820 100%);
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
  background: rgba(244,241,235,0.97);
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

/* barra de color vertical que identifica la sección */
.seccion-acento {
  width: 4px;
  height: 1.2rem;
  background: linear-gradient(180deg, #557820, #2d5a2d);
  border-radius: 9999px;
  flex-shrink: 0;
}

.seccion-titulo {
  font-family: var(--font-serif);
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--txt-1);
  letter-spacing: -0.01em;
}

/* ── Bloque de análisis crítico general ──────────────────────────────── */
.analisis-general {
  background: #edf5ed;
  border: 1px solid #9cc89c;
  border-left: 3px solid var(--accent);
  border-radius: var(--r);
  padding: 0.9rem 1.2rem;
  margin-bottom: 1.5rem;
  color: #1a3a1a;
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
  transition: box-shadow 0.2s, transform 0.15s, border-color 0.2s;
}
.tarjeta:hover {
  border-color: var(--border);
  box-shadow:
    0 1px 4px rgba(45,90,45,0.08),
    0 4px 16px rgba(45,90,45,0.12);
  transform: translateY(-1px);
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
  font-family: var(--font-serif);
  font-size: 1.05rem;
  font-weight: 700;
  line-height: 1.35;
  letter-spacing: -0.01em;
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
  background: #edf5ed;
  border: 1px solid #9cc89c;
  border-left: 2px solid var(--accent);
  border-radius: calc(var(--r) - 1px);
  padding: 0.55rem 0.875rem;
  font-size: 0.77rem;
  color: #1a3a1a;
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

/* ── Sidebar de navegación ───────────────────────────────────────────── */
.tab-bar {
  position: fixed;
  left: 0; top: 0; bottom: 0;
  width: 210px;
  background: #ffffff;
  border-right: 1px solid var(--border-sub);
  border-bottom: none;
  padding: 4rem 0 2rem;
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  z-index: 100;
  overflow-y: auto;
}

.tab-bar::before {
  content: '📰  Digest';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4rem;
  display: flex;
  align-items: center;
  padding: 0 1.25rem;
  font-weight: 700;
  font-size: 0.9rem;
  color: var(--txt-1);
  border-bottom: 1px solid var(--border-sub);
  letter-spacing: -0.02em;
}

.tab-bar-section {
  font-size: 0.6rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--txt-3);
  padding: 1rem 1.25rem 0.4rem;
  user-select: none;
}

.tab-btn {
  background: none;
  border: none;
  border-left: 3px solid transparent;
  color: var(--txt-3);
  cursor: pointer;
  font-size: 0.82rem;
  font-weight: 500;
  font-family: inherit;
  letter-spacing: 0.005em;
  padding: 0.6rem 1rem 0.6rem 1.1rem;
  margin: 0 0.5rem 0 0;
  border-radius: 0 0.375rem 0.375rem 0;
  text-align: left;
  width: calc(100% - 0.5rem);
  transition: color 0.15s, background 0.15s, border-left-color 0.15s;
}
.tab-btn:hover {
  color: var(--txt-1);
  background: var(--surface-2);
}
.tab-btn.active {
  color: var(--accent);
  font-weight: 600;
  border-left-color: var(--accent);
  background: rgba(45,90,45,0.07);
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

/* Ajustar posiciones sticky (sin tab-bar horizontal que ocupaba ~40px) */
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
    border-top: 1px solid var(--border-sub);
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
    color: var(--accent);
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
  border-top: 3px solid var(--accent);
  border-radius: var(--r);
  padding: 1.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
  transition: box-shadow 0.2s, transform 0.15s, border-color 0.2s;
  position: relative;
}
.tarjeta-destacada:hover {
  border-color: var(--border);
  box-shadow:
    0 2px 8px rgba(45,90,45,0.1),
    0 8px 24px rgba(45,90,45,0.14);
  transform: translateY(-2px);
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
  font-family: var(--font-serif);
  font-size: clamp(1.2rem, 1.5vw, 1.5rem);
  font-weight: 700;
  line-height: 1.25;
  letter-spacing: -0.01em;
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
  font-family: var(--font-serif);
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--txt-1);
  letter-spacing: -0.01em;
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
.sintesis-header h2 { font-family: var(--font-serif); font-size: 1.3rem; font-weight: 700; color: var(--txt-1); letter-spacing: -0.01em; margin-bottom: 0.3rem; }
.sintesis-header p  { font-size: 0.78rem; color: var(--txt-3); }

.grid-sintesis {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(480px, 1fr));
  gap: 1.25rem;
}

.sintesis-card {
  background: var(--surface);
  border: 1px solid var(--border-sub);
  border-top: 3px solid var(--accent);
  border-radius: var(--r);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  transition: border-color 0.18s, box-shadow 0.18s;
}
.sintesis-card:hover {
  box-shadow: 0 4px 16px rgba(45,90,45,0.14);
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
  background: #e8f0e8;
  color: var(--accent);
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
  border: 1px solid #9cc89c;
}

.sintesis-titulo {
  font-family: var(--font-serif);
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--txt-1);
  line-height: 1.3;
  letter-spacing: -0.01em;
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
  border-radius: 8px;
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
  border-radius: 8px;
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
}
.stat-kpi-valor {
  font-size: 2.2rem;
  font-weight: 800;
  background: linear-gradient(135deg, var(--accent), var(--accent-gold));
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
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
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
  background: #edf5ed;
  border: 1px solid #9cc89c;
  border-radius: calc(var(--r) - 1px);
  padding: 0.875rem 1rem;
  font-size: 0.82rem;
  color: #1a3a1a;
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
.drawer-btn-primary:hover { background: #1b3d1b; }
.drawer-btn-secondary { background: var(--surface-2); color: var(--txt-1); border: 1px solid var(--border-sub); }
.drawer-btn-secondary:hover { background: var(--border-sub); }
.drawer-btn-translate { background: #e8f5e8; color: #2d5a2d; border: 1px solid #9cc89c; }
.drawer-btn-translate:hover { background: #d8ecd8; }

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
.badge-sent-optimista { background: #e8f5e8; color: #2d5a2d; }

/* ── Badge multi-fuente verificado ───────────────────────────────────── */
.badge-verified {
  font-size: 0.55rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  background: #e8f0e0;
  color: #2d5a2d;
  border: 1px solid #8ab48a;
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
.asombro-score { font-size: 1rem; color: #7c3aed; margin-bottom: .45rem; letter-spacing: .1em; }
.asombro-cat { display: inline-block; font-size: .65rem; text-transform: uppercase; letter-spacing: .08em; color: #7c3aed; background: rgba(124,58,237,.1); border: 1px solid rgba(124,58,237,.3); border-radius: 9999px; padding: .1rem .5rem; margin-bottom: .6rem; }
.asombro-titulo { font-size: .95rem; font-weight: 600; color: var(--txt-1); margin-bottom: .35rem; line-height: 1.4; }
.asombro-titulo a { color: inherit; text-decoration: none; }
.asombro-titulo a:hover { color: #a78bfa; }
.asombro-fuente { font-size: .72rem; color: var(--txt-3); margin-bottom: .6rem; }
.asombro-razon { font-size: .8rem; color: #6d28d9; font-style: italic; margin-bottom: .6rem; line-height: 1.5; }
.asombro-resumen { font-size: .8rem; color: var(--txt-2); line-height: 1.6; }
.asombro-empty { text-align: center; padding: 5rem 1rem; color: var(--txt-3); }
.asombro-empty-icon { font-size: 3rem; margin-bottom: 1rem; }
.tab-btn[data-tab="asombro"].active { border-left-color: #7c3aed !important; color: #7c3aed !important; }

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
  background: #f0f8f0;
  border: 1px solid #9cc89c;
  border-radius: var(--r);
  padding: .6rem 1rem;
  margin: .75rem var(--pad-x);
  font-size: .8rem;
  color: #1a3a1a;
}
#ia-banner .ia-msg { flex: 1; }
#ia-banner .ia-regen {
  background: #2d5a2d;
  color: #fff;
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
#ia-banner .ia-regen:hover { background: #1b3d1b; }
#ia-banner .ia-regen:disabled { opacity: .5; cursor: default; }
#ia-banner .ia-close {
  background: none;
  border: none;
  color: #1b3d1b;
  cursor: pointer;
  font-size: 1.1rem;
  line-height: 1;
  padding: 0 .15rem;
}
"""

