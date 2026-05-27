"""
renderer — paquete modular del digest de noticias.

Punto de entrada público: renderizar_html() y guardar_y_abrir().

Para añadir una nueva pestaña edita renderer/tabs/__init__.py.
"""

import html as _html
import os
import webbrowser
from datetime import datetime

from analyzer import COLORES_SESGO
from config import ARCHIVO_SALIDA

from renderer.tabs import TABS
from renderer.tabs.todas import nav
from renderer import shell


# ── Utilidades internas ──────────────────────────────────────────────────────

def _calcular_verificados(grupos_sintesis: list[dict] | None) -> frozenset:
    """URLs confirmadas por ≥2 fuentes de sesgos opuestos → badge Multi-fuente."""
    if not grupos_sintesis:
        return frozenset()
    _izq = {"izquierda", "centro-izquierda"}
    _der = {"centro-derecha", "derecha"}
    candidatos: set[str] = set()
    for grupo in grupos_sintesis:
        arts = grupo.get("articulos", [])
        sesgos = {a.get("sesgo_fuente", "") for a in arts}
        if (sesgos & _izq) and (sesgos & _der):
            for a in arts:
                candidatos.add(a["enlace"])
    return frozenset(candidatos)


def _tension_html(noticias: dict[str, list[dict]]) -> str:
    """Tensiómetro del día basado en el sentimiento de los artículos."""
    sents = [
        a.get("sentimiento", "")
        for arts in noticias.values()
        for a in arts
        if a.get("sentimiento")
    ]
    if not sents:
        return ""
    n_alar = sum(1 for s in sents if s == "alarmista")
    pct    = int(n_alar / max(len(sents), 1) * 100)
    if pct >= 40:
        color, txt = "#dc2626", "Día tenso"
    elif pct >= 20:
        color, txt = "#f97316", "Día activo"
    else:
        color, txt = "#3d7a52", "Día tranquilo"
    return (
        f'<div class="tension-wrap">'
        f'<span class="tension-dot" style="background:{color}"></span>'
        f'<span class="tension-label" style="color:{color}">{txt}</span>'
        f'</div>'
    )


def _splash_headlines(noticias: dict[str, list[dict]]) -> str:
    todos = [a for arts in noticias.values() for a in arts]
    arts  = [a for a in todos if a.get("destacado")][:3]
    if len(arts) < 3:
        arts += [a for a in todos if not a.get("destacado")][:3 - len(arts)]
    if not arts:
        return '<div class="splash-hl">Cargando titulares del día...</div>'
    return "".join(
        f'<div class="splash-hl">{_html.escape(a["titulo"])}</div>'
        for a in arts[:3]
    )


# ── API pública ──────────────────────────────────────────────────────────────

def renderizar_html(
    noticias: dict[str, list[dict]],
    analisis: dict[str, str],
    alternativas: dict[str, list[dict]] | None = None,
    analisis_alt: dict[str, str] | None = None,
    grupos_sintesis: list[dict] | None = None,
    fuentes_fallidas: list[str] | None = None,
    procesos: list[dict] | None = None,
    conexiones: list[dict] | None = None,
    alertas_watch: list[dict] | None = None,
) -> str:
    ahora      = datetime.now().strftime("%d/%m/%Y — %H:%M")
    total      = sum(len(arts) for arts in noticias.values())
    total_alt  = sum(len(a) for a in (alternativas or {}).values())
    verificados = _calcular_verificados(grupos_sintesis)

    # Renderizar pestaña asombro por separado para obtener el conteo
    _tab_asombro = next((t for t in TABS if t.TAB_ID == 'asombro'), None)
    asombro_html, n_asombro = (_tab_asombro.render(
        noticias=noticias, alternativas=alternativas or {}
    ) if _tab_asombro else ("", 0))

    # Mapa de datos disponibles para cada pestaña
    datos = dict(
        noticias=noticias,
        analisis=analisis,
        alternativas=alternativas or {},
        analisis_alt=analisis_alt or {},
        grupos_sintesis=grupos_sintesis or [],
        fuentes_fallidas=fuentes_fallidas or [],
        procesos=procesos or [],
        conexiones=conexiones or [],
        verificados=verificados,
    )

    contenidos: dict[str, str] = {}
    for tab in TABS:
        try:
            resultado = tab.render(**datos)
            # asombro devuelve (html, n) — extraer solo el html
            contenidos[tab.TAB_ID] = resultado[0] if isinstance(resultado, tuple) else resultado
        except Exception as e:
            contenidos[tab.TAB_ID] = f'<p class="sin-articulos">Error al generar esta pestaña: {e}</p>'

    n_asombro  = n_asombro
    n_procesos = len(procesos) if procesos else 0
    n_sintesis = len(grupos_sintesis) if grupos_sintesis else 0

    return shell.construir(
        tabs=TABS,
        contenidos=contenidos,
        ahora=ahora,
        total=total,
        total_alt=total_alt,
        n_asombro=n_asombro,
        n_procesos=n_procesos,
        n_sintesis=n_sintesis,
        tension_html=_tension_html(noticias),
        splash_hls=_splash_headlines(noticias),
        alertas=alertas_watch or [],
        nav_html=nav(list(noticias.keys())),
        sesgo_colores=COLORES_SESGO,
    )


def guardar_y_abrir(html: str, abrir: bool = True) -> None:
    with open(ARCHIVO_SALIDA, "w", encoding="utf-8") as f:
        f.write(html)
    if abrir:
        webbrowser.open(f"file://{os.path.abspath(ARCHIVO_SALIDA)}")
