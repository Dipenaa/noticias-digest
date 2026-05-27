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
from styles import _CSS


# ── JS estático — cargado desde static/js/ ──────────────────────────────────

_JS_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'js')

# Orden de carga (las dependencias primero)
_JS_FILES = [
    'tabs.js',
    'search.js',
    'bookmarks.js',
    'drawer.js',
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
        if tid == 'asombro' and n_asombro:
            label += f'<span class="tab-count">{n_asombro}</span>'
        elif tid == 'actualidad' and n_procesos:
            label += f'<span class="tab-count">{n_procesos}</span>'
        elif tid == 'sintesis' and n_sintesis:
            label += f'<span style="font-size:.6rem;opacity:.7;margin-left:.3rem">{n_sintesis}</span>'
        elif tid == 'para-leer':
            label += '<span class="tab-count" id="bookmark-count" style="display:none"></span>'

        active = ' active' if tid == 'destacadas' else ''
        return f'<button class="tab-btn{active}" data-tab="{tid}" onclick="switchTab(\'{tid}\')">{label}</button>'

    btns = "\n  ".join(_btn(t) for t in tabs)
    return f"""<div class="tab-bar">
  {btns}
  <button class="dark-toggle" id="dark-toggle" onclick="toggleDark()">&#9790; Modo oscuro</button>
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
  <title>Digest de Noticias — {ahora}</title>
  <meta name="theme-color" content="{sesgo_colores.get('centro', '#3d7a52')}">
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
    <div>
      <div style="font-size:0.65rem;color:var(--txt-3);font-weight:600;letter-spacing:0.04em;margin-bottom:0.1rem" id="header-greeting"></div>
      <h1>Digest de Noticias</h1>
    </div>
  </div>
  <div class="meta">
    {ahora}<br>
    {total} principales · {total_alt} alternativas · Claude
    {tension_html}
  </div>
</header>

{alertas_blk}

<div id="ia-banner" style="display:none">
  <span class="ia-msg">&#9888; <strong><span id="ia-banner-count">0</span> art&#237;culos</strong> sin an&#225;lisis IA &mdash; resumen, sesgo y s&#237;ntesis pueden estar incompletos</span>
  <button class="ia-regen" id="ia-regen-btn" onclick="lanzarAnalisisIA()">Regenerar an&#225;lisis IA</button>
  <button class="ia-close" onclick="document.getElementById('ia-banner').style.display='none'" title="Cerrar">&#215;</button>
</div>

{tab_bar_blk}

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

{nav_html}

<main>
{tabs_html}
</main>

<footer>
  Sin publicidad · Sin algoritmos · Generado localmente ·
  Análisis por Claude (Anthropic)
</footer>

<!-- ── Splash de portada ────────────────────────────────────────────── -->
<div id="splash" onclick="dismissSplash()">
  <div class="splash-eyebrow">{ahora}</div>
  <div class="splash-logo">Digest</div>
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
{config_js}
</script>
<script>
{js_code}
</script>

</body>
</html>"""
