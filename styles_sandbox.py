"""
styles_sandbox.py — CSS del sandbox de diseño. Editar aquí sin tocar producción.
"""

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,400;0,500;0,600;0,700;0,800;0,900;1,400&family=Playfair+Display:wght@700;900&display=swap');

/* ═══════════════════════════════════════════════════════════════════════════
   Variables — Dark Premium
   ═══════════════════════════════════════════════════════════════════════════ */
:root {
  --bg:          #000000;
  --surface:     #0c0c0e;
  --surface-2:   #161618;
  --surface-3:   #1c1c1f;
  --border:      rgba(255,255,255,0.1);
  --border-sub:  rgba(255,255,255,0.05);
  --txt-1:       #f5f5f7;
  --txt-2:       #86868b;
  --txt-3:       #3d3d3f;
  --accent:      #4361ee;
  --accent-2:    #7b2fff;
  --accent-warm: #ff6b35;
  --accent-cyan: #06b6d4;
  --r:           12px;
  --font-serif:  'Playfair Display', Georgia, serif;
  --glow-blue:   rgba(67,97,238,0.18);
  --glow-purple: rgba(123,47,255,0.14);
  --accent-blue: #93adf0;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  background: var(--bg);
  color: var(--txt-1);
  line-height: 1.6;
  font-size: 15px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* ═══════════════════════════════════════════════════════════════════════════
   Header — Apple navbar
   ═══════════════════════════════════════════════════════════════════════════ */
header {
  background: rgba(0,0,0,0.72);
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
  border-bottom: 1px solid var(--border-sub);
  padding: 0 2.5rem;
  height: 52px;
  position: sticky; top: 0; z-index: 200;
  display: flex; justify-content: space-between; align-items: center; gap: 1rem;
}

.header-logo { display: flex; align-items: center; gap: 0.75rem; }

.header-logo .icono {
  width: 26px; height: 26px;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; flex-shrink: 0;
  box-shadow: 0 0 16px rgba(67,97,238,0.4);
}

.header-logo h1 {
  font-size: 0.82rem; font-weight: 700;
  color: var(--txt-1); letter-spacing: 0.04em;
  text-transform: uppercase;
}

header .meta { font-size: 0.62rem; color: var(--txt-3); text-align: right; line-height: 1.5; }

/* ═══════════════════════════════════════════════════════════════════════════
   Nav categorías — thin pill bar
   ═══════════════════════════════════════════════════════════════════════════ */
nav {
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(16px);
  padding: 0 2.5rem;
  height: 36px;
  display: flex; align-items: center; gap: 0.1rem;
  border-bottom: 1px solid var(--border-sub);
  position: sticky; top: 52px; z-index: 100; overflow-x: auto;
}
nav a {
  color: var(--txt-3); text-decoration: none;
  padding: 0.2rem 0.7rem; border-radius: 20px;
  font-size: 0.68rem; font-weight: 600; letter-spacing: 0.03em;
  text-transform: uppercase;
  transition: background 0.15s, color 0.15s; white-space: nowrap;
}
nav a:hover { background: var(--surface-2); color: var(--txt-2); }

/* ═══════════════════════════════════════════════════════════════════════════
   Layout
   ═══════════════════════════════════════════════════════════════════════════ */
main { max-width: 1360px; margin: 0 auto; padding: 3.5rem 2.5rem; }

/* ═══════════════════════════════════════════════════════════════════════════
   Leyenda de sesgo
   ═══════════════════════════════════════════════════════════════════════════ */
.leyenda {
  padding: 0 0 1rem; margin-bottom: 3.5rem;
  border-bottom: 1px solid var(--border-sub);
  display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;
}
.leyenda-titulo {
  font-size: 0.5rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.18em; color: var(--txt-3); white-space: nowrap;
}
.leyenda-items {
  display: flex; gap: 0;
  border-radius: 6px; overflow: hidden;
  border: 1px solid var(--border-sub);
}
.leyenda-items .badge {
  cursor: pointer; user-select: none; border-radius: 0;
  font-size: 0.48rem; padding: 0.22rem 0.65rem;
  opacity: 0.55; transition: opacity .15s, filter .15s;
  border-right: 1px solid rgba(0,0,0,0.2); flex-shrink: 0;
}
.leyenda-items .badge:last-child { border-right: none; }
.leyenda-items .badge:hover { opacity: 0.85; filter: brightness(1.2); }
.leyenda-items .badge.filtro-activo { opacity: 1; filter: brightness(1.3); }
.leyenda-tip { font-size: .55rem; color: var(--txt-3); font-style: italic; }
.filtro-aviso { font-size: .62rem; color: var(--accent); font-weight: 600; }
.filtro-clear-btn {
  background: none; border: 1px solid var(--border);
  color: var(--txt-3); border-radius: 4px; padding: .1rem .5rem;
  font-size: .58rem; cursor: pointer; font-family: inherit; transition: background .12s;
}
.filtro-clear-btn:hover { background: var(--surface-2); color: var(--txt-1); }

/* ═══════════════════════════════════════════════════════════════════════════
   Secciones — Apple-scale typography
   ═══════════════════════════════════════════════════════════════════════════ */
.seccion { margin-bottom: 7rem; scroll-margin-top: 100px; }

.seccion-header {
  display: flex; align-items: flex-end; justify-content: space-between;
  padding-bottom: 1.25rem; margin-bottom: 2.5rem;
  border-bottom: 1px solid var(--border-sub);
}

.seccion-acento { display: none; }

.seccion-titulo {
  font-family: var(--font-serif);
  font-size: clamp(2rem, 4vw, 3.25rem);
  font-weight: 900;
  letter-spacing: -0.045em;
  line-height: 0.95;
  background: linear-gradient(135deg, var(--txt-1) 0%, var(--txt-2) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Análisis general — blockquote sutil */
.analisis-general {
  background: none;
  border-left: 2px solid var(--border);
  padding: 0.5rem 0 0.5rem 1.25rem;
  margin-bottom: 2.5rem;
  color: var(--txt-3); font-size: 0.78rem; line-height: 1.75;
  font-style: italic;
}
.analisis-general-titulo { display: none; }

/* ═══════════════════════════════════════════════════════════════════════════
   Grid de tarjetas
   ═══════════════════════════════════════════════════════════════════════════ */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(440px, 1fr));
  gap: 1.25rem;
}

/* ═══════════════════════════════════════════════════════════════════════════
   Tarjeta — glassmorphism premium
   ═══════════════════════════════════════════════════════════════════════════ */
.tarjeta {
  background: rgba(255,255,255,0.033);
  border: 1px solid var(--border-sub);
  border-radius: var(--r);
  padding: 1.75rem 2rem;
  display: flex; flex-direction: column; gap: 1rem;
  cursor: pointer; position: relative; overflow: hidden;
  transition:
    transform  0.3s cubic-bezier(0.4, 0, 0.2, 1),
    box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1),
    border-color 0.25s, background 0.25s;
  will-change: transform;
}

/* Ambient glow blob — cada tarjeta tiene un orbe de luz sutil */
.tarjeta::before {
  content: '';
  position: absolute; top: -60px; right: -40px;
  width: 180px; height: 180px; border-radius: 50%;
  background: radial-gradient(circle, var(--glow-blue) 0%, transparent 70%);
  pointer-events: none; opacity: 0;
  transition: opacity 0.4s ease;
}
.tarjeta:hover::before { opacity: 1; }

.tarjeta:hover {
  transform: translateY(-6px) scale(1.014);
  background: rgba(255,255,255,0.055);
  border-color: rgba(255,255,255,0.14);
  box-shadow:
    0 30px 80px rgba(0,0,0,0.7),
    0 0 0 1px rgba(67,97,238,0.15),
    0 0 50px rgba(67,97,238,0.08);
  z-index: 10;
}

/* ── Hero card — primera de cada sección ─────────────────────────────────── */
.grid .tarjeta:first-child {
  grid-column: 1 / -1;
  padding: 3rem 3.5rem;
  background: linear-gradient(135deg,
    rgba(67,97,238,0.12) 0%,
    rgba(123,47,255,0.06) 50%,
    rgba(255,255,255,0.02) 100%
  );
  border-color: rgba(67,97,238,0.2);
  min-height: 220px;
}
.grid .tarjeta:first-child::before {
  width: 300px; height: 300px;
  top: -100px; right: -60px;
  opacity: 0.6;
}
.grid .tarjeta:first-child .titulo {
  font-size: clamp(1.6rem, 2.8vw, 2.2rem);
  letter-spacing: -0.035em; line-height: 1.18;
}
.grid .tarjeta:first-child .resumen {
  max-height: 8rem; font-size: 0.88rem;
}
.grid .tarjeta:first-child:hover {
  transform: translateY(-5px);
  box-shadow:
    0 40px 100px rgba(0,0,0,0.7),
    0 0 0 1px rgba(67,97,238,0.25),
    0 0 80px rgba(67,97,238,0.1);
}

/* ═══════════════════════════════════════════════════════════════════════════
   Meta (fuente + fecha + badges)
   ═══════════════════════════════════════════════════════════════════════════ */
.tarjeta-meta { display: flex; flex-direction: column; gap: 0.5rem; }

.fuente-bloque {
  display: flex; flex-direction: row;
  align-items: center; justify-content: space-between; gap: 0.5rem;
}
.fuente-nombre {
  font-size: 0.7rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.07em;
  color: var(--txt-2);
}
.fecha { font-size: 0.6rem; color: var(--txt-3); flex-shrink: 0; }

/* ═══════════════════════════════════════════════════════════════════════════
   Badges & spectrum bars
   ═══════════════════════════════════════════════════════════════════════════ */
.badges { display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap; }

.badge {
  display: inline-block; font-size: 0.52rem; font-weight: 700;
  letter-spacing: 0.05em; padding: 0.15rem 0.5rem;
  border-radius: 4px; color: #fff;
}

.badge-etiqueta {
  font-size: 0.42rem; font-weight: 700; letter-spacing: 0.1em;
  text-transform: uppercase; color: var(--txt-3); display: inline-block;
}

/* Spectrum bars — card view */
.badges .badge {
  display: inline-block; background: none !important; border: none;
  padding: 0; font-size: 0; position: relative;
  width: 52px; height: 10px; vertical-align: middle;
  flex-shrink: 0; cursor: help;
}
.badges .badge::before {
  content: ''; position: absolute; left: 0; right: 0;
  top: 50%; transform: translateY(-50%); height: 2px;
  background: linear-gradient(to right, #4f8ef7, #7baff7, #6b7280, #f07040, #ef4444);
  border-radius: 2px; opacity: 0.25;
}
.badges .badge::after {
  content: ''; position: absolute; width: 8px; height: 8px;
  border-radius: 50%; top: 50%; transform: translateY(-50%);
  background: var(--dot-color, #6b7280); left: var(--dot-left, 22px);
  border: 1.5px solid var(--surface); box-shadow: 0 1px 4px rgba(0,0,0,0.5);
}
.badges .badge[title="izquierda"]        { --dot-left: 1px;  --dot-color: #4f8ef7; }
.badges .badge[title="centro-izquierda"] { --dot-left: 11px; --dot-color: #7baff7; }
.badges .badge[title="centro"]           { --dot-left: 22px; --dot-color: #7a7a8a; }
.badges .badge[title="centro-derecha"]   { --dot-left: 33px; --dot-color: #f07040; }
.badges .badge[title="derecha"]          { --dot-left: 43px; --dot-color: #ef4444; }
.badges .badge[title="desconocido"]::before { opacity: 0.06; }
.badges .badge[title="desconocido"]::after  { display: none; }

/* Drawer spectrum bars */
.drawer-badges .badge {
  display: inline-block; background: none !important; border: none;
  padding: 0; font-size: 0; position: relative; width: 64px; height: 12px;
  vertical-align: middle; flex-shrink: 0; cursor: help;
}
.drawer-badges .badge::before {
  content: ''; position: absolute; left: 0; right: 0;
  top: 50%; transform: translateY(-50%); height: 2px;
  background: linear-gradient(to right, #4f8ef7, #7baff7, #6b7280, #f07040, #ef4444);
  border-radius: 2px; opacity: 0.3;
}
.drawer-badges .badge::after {
  content: ''; position: absolute; width: 10px; height: 10px;
  border-radius: 50%; top: 50%; transform: translateY(-50%);
  background: var(--dot-color, #6b7280); left: var(--dot-left, 27px);
  border: 2px solid #0c0c0e; box-shadow: 0 1px 6px rgba(0,0,0,0.6);
}
.drawer-badges .badge[title="izquierda"]        { --dot-left: 1px;  --dot-color: #4f8ef7; }
.drawer-badges .badge[title="centro-izquierda"] { --dot-left: 14px; --dot-color: #7baff7; }
.drawer-badges .badge[title="centro"]           { --dot-left: 27px; --dot-color: #7a7a8a; }
.drawer-badges .badge[title="centro-derecha"]   { --dot-left: 40px; --dot-color: #f07040; }
.drawer-badges .badge[title="derecha"]          { --dot-left: 53px; --dot-color: #ef4444; }
.drawer-badges .badge[title="desconocido"]::before { opacity: 0.08; }
.drawer-badges .badge[title="desconocido"]::after  { display: none; }

/* ═══════════════════════════════════════════════════════════════════════════
   Título
   ═══════════════════════════════════════════════════════════════════════════ */
.titulo {
  font-family: var(--font-serif);
  font-size: 1.2rem; font-weight: 700;
  line-height: 1.25; letter-spacing: -0.025em;
}
.titulo a {
  color: var(--txt-1); text-decoration: none;
  background: linear-gradient(var(--accent-cyan), var(--accent-cyan)) no-repeat 0 100%;
  background-size: 0% 1px;
  transition: background-size 0.35s ease, color 0.2s;
}
.tarjeta:hover .titulo a { color: #f5f5f7; background-size: 100% 1px; }

/* ═══════════════════════════════════════════════════════════════════════════
   Resumen — expande al hover
   ═══════════════════════════════════════════════════════════════════════════ */
.resumen {
  font-size: 0.84rem; color: var(--txt-2); line-height: 1.75;
  overflow: hidden; max-height: 5.25rem;
  transition: max-height 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}
.tarjeta:hover .resumen { max-height: 20rem; }

/* ═══════════════════════════════════════════════════════════════════════════
   Crítica IA — emerge al hover
   ═══════════════════════════════════════════════════════════════════════════ */
.critica {
  border: none; padding: 0; font-size: 0.71rem;
  color: var(--txt-3); line-height: 1.65;
  max-height: 0; overflow: hidden; opacity: 0;
  transition:
    max-height 0.45s cubic-bezier(0.4, 0, 0.2, 1),
    opacity 0.3s ease 0.05s,
    padding 0.3s ease,
    border-color 0.3s ease;
  border-top: 1px solid transparent;
}
.tarjeta:hover .critica {
  max-height: 10rem; opacity: 1;
  padding-top: 0.875rem; border-top-color: var(--border-sub);
}
.critica::before {
  content: 'ANÁLISIS IA';
  display: block; font-size: 0.46rem; font-weight: 800;
  letter-spacing: 0.2em; color: var(--accent-cyan); margin-bottom: 0.4rem;
}
.critica-icono { display: none; }

/* ═══════════════════════════════════════════════════════════════════════════
   Sin artículos / Footer
   ═══════════════════════════════════════════════════════════════════════════ */
.sin-articulos { color: var(--txt-3); font-size: 0.85rem; padding: 0.5rem 0; }

footer {
  text-align: center; padding: 2.5rem;
  color: var(--txt-3); font-size: 0.6rem;
  border-top: 1px solid var(--border-sub); margin-top: 2rem;
  letter-spacing: 0.08em; text-transform: uppercase;
}

/* ═══════════════════════════════════════════════════════════════════════════
   Pestañas
   ═══════════════════════════════════════════════════════════════════════════ */
.tab-content { display: none; }

/* ═══════════════════════════════════════════════════════════════════════════
   Sidebar
   ═══════════════════════════════════════════════════════════════════════════ */
.tab-bar {
  position: fixed; left: 0; top: 0; bottom: 0; width: 220px;
  background: #050507;
  border-right: 1px solid var(--border-sub);
  padding: 4rem 0 5rem;
  display: flex; flex-direction: column; gap: 0;
  z-index: 300; overflow-y: auto; overflow-x: hidden;
}

.tab-bar::before {
  content: 'DIGEST';
  position: absolute; top: 0; left: 0; right: 0; height: 4rem;
  display: flex; align-items: center; padding: 0 1.5rem;
  font-weight: 900; font-size: 0.7rem; letter-spacing: 0.28em;
  color: var(--txt-1); border-bottom: 1px solid var(--border-sub);
}

.tab-bar-section {
  font-size: 0.44rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.2em; color: var(--txt-3);
  padding: 1.25rem 1rem 0.4rem; user-select: none;
}

.tab-btn {
  background: none; border: none; border-left: 2px solid transparent;
  color: rgba(255,255,255,0.58);
  cursor: pointer;
  font-size: 0.76rem; font-weight: 500; font-family: inherit;
  letter-spacing: 0.005em;
  padding: 0.45rem 0.875rem 0.45rem 0.75rem;
  text-align: left;
  width: calc(100% - 0.75rem);
  margin: 0 0.375rem 0.08rem 0.375rem;
  border-radius: 7px;
  transition: color 0.15s, background 0.15s, border-color 0.15s;
  display: block;
}
.tab-btn:hover {
  color: rgba(255,255,255,0.88);
  background: rgba(255,255,255,0.06);
}
.tab-btn.active {
  color: #c7d2fe;
  font-weight: 700;
  background: rgba(67,97,238,0.2);
  border-left-color: var(--accent);
}

/* Desplazar contenido */
header, #ia-banner, .search-bar, .sort-bar, nav, main, footer {
  margin-left: 220px;
}
header    { top: 0; }
.search-bar { top: 52px; }
#cat-nav    { top: 84px; }

/* ═══════════════════════════════════════════════════════════════════════════
   Mobile
   ═══════════════════════════════════════════════════════════════════════════ */
@media (max-width: 768px) {
  .tab-bar {
    position: fixed; left: 0; right: 0; bottom: 0; top: auto;
    width: 100%; height: auto; padding: 0; flex-direction: row;
    overflow-x: auto; overflow-y: hidden;
    border-right: none; border-top: 1px solid var(--border-sub);
    gap: 0; z-index: 200; background: rgba(5,5,7,0.95);
    backdrop-filter: blur(20px);
  }
  .tab-bar::before { display: none; }
  .tab-bar-section { display: none; }
  .tab-btn {
    padding: 0.7rem 0.875rem; border-left: none;
    border-top: 2px solid transparent; border-radius: 0;
    text-align: center; width: auto; margin: 0;
    white-space: nowrap; flex-shrink: 0; font-size: 0.68rem;
  }
  .tab-btn.active {
    border-left: none; border-top-color: var(--accent);
    background: none; color: var(--txt-1);
  }
  header, #ia-banner, .search-bar, .sort-bar, nav, main, footer { margin-left: 0; }
  main { padding-bottom: 4.5rem; }
  .search-bar { top: 52px; }
  #cat-nav { top: 84px; }
  .search-bar::after { display: none; }
}

#cat-nav { top: 84px; }

/* ═══════════════════════════════════════════════════════════════════════════
   Tarjeta destacada
   ═══════════════════════════════════════════════════════════════════════════ */
.grid-destacadas {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(460px, 1fr));
  gap: 1.25rem; margin-bottom: 2rem;
}
.tarjeta-destacada {
  background: rgba(255,255,255,0.033);
  border: 1px solid var(--border-sub); border-radius: var(--r);
  padding: 2.25rem; display: flex; flex-direction: column; gap: 1rem;
  cursor: pointer; position: relative; overflow: hidden;
  transition: transform 0.3s cubic-bezier(0.4,0,0.2,1), box-shadow 0.3s, border-color 0.25s, background 0.25s;
  will-change: transform;
}
.tarjeta-destacada:hover {
  transform: translateY(-6px) scale(1.012);
  background: rgba(255,255,255,0.055); border-color: rgba(255,255,255,0.14);
  box-shadow: 0 30px 80px rgba(0,0,0,0.7), 0 0 0 1px rgba(67,97,238,0.15);
  z-index: 10;
}
.tarjeta-destacada .categoria-label {
  font-size: 0.55rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.14em; color: var(--accent-cyan);
}
.tarjeta-destacada .fuente-nombre { font-size: 0.72rem; color: var(--txt-2); }
.tarjeta-destacada .titulo { font-size: clamp(1.2rem, 1.8vw, 1.6rem); font-weight: 700; }
.tarjeta-destacada .resumen { font-size: 0.85rem; color: var(--txt-2); line-height: 1.75; display: block; overflow: visible; }
.tarjeta-destacada .critica { font-size: 0.78rem; }
.destacadas-header { margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid var(--border-sub); }
.destacadas-header h2 { font-family: var(--font-serif); font-size: 1.8rem; font-weight: 900; color: var(--txt-1); letter-spacing: -0.03em; margin-bottom: 0.3rem; }
.destacadas-header p { font-size: 0.73rem; color: var(--txt-3); }
.sin-destacadas { color: var(--txt-3); font-size: 0.875rem; padding: 3rem 0; text-align: center; }

/* ═══════════════════════════════════════════════════════════════════════════
   Buscador — Spotlight style
   ═══════════════════════════════════════════════════════════════════════════ */
.kw-sep { display: none; }
.keywords-input { display: none; }

.search-bar {
  display: flex; align-items: center; gap: 0.6rem;
  padding: 0.3rem 2.5rem; background: transparent;
  border-bottom: none; position: sticky; z-index: 90;
}

.search-input {
  width: 180px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 20px; color: var(--txt-1); font-family: inherit;
  font-size: 0.74rem; padding: 0.3rem 0.875rem 0.3rem 1.9rem;
  outline: none;
  transition: width 0.4s cubic-bezier(0.4,0,0.2,1), box-shadow 0.25s, border-color 0.2s, background 0.2s;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2344445c' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='11' cy='11' r='8'/%3E%3Cpath d='m21 21-4.35-4.35'/%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: 0.65rem center; background-size: 12px 12px;
}
.search-input::placeholder { color: var(--txt-3); font-size: 0.72rem; }
.search-input:focus {
  width: 400px; border-color: var(--accent); border-radius: 10px;
  background-color: rgba(255,255,255,0.09);
  box-shadow: 0 0 0 3px rgba(67,97,238,0.2), 0 8px 32px rgba(0,0,0,0.4);
}

.search-count { font-size: 0.6rem; color: var(--txt-3); white-space: nowrap; flex-shrink: 0; }
.search-bar::after {
  content: '⌘K'; font-size: 0.46rem; font-weight: 700; letter-spacing: 0.08em;
  color: var(--txt-3); background: var(--surface-2); border: 1px solid var(--border-sub);
  border-radius: 3px; padding: 0.14rem 0.38rem; flex-shrink: 0; pointer-events: none;
}

/* ═══════════════════════════════════════════════════════════════════════════
   Sort bar — control segmentado iOS
   ═══════════════════════════════════════════════════════════════════════════ */
.sort-bar {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0.28rem 2.5rem;
  background: transparent;
  border-bottom: 1px solid var(--border-sub);
  position: sticky;
  top: 84px;
  z-index: 88;
  gap: 0;
}
.sort-label { display: none; }
.sort-btn {
  font-size: 0.58rem; font-weight: 600; letter-spacing: 0.025em;
  padding: 0.22rem 0.7rem;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.07);
  border-right: none;
  color: rgba(255,255,255,0.25);
  cursor: pointer; font-family: inherit;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
  white-space: nowrap;
}
.sort-btn:first-of-type { border-radius: 5px 0 0 5px; }
.sort-btn:last-of-type  { border-radius: 0 5px 5px 0; border-right: 1px solid rgba(255,255,255,0.07); }
.sort-btn:hover { background: rgba(255,255,255,0.08); color: rgba(255,255,255,0.6); }
.sort-btn.active {
  background: rgba(67,97,238,0.2);
  border-color: rgba(67,97,238,0.35);
  color: #8ba4f8;
}
.sort-btn.active + .sort-btn { border-left-color: rgba(67,97,238,0.35); }
/* Solo los 4 primeros botones de ordenar */
.sort-btn:nth-child(n+6) { display: none; }
/* El 4º botón visible (5º hijo = Destacados primero) cierra el grupo */
.sort-btn:nth-child(5) { border-radius: 0 5px 5px 0 !important; border-right: 1px solid rgba(255,255,255,0.07) !important; }

/* ═══════════════════════════════════════════════════════════════════════════
   Síntesis
   ═══════════════════════════════════════════════════════════════════════════ */
.sintesis-header { margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid var(--border-sub); }
.sintesis-header h2 { font-family: var(--font-serif); font-size: 1.8rem; font-weight: 900; color: var(--txt-1); letter-spacing: -0.03em; margin-bottom: 0.3rem; }
.sintesis-header p { font-size: 0.73rem; color: var(--txt-3); }

.grid-sintesis {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(500px, 1fr)); gap: 1.25rem;
}
.sintesis-card {
  background: rgba(255,255,255,0.033); border: 1px solid var(--border-sub);
  border-radius: var(--r); padding: 2rem; display: flex; flex-direction: column; gap: 1rem;
  cursor: pointer; position: relative; overflow: hidden;
  transition: transform 0.3s cubic-bezier(0.4,0,0.2,1), box-shadow 0.3s, border-color 0.25s, background 0.25s;
  will-change: transform;
}
.sintesis-card:hover {
  transform: translateY(-5px) scale(1.008);
  background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.12);
  box-shadow: 0 25px 70px rgba(0,0,0,0.65), 0 0 0 1px rgba(67,97,238,0.1);
  z-index: 10;
}
.sintesis-meta { display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; }
.sintesis-fuentes-count {
  font-size: 0.52rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em;
  background: rgba(67,97,238,0.1); color: var(--accent-blue); padding: 0.13rem 0.5rem;
  border-radius: 4px; border: 1px solid rgba(67,97,238,0.2);
}
.sintesis-titulo { font-family: var(--font-serif); font-size: 1.25rem; font-weight: 700; color: var(--txt-1); line-height: 1.3; letter-spacing: -0.02em; }
.sintesis-texto { font-size: 0.82rem; color: var(--txt-2); line-height: 1.8; white-space: pre-line; }
.sintesis-fuentes { border-top: 1px solid var(--border-sub); padding-top: 0.875rem; display: flex; flex-direction: column; gap: 0.4rem; }
.sintesis-fuente-item { display: flex; align-items: baseline; gap: 0.5rem; font-size: 0.78rem; }
.sintesis-fuente-nombre { color: var(--txt-3); font-weight: 600; font-size: 0.58rem; text-transform: uppercase; letter-spacing: 0.09em; white-space: nowrap; min-width: 110px; }
.sintesis-fuente-link { color: var(--txt-2); text-decoration: none; line-height: 1.4; transition: color 0.12s; }
.sintesis-fuente-link:hover { color: var(--txt-1); }
.sintesis-fuente-alt { font-size: 0.54rem; color: #f87171; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; flex-shrink: 0; }
.sin-sintesis { text-align: center; padding: 4rem 2rem; color: var(--txt-3); font-size: 0.875rem; line-height: 1.7; max-width: 480px; margin: 0 auto; }
.sin-sintesis h3 { color: var(--txt-1); font-size: 1rem; margin-bottom: .75rem; }
.sin-sintesis-nota { font-size: .76rem; margin-bottom: 1.5rem; color: var(--txt-3); }
.sin-sintesis button { background: var(--accent); color: #fff; border: none; border-radius: 6px; padding: .6rem 1.4rem; font-size: .875rem; font-weight: 600; cursor: pointer; transition: opacity .15s; }
.sin-sintesis button:hover { opacity: .85; }
.sin-sintesis button:disabled { opacity: .5; cursor: default; }

/* ═══════════════════════════════════════════════════════════════════════════
   Libertaria
   ═══════════════════════════════════════════════════════════════════════════ */
#tab-libertaria .seccion-acento { background: #ef4444; }
#tab-libertaria .analisis-general { border-left-color: #ef4444; }
.libertaria-header {
  background: rgba(239,68,68,0.05); border: 1px solid rgba(239,68,68,0.14);
  border-left: 2px solid #ef4444; border-radius: var(--r);
  padding: 0.875rem 1.1rem; margin-bottom: 2rem;
  color: var(--txt-2); font-size: 0.82rem; line-height: 1.65;
}
.libertaria-header strong { color: #ef4444; display: block; margin-bottom: 0.3rem; font-size: 0.58rem; text-transform: uppercase; letter-spacing: 0.1em; }
#tab-libertaria .tab-btn.active { border-left-color: #ef4444; }

/* ═══════════════════════════════════════════════════════════════════════════
   Estadísticas
   ═══════════════════════════════════════════════════════════════════════════ */
.stats-header { margin-bottom: 2rem; padding-bottom: .75rem; border-bottom: 1px solid var(--border-sub); }
.stats-header h2 { font-family: var(--font-serif); font-size: 1.8rem; font-weight: 900; color: var(--txt-1); letter-spacing: -.03em; margin-bottom: .3rem; }
.stats-header p { font-size: .73rem; color: var(--txt-3); }
.stats-fallidas { background: rgba(245,158,11,0.06); border: 1px solid rgba(245,158,11,0.18); border-radius: var(--r); padding: .7rem 1rem; margin-bottom: 1.5rem; font-size: .77rem; color: var(--accent-warm); }
.stats-fallidas ul { margin: .4rem 0; padding-left: 1.2rem; color: var(--txt-2); }
.stats-fallidas span { font-size: .7rem; color: var(--txt-3); }
.stats-kpi-row { display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 2rem; }
.stat-kpi { background: rgba(255,255,255,0.033); border: 1px solid var(--border-sub); border-radius: var(--r); padding: 1.5rem; min-width: 150px; flex: 1; }
.stat-kpi-valor { font-size: 2.4rem; font-weight: 900; color: var(--accent); letter-spacing: -.05em; line-height: 1; }
.stat-kpi-label { font-size: .58rem; color: var(--txt-3); margin-top: .4rem; text-transform: uppercase; letter-spacing: .1em; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }
.stat-card { background: rgba(255,255,255,0.033); border: 1px solid var(--border-sub); border-radius: var(--r); padding: 1.25rem 1.5rem; }
.stat-card-title { font-size: .54rem; font-weight: 700; text-transform: uppercase; letter-spacing: .14em; color: var(--txt-3); margin-bottom: 1rem; }
.stat-bar-row { display: flex; align-items: center; gap: .75rem; margin-bottom: .55rem; }
.stat-bar-label { font-size: .7rem; color: var(--txt-2); min-width: 120px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.stat-bar-bg { flex: 1; background: var(--surface-3); border-radius: 2px; height: 3px; min-width: 40px; }
.stat-bar-fill { height: 3px; border-radius: 2px; min-width: 2px; transition: width .6s cubic-bezier(.4,0,.2,1); }
.stat-bar-count { font-size: .67rem; color: var(--txt-3); min-width: 22px; text-align: right; }

/* ═══════════════════════════════════════════════════════════════════════════
   Drawer lateral — premium
   ═══════════════════════════════════════════════════════════════════════════ */
.drawer-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.75);
  z-index: 500; opacity: 0; pointer-events: none;
  transition: opacity 0.25s; backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px);
}
.drawer-overlay.open { opacity: 1; pointer-events: all; }

.drawer {
  position: fixed; top: 0; right: 0; height: 100%;
  width: min(580px, 100vw);
  background: #09090b;
  border-left: 1px solid var(--border-sub);
  z-index: 501; display: flex; flex-direction: column;
  transform: translateX(100%);
  transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: -16px 0 60px rgba(0,0,0,0.8);
}
.drawer.open { transform: translateX(0); }

.drawer-header {
  padding: 1.25rem 1.75rem; border-bottom: 1px solid var(--border-sub);
  display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; flex-shrink: 0;
}
.drawer-header-meta { display: flex; flex-direction: column; gap: 0.35rem; min-width: 0; }
.drawer-categoria { font-size: 0.52rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.16em; color: var(--accent-cyan); }
.drawer-fuente-row { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
.drawer-reading { font-size: 0.58rem; color: var(--txt-3); display: flex; align-items: center; gap: 0.25rem; }

.drawer-close {
  background: none; border: 1px solid var(--border-sub); color: var(--txt-3);
  border-radius: 6px; width: 30px; height: 30px; cursor: pointer; font-size: 0.8rem;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  transition: background 0.12s, color 0.12s;
}
.drawer-close:hover { background: var(--surface-2); color: var(--txt-1); }

.drawer-body { padding: 1.75rem; overflow-y: auto; flex: 1; display: flex; flex-direction: column; gap: 1.5rem; }
.drawer-badges { display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap; }
.drawer-titulo { font-family: var(--font-serif); font-size: 1.65rem; font-weight: 900; line-height: 1.2; letter-spacing: -0.03em; color: var(--txt-1); }
.drawer-resumen { font-size: 0.9rem; color: var(--txt-2); line-height: 1.9; }
.drawer-critica {
  background: rgba(6,182,212,0.05); border: none;
  border-left: 2px solid var(--accent-cyan); border-radius: 0 var(--r) var(--r) 0;
  padding: 0.875rem 1.25rem;
  font-size: 0.8rem; color: var(--txt-2); line-height: 1.7;
}
.drawer-critica::before {
  content: 'ANÁLISIS IA'; display: block; font-size: 0.46rem; font-weight: 800;
  letter-spacing: 0.2em; color: var(--accent-cyan); margin-bottom: 0.4rem;
}

.drawer-footer {
  padding: 1rem 1.75rem; border-top: 1px solid var(--border-sub);
  display: flex; gap: 0.75rem; flex-shrink: 0; flex-wrap: wrap;
}
.drawer-btn {
  flex: 1; padding: 0.6rem 1rem; border-radius: 8px;
  font-size: 0.76rem; font-weight: 600; font-family: inherit;
  cursor: pointer; border: none; transition: background 0.15s, opacity 0.15s;
  text-decoration: none; display: flex; align-items: center; justify-content: center; gap: 0.4rem;
}
.drawer-btn-primary { background: var(--accent); color: #fff; }
.drawer-btn-primary:hover { background: #2d4fd6; }
.drawer-btn-secondary { background: var(--surface-2); color: var(--txt-1); border: 1px solid var(--border-sub); }
.drawer-btn-secondary:hover { background: var(--surface-3); }
.drawer-btn-translate { background: rgba(6,182,212,0.08); color: var(--accent-cyan); border: 1px solid rgba(6,182,212,0.2); }
.drawer-btn-translate:hover { background: rgba(6,182,212,0.14); }

.tarjeta, .tarjeta-destacada { cursor: pointer; }
.tarjeta:active, .tarjeta-destacada:active { transform: scale(0.998); }

/* ═══════════════════════════════════════════════════════════════════════════
   Sentimiento / badges varios
   ═══════════════════════════════════════════════════════════════════════════ */
.badge-sent { font-size: 0.48rem; font-weight: 700; letter-spacing: 0.05em; padding: 0.1rem 0.4rem; border-radius: 4px; }
.badge-sent-alarmista { background: rgba(239,68,68,0.12); color: #f87171; }
.badge-sent-neutral   { background: rgba(255,255,255,0.05); color: var(--txt-3); }
.badge-sent-optimista { background: rgba(45,212,160,0.1); color: #4ade80; }
.badge-verified { font-size: 0.48rem; font-weight: 700; letter-spacing: 0.07em; padding: 0.1rem 0.4rem; border-radius: 4px; background: rgba(67,97,238,0.1); color: var(--accent-blue); border: 1px solid rgba(67,97,238,0.2); }
.badge-senal { font-size: 0.48rem; font-weight: 700; padding: 0.1rem 0.4rem; border-radius: 4px; background: rgba(6,182,212,0.1); color: var(--accent-cyan); border: 1px solid rgba(6,182,212,0.2); }
.badge-ruido { font-size: 0.48rem; font-weight: 700; padding: 0.1rem 0.4rem; border-radius: 4px; background: rgba(255,255,255,0.04); color: var(--txt-3); }
.bookmark-btn { background: none; border: none; cursor: pointer; font-size: 0.8rem; color: var(--txt-3); padding: 0.1rem 0.2rem; border-radius: 4px; line-height: 1; transition: color 0.15s; flex-shrink: 0; }
.bookmark-btn:hover { color: var(--accent-warm); }
.bookmark-btn.guardado { color: var(--accent-warm); }

/* Palabras clave */
.tarjeta.kw-match, .tarjeta-destacada.kw-match { border-left: 2px solid var(--accent-warm); }
.tarjeta[hidden], .tarjeta-destacada[hidden], .sintesis-card[hidden] { display: none !important; }

/* ═══════════════════════════════════════════════════════════════════════════
   Asombro
   ═══════════════════════════════════════════════════════════════════════════ */
#tab-asombro { padding: 1rem; }
.asombro-header { text-align: center; padding: 3rem 0 2rem; }
.asombro-header h2 { font-family: var(--font-serif); font-size: clamp(2rem,4vw,3rem); font-weight: 900; color: var(--txt-1); margin-bottom: .5rem; letter-spacing: -.04em; }
.asombro-header p { font-size: .82rem; color: var(--txt-3); max-width: 520px; margin: 0 auto; line-height: 1.7; }
.asombro-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(380px,1fr)); gap: 1.25rem; max-width: 1400px; margin: 0 auto; }
.asombro-card { background: rgba(255,255,255,0.033); border: 1px solid var(--border-sub); border-radius: var(--r); padding: 1.75rem; cursor: pointer; transition: transform 0.3s cubic-bezier(0.4,0,0.2,1), box-shadow 0.3s, background 0.2s; }
.asombro-card:hover { transform: translateY(-5px); background: rgba(123,47,255,0.06); border-color: rgba(123,47,255,0.2); box-shadow: 0 25px 70px rgba(0,0,0,0.6), 0 0 40px rgba(123,47,255,0.08); }
.asombro-score { font-size: 0.85rem; color: #a78bfa; margin-bottom: .4rem; letter-spacing: .12em; }
.asombro-cat { display: inline-block; font-size: .52rem; text-transform: uppercase; letter-spacing: .1em; color: #a78bfa; background: rgba(167,139,250,0.1); border: 1px solid rgba(167,139,250,0.2); border-radius: 4px; padding: .1rem .4rem; margin-bottom: .6rem; }
.asombro-titulo { font-family: var(--font-serif); font-size: 1rem; font-weight: 700; color: var(--txt-1); margin-bottom: .35rem; line-height: 1.3; }
.asombro-titulo a { color: inherit; text-decoration: none; }
.asombro-titulo a:hover { color: #a78bfa; }
.asombro-fuente { font-size: .63rem; color: var(--txt-3); margin-bottom: .6rem; }
.asombro-razon { font-size: .77rem; color: #a78bfa; font-style: italic; margin-bottom: .6rem; line-height: 1.5; }
.asombro-resumen { font-size: .77rem; color: var(--txt-2); line-height: 1.6; }
.asombro-empty { text-align: center; padding: 5rem 1rem; color: var(--txt-3); }
.asombro-empty-icon { font-size: 3rem; margin-bottom: 1rem; }
.tab-btn[data-tab="asombro"].active { border-left-color: #7c3aed !important; background: linear-gradient(90deg, rgba(124,58,237,0.12), transparent) !important; }

/* ═══════════════════════════════════════════════════════════════════════════
   Para Leer / misc
   ═══════════════════════════════════════════════════════════════════════════ */
.para-leer-header { margin-bottom: 1.5rem; padding-bottom: .75rem; border-bottom: 1px solid var(--border-sub); }
.para-leer-header h2 { font-family: var(--font-serif); font-size: 1.8rem; font-weight: 900; color: var(--txt-1); letter-spacing: -.03em; margin-bottom: .3rem; }
.para-leer-header p { font-size: .73rem; color: var(--txt-3); }
.para-leer-empty { text-align: center; padding: 4rem 0; color: var(--txt-3); font-size: .875rem; line-height: 1.7; }
.tab-count { font-size: .5rem; background: var(--accent); color: #fff; border-radius: 3px; padding: .08rem .36rem; margin-left: .3rem; vertical-align: middle; }

/* Ángulos */
.angulos-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: .75rem; border-top: 1px solid var(--border-sub); padding-top: .875rem; }
.angulo-col { display: flex; flex-direction: column; gap: .4rem; }
.angulo-label { font-size: .52rem; font-weight: 700; text-transform: uppercase; letter-spacing: .12em; color: var(--txt-3); margin-bottom: .1rem; }
.angulo-item { font-size: .73rem; }
.angulo-item a { color: var(--txt-2); text-decoration: none; line-height: 1.4; }
.angulo-item a:hover { color: var(--txt-1); }

/* Banner IA */
#ia-banner {
  display: none; align-items: center; gap: .75rem;
  background: rgba(67,97,238,0.06); border: 1px solid rgba(67,97,238,0.15);
  border-radius: 0; padding: .55rem 2.5rem; font-size: .77rem; color: var(--txt-2);
}
#ia-banner .ia-msg { flex: 1; }
#ia-banner .ia-regen { background: var(--accent); color: #fff; border: none; border-radius: 6px; padding: .3rem .875rem; font-size: .74rem; font-weight: 600; cursor: pointer; text-decoration: none; white-space: nowrap; transition: background .15s; }
#ia-banner .ia-regen:hover { background: #2d4fd6; }
#ia-banner .ia-regen:disabled { opacity: .5; cursor: default; }
#ia-banner .ia-close { background: none; border: none; color: var(--txt-3); cursor: pointer; font-size: 1rem; line-height: 1; padding: 0 .15rem; }

/* Dark toggle */
.dark-toggle { background: none; border: 1px solid var(--border-sub); color: var(--txt-3); border-radius: 6px; padding: .2rem .6rem; font-size: .62rem; cursor: pointer; transition: background .12s; font-family: inherit; }
.dark-toggle:hover { background: var(--surface-2); color: var(--txt-1); }

/* Actualidad Absoluta */
.actualidad-header { padding: 2rem 0 1.25rem; border-bottom: 1px solid var(--border-sub); margin-bottom: 2rem; }
.actualidad-header h2 { font-family: var(--font-serif); font-size: clamp(2rem,3.5vw,3rem); font-weight: 900; color: var(--txt-1); margin: 0 0 .35rem; letter-spacing: -0.04em; }
.actualidad-header > p { color: var(--txt-3); font-size: .82rem; margin: 0 0 1rem; }
.historial-filtros { display: flex; align-items: center; gap: .4rem; flex-wrap: wrap; }
.historial-filtro-label { font-size: .7rem; color: var(--txt-3); font-weight: 600; }
.historial-filtro-sep { color: var(--border); font-size: .85rem; margin: 0 .15rem; }
.historial-filter-btn { background: var(--surface-2); border: 1px solid var(--border-sub); color: var(--txt-3); border-radius: 4px; padding: .18rem .58rem; font-size: .68rem; font-weight: 600; cursor: pointer; transition: all .15s; white-space: nowrap; }
.historial-filter-btn.active, .historial-filter-btn:hover { background: var(--accent); border-color: var(--accent); color: #fff; }
.proceso-card, .proceso-card-hero { background: rgba(255,255,255,0.033); border: 1px solid var(--border-sub); border-left-width: 3px; border-radius: var(--r); overflow: hidden; display: flex; flex-direction: column; transition: background .15s; }
.proceso-card:hover, .proceso-card-hero:hover { background: rgba(255,255,255,0.05); }
.proceso-card[data-estado="escalada"], .proceso-card-hero[data-estado="escalada"] { border-left-color: #ef4444; }
.proceso-card[data-estado="estable"],  .proceso-card-hero[data-estado="estable"]  { border-left-color: var(--accent); }
.proceso-card[data-estado="resolucion"],.proceso-card-hero[data-estado="resolucion"]{ border-left-color: #4ade80; }

/* Watch panel */
#watch-panel { display: flex; flex-direction: column; gap: .75rem; margin-bottom: 2rem; }
.watch-alerta { background: rgba(245,158,11,0.06); border: 1px solid rgba(245,158,11,0.18); border-radius: var(--r); padding: .875rem 1rem; display: flex; align-items: flex-start; gap: .75rem; }
.watch-icono { font-size: 1rem; flex-shrink: 0; color: var(--accent-warm); }
.watch-alerta strong { font-size: .78rem; color: var(--txt-1); display: block; margin-bottom: .2rem; }
.watch-alerta p { font-size: .72rem; color: var(--txt-2); }
.watch-confianza { font-size: .62rem; font-weight: 700; color: var(--accent-warm); white-space: nowrap; }


/* Conexiones / Briefing */
.briefing-header { margin-bottom: 1.5rem; }
.briefing-header h3 { font-family: var(--font-serif); font-size: 1.4rem; font-weight: 900; color: var(--txt-1); letter-spacing: -.03em; }
.briefing-texto { font-size: .84rem; color: var(--txt-2); line-height: 1.85; }
.conexion-card { background: rgba(255,255,255,0.033); border: 1px solid var(--border-sub); border-radius: var(--r); padding: 1.5rem; margin-bottom: 1rem; }
.conexion-titulo { font-size: .78rem; font-weight: 700; color: var(--txt-1); margin-bottom: .4rem; }
.conexion-desc { font-size: .73rem; color: var(--txt-2); line-height: 1.65; }
.tension-badge { display: inline-block; font-size: .48rem; font-weight: 700; text-transform: uppercase; letter-spacing: .1em; padding: .1rem .4rem; border-radius: 4px; margin-right: .4rem; }
.tension-alta { background: rgba(239,68,68,0.12); color: #f87171; }
.tension-media { background: rgba(245,158,11,0.1); color: #fbbf24; }
.tension-baja { background: rgba(74,222,128,0.1); color: #4ade80; }
@keyframes pulso {
  0%, 100% { transform: scale(1); opacity: 1; }
  50%       { transform: scale(1.35); opacity: 0.6; }
}
.tension-label { font-size: 0.55rem; letter-spacing: 0.09em; text-transform: uppercase; font-weight: 700; }
"""
