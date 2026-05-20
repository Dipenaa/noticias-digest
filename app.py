"""
app.py — Servidor Flask para desplegar el digest en Render (o cualquier PaaS).

Rutas:
  GET /            → sirve el digest HTML más reciente
  GET /regenerar   → lanza una regeneración en background y redirige a /
  GET /estado      → JSON con el estado actual (generando, último update, errores)

Flujo al arrancar:
  1. Genera el digest completo en un hilo de background
  2. Mientras tanto, / devuelve una página de "cargando"
  3. Cuando termina, / devuelve el HTML completo
  4. Render puede hacer cron de /regenerar para mantenerlo fresco

Variables de entorno requeridas:
  ANTHROPIC_API_KEY → tu clave de la API de Claude (configúrala en Render Dashboard)
  GEMINI_API_KEY    → tu clave de la API de Gemini (solo para discoverer.py; opcional)
"""

import os
import time
import threading
import traceback
from datetime import datetime
from flask import Flask, Response, redirect, jsonify

_INTERVALO_HORAS = 6   # regenerar el digest cada N horas

# Importamos solo los módulos que no usan sys.stdout.reconfigure
from fetcher import obtener_todas_las_noticias, obtener_noticias_alternativas
from analyzer import analizar_todas_las_noticias
from synthesizer import sintetizar_noticias
from renderer import renderizar_html

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Estado global (compartido entre hilos con un lock)
# ---------------------------------------------------------------------------

_lock             = threading.Lock()
_html_cache       = None          # HTML generado más reciente (str)
_generando        = False         # True mientras hay una generación en curso
_ultimo_update    = None          # datetime del último digest exitoso
_ultimo_error     = None          # texto del último error, si lo hubo
_sin_ia           = os.getenv("SIN_IA", "").lower() in ("1", "true", "yes")
_noticias_raw     = None          # último dict de noticias principales sin enriquecer
_alternativas_raw = None          # último dict de noticias alternativas sin enriquecer


# ---------------------------------------------------------------------------
# Lógica de generación (se ejecuta en un hilo separado)
# ---------------------------------------------------------------------------

def _generar():
    """Descarga feeds, analiza con Claude (si procede) y actualiza _html_cache."""
    global _generando, _html_cache, _ultimo_update, _ultimo_error
    global _noticias_raw, _alternativas_raw

    with _lock:
        if _generando:
            return   # ya hay una generación en marcha
        _generando = True

    try:
        print(f"[{datetime.now():%H:%M:%S}] Iniciando generación del digest...")

        # 1. Descarga
        noticias     = obtener_todas_las_noticias()
        alternativas = obtener_noticias_alternativas()

        # Guardamos una copia de las noticias crudas para poder re-analizar sin re-descargar
        import copy
        with _lock:
            _noticias_raw     = copy.deepcopy(noticias)
            _alternativas_raw = copy.deepcopy(alternativas)

        # 2. Análisis IA (opcional — desactivado si SIN_IA=1 o no hay API key)
        analisis:      dict = {}
        analisis_alt:  dict = {}
        grupos_sintesis: list = []

        from config import ANTHROPIC_API_KEY
        ia_disponible = (not _sin_ia) and ANTHROPIC_API_KEY not in ("TU_API_KEY_AQUÍ", "", None)

        if ia_disponible:
            print(f"[{datetime.now():%H:%M:%S}] Analizando con Claude...")
            noticias,     analisis     = analizar_todas_las_noticias(noticias)
            alternativas, analisis_alt = analizar_todas_las_noticias(alternativas)
            grupos_sintesis            = sintetizar_noticias(noticias, alternativas)
        else:
            print(f"[{datetime.now():%H:%M:%S}] Modo sin IA (SIN_IA=1 o ANTHROPIC_API_KEY no configurada)")

        # 3. Renderiza
        html = renderizar_html(
            noticias, analisis,
            alternativas, analisis_alt,
            grupos_sintesis,
        )

        with _lock:
            _html_cache    = html
            _ultimo_update = datetime.now()
            _ultimo_error  = None

        print(f"[{datetime.now():%H:%M:%S}] Digest generado correctamente.")

    except Exception:
        err = traceback.format_exc()
        print(f"[{datetime.now():%H:%M:%S}] ERROR durante la generación:\n{err}")
        with _lock:
            _ultimo_error = err

    finally:
        with _lock:
            _generando = False


def _lanzar_generacion():
    """Arranca _generar() en un hilo daemon si no hay una en curso."""
    t = threading.Thread(target=_generar, daemon=True)
    t.start()


def _solo_analizar_ia():
    """Corre solo el análisis IA sobre las noticias ya descargadas (sin re-fetch de feeds)."""
    global _generando, _html_cache, _ultimo_update, _ultimo_error
    global _noticias_raw, _alternativas_raw

    with _lock:
        if _generando:
            return
        if _noticias_raw is None:
            # No hay caché de noticias → lanzar generación completa
            _lanzar_generacion()
            return
        _generando = True

    try:
        import copy
        with _lock:
            noticias     = copy.deepcopy(_noticias_raw)
            alternativas = copy.deepcopy(_alternativas_raw)

        print(f"[{datetime.now():%H:%M:%S}] Lanzando análisis IA sobre noticias en caché...")

        from config import ANTHROPIC_API_KEY
        ia_disponible = (not _sin_ia) and ANTHROPIC_API_KEY not in ("TU_API_KEY_AQUÍ", "", None)

        analisis:      dict = {}
        analisis_alt:  dict = {}
        grupos_sintesis: list = []

        if ia_disponible:
            noticias,     analisis     = analizar_todas_las_noticias(noticias)
            alternativas, analisis_alt = analizar_todas_las_noticias(alternativas)
            grupos_sintesis            = sintetizar_noticias(noticias, alternativas)
        else:
            print(f"[{datetime.now():%H:%M:%S}] IA no disponible — SIN_IA o ANTHROPIC_API_KEY ausente")

        html = renderizar_html(
            noticias, analisis,
            alternativas, analisis_alt,
            grupos_sintesis,
        )

        with _lock:
            _html_cache    = html
            _ultimo_update = datetime.now()
            _ultimo_error  = None

        print(f"[{datetime.now():%H:%M:%S}] Análisis IA completado.")

    except Exception:
        err = traceback.format_exc()
        print(f"[{datetime.now():%H:%M:%S}] ERROR en análisis IA:\n{err}")
        with _lock:
            _ultimo_error = err
    finally:
        with _lock:
            _generando = False


def _scheduler():
    """Regenera el digest cada _INTERVALO_HORAS mientras el servidor está activo."""
    while True:
        time.sleep(_INTERVALO_HORAS * 3600)
        print(f"[{datetime.now():%H:%M:%S}] Regeneración automática ({_INTERVALO_HORAS}h)")
        _lanzar_generacion()


# ---------------------------------------------------------------------------
# Página de carga (se muestra mientras el digest no está listo)
# ---------------------------------------------------------------------------

_HTML_CARGANDO = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Generando digest…</title>
  <style>
    body { font-family: system-ui, sans-serif; background: #09090b; color: #a1a1aa;
           display: flex; flex-direction: column; align-items: center;
           justify-content: center; height: 100vh; margin: 0; gap: 1.5rem; }
    h1   { color: #fafafa; font-size: 1.2rem; font-weight: 700; }
    .dot { display: inline-block; animation: blink 1.2s infinite; }
    .dot:nth-child(2) { animation-delay: .2s; }
    .dot:nth-child(3) { animation-delay: .4s; }
    @keyframes blink { 0%,80%,100%{opacity:0} 40%{opacity:1} }
    p    { font-size: .85rem; max-width: 340px; text-align: center; line-height:1.6; }
  </style>
</head>
<body>
  <h1>📰 Generando digest<span class="dot">.</span><span class="dot">.</span><span class="dot">.</span></h1>
  <p>Descargando feeds RSS y analizando con Gemini.<br>
     Esta página se recargará automáticamente cada 8 segundos.</p>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Rutas Flask
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    with _lock:
        html   = _html_cache
        error  = _ultimo_error
        update = _ultimo_update

    # Si el caché tiene más de _INTERVALO_HORAS (p.ej. el servidor acaba de
    # despertar tras estar dormido), lanzar regeneración en background.
    # El visitante recibe el HTML viejo de inmediato; el siguiente ya verá el nuevo.
    if html and update:
        edad = (datetime.now() - update).total_seconds()
        if edad > _INTERVALO_HORAS * 3600:
            _lanzar_generacion()

    if html:
        return Response(html, mimetype="text/html; charset=utf-8")

    if error:
        return Response(
            f"<pre style='color:red;background:#111;padding:2rem'>{error}</pre>",
            status=500, mimetype="text/html",
        )

    return Response(_HTML_CARGANDO, status=503, mimetype="text/html")


@app.route("/regenerar")
def regenerar():
    """Lanza una nueva generación en background y redirige al digest."""
    _lanzar_generacion()
    return redirect("/")


@app.route("/analizar", methods=["GET", "POST"])
def analizar():
    """Lanza solo el análisis IA sobre las noticias ya cacheadas (sin re-fetch de feeds).
    Devuelve JSON {ok: true} de inmediato; el cliente sondea /estado para saber cuándo acabó.
    """
    t = threading.Thread(target=_solo_analizar_ia, daemon=True)
    t.start()
    return jsonify({"ok": True, "mensaje": "Análisis IA iniciado en background"})


@app.route("/estado")
def estado():
    """Devuelve el estado actual en JSON (útil para monitorización)."""
    with _lock:
        return jsonify({
            "generando":     _generando,
            "tiene_cache":   _html_cache is not None,
            "ultimo_update": _ultimo_update.isoformat() if _ultimo_update else None,
            "ultimo_error":  _ultimo_error is not None,
        })


# ---------------------------------------------------------------------------
# Arranque
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Genera el digest al arrancar (en background para no bloquear el bind del puerto)
    _lanzar_generacion()

    # Regenera automáticamente cada _INTERVALO_HORAS
    threading.Thread(target=_scheduler, daemon=True).start()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
