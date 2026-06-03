"""
pipeline.py — Pipeline de generación del digest (descarga, análisis IA, renderizado).

Estado global compartido entre hilos. app.py importa de aquí para mantenerse
como capa puramente Flask (~150 líneas).
"""

import copy
import os
import threading
import traceback
from datetime import datetime

from fetcher import obtener_todas_las_noticias, obtener_noticias_alternativas, get_fuentes_fallidas
from analyzer import analizar_todas_las_noticias
from synthesizer import sintetizar_noticias
from renderer import renderizar_html

_INTERVALO_HORAS = 18

_lock             = threading.Lock()
_html_cache: str | None       = None
_generando:  bool             = False
_ultimo_update: datetime | None = None
_ultimo_error:  str | None    = None
_sin_ia           = os.getenv("SIN_IA", "").lower() in ("1", "true", "yes")
_noticias_raw:      dict | None = None
_alternativas_raw:  dict | None = None
_render_data:       dict | None = None
_fuentes_fallidas_cache: list   = []


# ---------------------------------------------------------------------------
# Accesores de estado (evitan que app.py acceda a globals directamente)
# ---------------------------------------------------------------------------

def get_html() -> tuple[str | None, str | None, datetime | None]:
    with _lock:
        return _html_cache, _ultimo_error, _ultimo_update


def get_render_data() -> dict | None:
    with _lock:
        return _render_data


def is_generando() -> bool:
    with _lock:
        return _generando


def get_estado() -> dict:
    from config import ANTHROPIC_API_KEY, GEMINI_API_KEY
    from article_cache import shared as _cache
    from claude_client import resumen_coste
    stats = _cache.stats()
    with _lock:
        return {
            "generando":               _generando,
            "tiene_cache":             _html_cache is not None,
            "ultimo_update":           _ultimo_update.isoformat() if _ultimo_update else None,
            "ultimo_error":            _ultimo_error,
            "ia_ok":                   (GEMINI_API_KEY not in ("", None)) or (ANTHROPIC_API_KEY not in ("", None)),
            "cache_articulos":         stats["articulos_cacheados"],
            "cache_sintesis":          stats["sintesis_cacheadas"],
            "coste_ultima_generacion": resumen_coste(),
        }


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _ia_disponible() -> bool:
    from config import ANTHROPIC_API_KEY, GEMINI_API_KEY
    gemini_ok = GEMINI_API_KEY not in ("TU_API_KEY_AQUÍ", "", None)
    anthropic_ok = ANTHROPIC_API_KEY not in ("TU_API_KEY_AQUÍ", "", None)
    return (not _sin_ia) and (gemini_ok or anthropic_ok)


def _pipeline_ia(noticias: dict, alternativas: dict):
    """Análisis IA, síntesis, macro_tracker, noise_filter, watch. Devuelve datos enriquecidos."""
    ia = _ia_disponible()
    analisis:       dict = {}
    analisis_alt:   dict = {}
    grupos_sintesis: list = []

    if ia:
        noticias,     analisis     = analizar_todas_las_noticias(noticias)
        alternativas, analisis_alt = analizar_todas_las_noticias(alternativas)
        try:
            grupos_sintesis = sintetizar_noticias(noticias, alternativas)
            print(f"[{datetime.now():%H:%M:%S}] Síntesis: {len(grupos_sintesis)} historia(s).")
            # Segundo pase (B-lite): perspectivas globales por historia vía Google News (sin coste IA)
            try:
                from fuentes_dinamicas import enriquecer_grupos
                enriquecer_grupos(grupos_sintesis)
                n_ext = sum(len(g.get("perspectivas_extra", [])) for g in grupos_sintesis)
                print(f"[{datetime.now():%H:%M:%S}] Perspectivas extra: {n_ext} ángulo(s) global(es).")
            except Exception as e:
                print(f"[{datetime.now():%H:%M:%S}] Perspectivas extra fallaron (no crítico): {e}")
        except Exception as e:
            print(f"[{datetime.now():%H:%M:%S}] Síntesis falló (no crítico): {e}")

        from article_cache import shared as _cache
        for cat, arts in noticias.items():
            _cache.update_pool(cat, arts)
    else:
        print(f"[{datetime.now():%H:%M:%S}] Modo sin IA (SIN_IA=1 o API_KEY ausente)")

    from macro_tracker import obtener_macro_data as _macro
    from noise_filter import detectar_ruido as _ruido
    from watch import verificar_condiciones as _watch

    try:
        macro = _macro(noticias) if ia else {"procesos": [], "conexiones": []}
    except Exception as e:
        err_str = traceback.format_exc()
        print(f"[{datetime.now():%H:%M:%S}] Macro falló (no crítico): {e}\n{err_str}")
        global _ultimo_error
        with _lock:
            _ultimo_error = f"[macro] {str(e)}"
        macro = {"procesos": [], "conexiones": []}
    if ia:
        noticias     = _ruido(noticias)
        alternativas = _ruido(alternativas)
    alertas_watch = _watch(noticias, alternativas) if ia else []

    return noticias, analisis, alternativas, analisis_alt, grupos_sintesis, macro, alertas_watch


# ---------------------------------------------------------------------------
# Función unificada de generación
# ---------------------------------------------------------------------------

def generar(refetch: bool = True) -> None:
    """
    Pipeline completo. Si refetch=True descarga feeds; si False reutiliza los
    artículos cacheados en memoria (análisis IA sobre datos ya descargados).
    """
    global _generando, _html_cache, _ultimo_update, _ultimo_error
    global _noticias_raw, _alternativas_raw, _render_data, _fuentes_fallidas_cache

    with _lock:
        if _generando:
            return
        if not refetch and _noticias_raw is None:
            refetch = True  # sin caché → forzar descarga
        _generando = True

    try:
        from claude_client import reset_coste, resumen_coste
        reset_coste()
        label = "generación completa" if refetch else "análisis IA sobre caché"
        print(f"[{datetime.now():%H:%M:%S}] Iniciando {label}...")

        if refetch:
            noticias      = obtener_todas_las_noticias()
            _f_principales = get_fuentes_fallidas()
            alternativas  = obtener_noticias_alternativas()
            _fuentes_fallidas_cache = _f_principales + get_fuentes_fallidas()

            # Fusionar pool de 3 días con artículos frescos
            from article_cache import shared as _cache
            for cat in list(noticias.keys()):
                pool = _cache.get_pool(cat)
                if pool:
                    urls_hoy = {a["enlace"] for a in noticias[cat]}
                    extras = [a for a in pool if a.get("enlace") not in urls_hoy]
                    noticias[cat] = noticias[cat] + extras

            with _lock:
                _noticias_raw     = copy.deepcopy(noticias)
                _alternativas_raw = copy.deepcopy(alternativas)
        else:
            with _lock:
                noticias     = copy.deepcopy(_noticias_raw)
                alternativas = copy.deepcopy(_alternativas_raw)

        (noticias, analisis, alternativas, analisis_alt,
         grupos_sintesis, macro, alertas_watch) = _pipeline_ia(noticias, alternativas)

        with _lock:
            _render_data = {
                "noticias":      copy.deepcopy(noticias),
                "analisis":      analisis,
                "alternativas":  copy.deepcopy(alternativas),
                "analisis_alt":  analisis_alt,
                "procesos":      macro["procesos"],
                "conexiones":    macro["conexiones"],
                "alertas_watch": alertas_watch,
            }

        html = renderizar_html(
            noticias, analisis,
            alternativas, analisis_alt,
            grupos_sintesis,
            fuentes_fallidas=_fuentes_fallidas_cache,
            procesos=macro["procesos"],
            conexiones=macro["conexiones"],
            alertas_watch=alertas_watch,
        )

        with _lock:
            _html_cache    = html
            _ultimo_update = datetime.now()
            _ultimo_error  = None

        print(f"[{datetime.now():%H:%M:%S}] Digest generado. Coste IA: {resumen_coste()}")

    except Exception:
        err = traceback.format_exc()
        print(f"[{datetime.now():%H:%M:%S}] ERROR durante la generación:\n{err}")
        with _lock:
            _ultimo_error = err
    finally:
        with _lock:
            _generando = False


def sintetizar() -> None:
    """Re-genera la síntesis con los datos ya analizados y actualiza el HTML."""
    global _html_cache, _ultimo_update, _ultimo_error

    with _lock:
        data = _render_data

    if not data:
        print(f"[{datetime.now():%H:%M:%S}] Síntesis solicitada pero no hay datos analizados")
        return

    try:
        print(f"[{datetime.now():%H:%M:%S}] Generando síntesis cruzada...")
        grupos = sintetizar_noticias(data["noticias"], data["alternativas"])

        html = renderizar_html(
            data["noticias"], data["analisis"],
            data["alternativas"], data["analisis_alt"],
            grupos,
            fuentes_fallidas=_fuentes_fallidas_cache,
            procesos=data.get("procesos", []),
            conexiones=data.get("conexiones", []),
            alertas_watch=data.get("alertas_watch", []),
        )

        with _lock:
            _html_cache    = html
            _ultimo_update = datetime.now()
            _ultimo_error  = None

        print(f"[{datetime.now():%H:%M:%S}] Síntesis completada — {len(grupos)} historia(s).")

    except Exception:
        err = traceback.format_exc()
        print(f"[{datetime.now():%H:%M:%S}] ERROR en síntesis:\n{err}")
        with _lock:
            _ultimo_error = err


# ---------------------------------------------------------------------------
# Lanzadores (inician funciones en hilos daemon)
# ---------------------------------------------------------------------------

def lanzar_generacion() -> None:
    threading.Thread(target=generar, kwargs={"refetch": True}, daemon=True).start()


def lanzar_analizar_ia() -> None:
    threading.Thread(target=generar, kwargs={"refetch": False}, daemon=True).start()


def lanzar_sintetizar() -> None:
    threading.Thread(target=sintetizar, daemon=True).start()


def scheduler() -> None:
    """Regenera el digest automáticamente cada _INTERVALO_HORAS."""
    import time
    while True:
        time.sleep(_INTERVALO_HORAS * 3600)
        print(f"[{datetime.now():%H:%M:%S}] Regeneración automática ({_INTERVALO_HORAS}h)")
        lanzar_generacion()
