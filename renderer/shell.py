"""
HTML wrapper del digest.

Genera el documento completo inlineando CSS y JS, y ensamblando los
contenidos de cada pestaña del registro TABS.
"""

import html as _html
import json
import os
from datetime import datetime

from analyzer import COLORES_SESGO


# ── JS estático — cargado desde static/js/ ──────────────────────────────────

_JS_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'js')

# Orden de carga (las dependencias primero)
_JS_FILES = [
    'tabs.js',
    'search.js',
    'bookmarks.js',
    'audio.js',
    'drawer.js',
    'charts.js',
    'stats.js',
    'sort.js',
    'actualidad.js',
    'init.js',
]


def _cargar_js() -> str:
    partes = []
    for nombre in _JS_FILES:
        ruta = os.path.join(_JS_DIR, nombre)
        try:
            with open(ruta, encoding='utf-8') as f:
                partes.append(f'/* ── {nombre} ── */\n' + f.read())
        except FileNotFoundError:
            partes.append(f'/* MISSING: {nombre} */')
    return '\n\n'.join(partes)


# ── Alertas de vigilancia ────────────────────────────────────────────────────

def alertas_html(alertas: list[dict]) -> str:
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


# ── Tab bar sidebar ──────────────────────────────────────────────────────────

def _tab_bar(tabs: list, n_asombro: int, n_procesos: int, n_sintesis: int) -> str:
    def _btn(tab) -> str:
        label = tab.TAB_LABEL
        tid   = tab.TAB_ID

        # Badges de conteo por pestaña
        badge_html = ""
        if tid == 'asombro' and n_asombro:
            badge_html = f'<span class="tab-count">{n_asombro}</span>'
        elif tid == 'actualidad' and n_procesos:
            badge_html = f'<span class="tab-count">{n_procesos}</span>'
        elif tid == 'sintesis' and n_sintesis:
            badge_html = f'<span style="font-size:.6rem;opacity:.7;margin-left:.3rem">{n_sintesis}</span>'
        elif tid == 'para-leer':
            badge_html = '<span class="tab-count" id="bookmark-count" style="display:none"></span>'

        active = ' active' if tid == 'destacadas' else ''
        return f'<button class="tab-btn{active}" data-tab="{tid}" onclick="switchTab(\'{tid}\')"><span data-translate="tab_{tid}">{label}</span>{badge_html}</button>'

    btns = "\n  ".join(_btn(t) for t in tabs)
    return f"""<div class="tab-bar">
  {btns}
  <button class="dark-toggle" id="dark-toggle" onclick="toggleDark()" data-translate="dark_mode">🌙 Modo oscuro</button>
  <div class="lang-toggle-group">
    <span class="lang-label" data-translate="lang_label">Idioma:</span>
    <button class="lang-btn active" data-lang="es" onclick="changeLanguage('es')">ES</button>
    <button class="lang-btn" data-lang="en" onclick="changeLanguage('en')">EN</button>
  </div>
</div>"""


# ── Documento HTML completo ──────────────────────────────────────────────────

def construir(
    tabs: list,
    contenidos: dict[str, str],
    ahora: str,
    total: int,
    total_alt: int,
    n_asombro: int,
    n_procesos: int,
    n_sintesis: int,
    tension_html: str,
    splash_hls: str,
    alertas: list[dict],
    nav_html: str,
    sesgo_colores: dict[str, str],
) -> str:
    """Ensambla el HTML final."""
    alertas_blk = alertas_html(alertas)
    tab_bar_blk = _tab_bar(tabs, n_asombro, n_procesos, n_sintesis)

    # Bloques de contenido de pestañas
    tabs_html = "\n\n".join(
        f'  <div id="tab-{tab.TAB_ID}" class="tab-content">\n    {contenidos.get(tab.TAB_ID, "")}\n  </div>'
        for tab in tabs
    )

    # window.DIGEST_CONFIG — datos Python expuestos a todos los JS
    config_js = (
        "window.DIGEST_CONFIG = {\n"
        "  sesgoColores: " + json.dumps(sesgo_colores) + "\n"
        "};"
    )

    js_code = _cargar_js()

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>EnPapel — {ahora}</title>
  <meta name="theme-color" content="{sesgo_colores.get('centro', '#3d7a52')}">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-title" content="EnPapel">
  <link rel="manifest" href="/manifest.json">
  <link rel="icon" href="/icon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,500&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="static/css/reset.css">
  <link rel="stylesheet" href="static/css/layout.css">
  <link rel="stylesheet" href="static/css/components.css">
  <link rel="stylesheet" href="static/css/animations.css">
</head>
<body class="light">

<header>
  <div class="header-logo">
    <h1>EnPapel</h1>
  </div>
  <div class="meta">
    <span class="meta-fecha">{ahora}</span>
    <span class="meta-count">
      <span id="meta-total">{total}</span> <span data-translate="meta_news">noticias</span> · 
      <span id="meta-alts">{total_alt}</span> <span data-translate="meta_alts">alternativas</span>
    </span>
    {tension_html}
  </div>
</header>

{alertas_blk}


{tab_bar_blk}

<div class="search-bar">
  <input class="search-input" id="buscador" type="search"
         placeholder="Buscar noticias..." autocomplete="off"
         oninput="clearTimeout(_buscarTimer);_buscarTimer=setTimeout(function(){{buscar(document.getElementById('buscador').value)}},200)">
  <span class="search-count" id="search-count"></span>
</div>

<div class="filter-bar" id="filter-bar">
  <div class="filter-pills">
    <button class="filter-pill timeline-btn active" data-dias="todos" onclick="filtrarDias(null,this)">Todos</button>
    <button class="filter-pill timeline-btn" data-dias="0" onclick="filtrarDias(0,this)">Hoy</button>
    <button class="filter-pill timeline-btn" data-dias="1" onclick="filtrarDias(1,this)">Ayer</button>
    <button class="filter-pill timeline-btn" data-dias="2" onclick="filtrarDias(2,this)">3 días</button>
    <button class="filter-pill timeline-btn" data-dias="4" onclick="filtrarDias(4,this)">5 días</button>
  </div>
  <div class="filter-sep"></div>
  <select class="filter-select" id="filter-sesgo" onchange="filtrarSesgoSelect(this.value)">
    <option value="">Sesgo: todos</option>
    <option value="izquierda">Izquierda</option>
    <option value="centro-izquierda">Centro-izq</option>
    <option value="centro">Centro</option>
    <option value="centro-derecha">Centro-der</option>
    <option value="derecha">Derecha</option>
  </select>
  <select class="filter-select" id="filter-orden" onchange="sortCards(this.value,null)">
    <option value="defecto">Orden: defecto</option>
    <option value="fecha-desc">Más recientes</option>
    <option value="fecha-asc">Más antiguos</option>
    <option value="novedad">Por novedad</option>
    <option value="sesgo-izq">Sesgo → izq</option>
    <option value="sesgo-der">Sesgo → der</option>
  </select>
</div>

{nav_html}

<main>
{tabs_html}
</main>

<footer data-translate="footer_text">
  Sin publicidad · Sin algoritmos · Generado localmente ·
  Análisis por Claude (Anthropic)
</footer>

<!-- ── Splash de portada ────────────────────────────────────────────── -->
<div id="splash" onclick="dismissSplash()">
  <div class="splash-eyebrow">{ahora}</div>
  <div class="splash-logo">EnPapel</div>
  <div class="splash-divider"></div>
  <div class="splash-headlines">{splash_hls}</div>
  <div class="splash-hint">toca para entrar</div>
</div>

<!-- ── Vista inmersiva ──────────────────────────────────────────────── -->
<div class="drawer-overlay" id="drawer-overlay" onclick="cerrarDrawer()"></div>
<div class="drawer" id="drawer" role="dialog" aria-modal="true">
  <div class="drawer-header">
    <div class="drawer-header-meta">
      <span class="drawer-categoria" id="d-categoria"></span>
      <div class="drawer-fuente-row">
        <span class="fuente-nombre" id="d-fuente"></span>
        <span class="fecha" id="d-fecha"></span>
        <span class="drawer-reading">&#9201; <span id="d-reading"></span> <span data-translate="drawer_reading">min</span></span>
      </div>
      <div class="drawer-badges" style="margin-top:.4rem">
        <span class="badge-etiqueta" data-translate="drawer_source">Fuente:</span>
        <span class="badge" id="d-sesgo-f"></span>
        <span class="badge-etiqueta" style="margin-left:.25rem" data-translate="drawer_ia">IA:</span>
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

    <!-- Ficha de Análisis Editorial IA -->
    <div class="drawer-analisis-ia" id="d-analisis-ia" style="display:none">
      <div class="drawer-analisis-grid">
        <div class="drawer-analisis-seccion">
          <div class="drawer-analisis-header">
            <span class="drawer-analisis-titulo" data-translate="ia_title_tono">Tono Emocional</span>
            <span class="drawer-analisis-valor" id="d-val-sentimiento"></span>
          </div>
          <p class="drawer-analisis-desc" id="d-desc-sentimiento"></p>
        </div>

        <div class="drawer-analisis-seccion">
          <div class="drawer-analisis-header">
            <span class="drawer-analisis-titulo" data-translate="ia_title_novedad">Índice de Novedad</span>
            <span class="drawer-analisis-valor" id="d-val-novedad"></span>
          </div>
          <p class="drawer-analisis-desc" id="d-desc-novedad"></p>
        </div>
      </div>
    </div>

    <!-- Contrapeso Editorial (Perspectiva Inversa) -->
    <div class="drawer-contrapeso" id="d-contrapeso" style="display:none">
      <div class="contrapeso-header" data-translate="contrapeso_title">Contrapeso Editorial</div>
      <p class="contrapeso-desc" data-translate="contrapeso_desc">Lee una perspectiva diferente sobre esta misma historia en medios del espectro opuesto:</p>
      <a class="contrapeso-link" id="d-contrapeso-link" href="#" target="_blank" rel="noopener noreferrer">-</a>
    </div>
  </div>
  <div class="drawer-footer" style="flex-wrap:wrap">
    <a class="drawer-btn drawer-btn-primary" id="d-btn-leer" href="#"
       target="_blank" rel="noopener noreferrer" data-translate="drawer_btn_read">
      Leer artículo ↗
    </a>
    <a class="drawer-btn drawer-btn-translate" id="d-btn-traducir" href="#"
       target="_blank" rel="noopener noreferrer" data-translate="drawer_btn_translate">
      🌐 Traducir
    </a>
    <button class="drawer-btn drawer-btn-voice" id="d-btn-voz"
            onclick="toggleVozDrawer(event)" data-translate="drawer_btn_voice">
      🔊 Escuchar
    </button>
    <button class="drawer-btn drawer-btn-secondary" id="d-btn-compartir"
            onclick="compartirArticulo()">
      Copiar enlace
    </button>
  </div>
</div>


<script>
{config_js}
</script>
<script>
{js_code}
</script>

</body>
</html>"""
