"""
app.py — Servidor Flask para el digest de noticias en Render.

Rutas:
  GET /            → digest HTML más reciente (o página de carga)
  GET /regenerar   → lanza generación completa en background
  GET /analizar    → lanza solo análisis IA sobre artículos ya descargados
  GET /sintetizar  → lanza síntesis cruzada con datos ya analizados
  GET /briefing    → genera memo de inteligencia (JSON)
  GET /estado      → estado actual en JSON (monitorización)
  GET /ping        → keep-alive
  GET /manifest.json, /icon.svg, /sw.js → PWA assets

Variables de entorno:
  ANTHROPIC_API_KEY — clave Claude (requerida para IA)
  DIGEST_PASSWORD   — contraseña de acceso básico (por defecto: "dipe")
  SIN_IA=1          — desactiva análisis IA
"""

import os
import hmac
import threading
from datetime import datetime

from flask import Flask, Response, redirect, jsonify, request

import pipeline

_PASSWORD = os.getenv("DIGEST_PASSWORD", "dipe")

app = Flask(__name__)

_RUTAS_PUBLICAS = {"/sw.js", "/manifest.json", "/icon.svg", "/estado", "/ping"}


@app.before_request
def _auth():
    if request.path in _RUTAS_PUBLICAS:
        return
    auth = request.authorization
    if not auth or not hmac.compare_digest(auth.password, _PASSWORD):
        return Response(
            "Acceso restringido",
            401,
            {"WWW-Authenticate": 'Basic realm="Noticias Digest"'},
        )


@app.after_request
def _security_headers(r):
    r.headers["X-Content-Type-Options"] = "nosniff"
    r.headers["X-Frame-Options"] = "SAMEORIGIN"
    r.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return r


# ---------------------------------------------------------------------------
# HTML de espera (mientras el digest no está listo)
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
  <h1>\U0001f4f0 Generando digest<span class="dot">.</span><span class="dot">.</span><span class="dot">.</span></h1>
  <p>Descargando feeds RSS y analizando con Claude.<br>
     Esta página se recargará automáticamente cada 8 segundos.</p>
</body>
</html>"""


def _strip_splash(html: str) -> str:
    """Elimina el div#splash del HTML cacheado contando divs anidados correctamente."""
    start = html.find('<div id="splash"')
    if start == -1:
        return html
    pos = html.find(">", start) + 1
    depth = 1
    while depth > 0 and pos < len(html):
        next_open  = html.find("<div", pos)
        next_close = html.find("</div>", pos)
        if next_close == -1:
            break
        if next_open != -1 and next_open < next_close:
            depth += 1
            pos = next_open + 4
        else:
            depth -= 1
            pos = next_close + 6
    return html[:start] + html[pos:]


# ---------------------------------------------------------------------------
# Rutas Flask
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    html, error, update = pipeline.get_html()

    if html and 'id="splash"' in html:
        html = _strip_splash(html)

    if html and update:
        edad = (datetime.now() - update).total_seconds()
        if edad > pipeline._INTERVALO_HORAS * 3600:
            pipeline.lanzar_generacion()

    if html:
        return Response(html, mimetype="text/html; charset=utf-8")

    if error:
        print(f"[ERROR] {error}")
        return Response(
            "<p style='font-family:sans-serif;padding:2rem;color:#c00'>"
            "Error al generar el digest. Revisa los logs del servidor.</p>",
            status=500, mimetype="text/html",
        )

    return Response(_HTML_CARGANDO, status=503, mimetype="text/html")


@app.route("/regenerar")
def regenerar():
    pipeline.lanzar_generacion()
    return redirect("/")


@app.route("/analizar", methods=["GET", "POST"])
def analizar():
    pipeline.lanzar_analizar_ia()
    return jsonify({"ok": True, "mensaje": "Análisis IA iniciado en background"})


@app.route("/sintetizar", methods=["GET", "POST"])
def sintetizar():
    pipeline.lanzar_sintetizar()
    return jsonify({"ok": True, "mensaje": "Síntesis iniciada en background"})


@app.route("/briefing", methods=["GET", "POST"])
def briefing():
    from briefing_generator import generar_briefing as _generar_briefing
    data = pipeline.get_render_data()
    if not data:
        return jsonify({"ok": False, "texto": "Sin datos disponibles. Regenera el digest primero."})
    texto = _generar_briefing(
        data.get("procesos", []),
        data.get("noticias", {}),
        data.get("alternativas", {}),
    )
    return jsonify({"ok": True, "texto": texto})


@app.route("/manifest.json")
def manifest():
    return jsonify({
        "name":             "Noticias Digest",
        "short_name":       "Noticias",
        "description":      "Digest de noticias con análisis de sesgo por IA",
        "start_url":        "/",
        "display":          "standalone",
        "background_color": "#060e08",
        "theme_color":      "#22c55e",
        "icons": [
            {"src": "/icon.svg", "sizes": "any", "type": "image/svg+xml"},
        ],
    })


@app.route("/icon.svg")
def icon_svg():
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 192 192">'
        '<rect width="192" height="192" rx="28" fill="#b5451b"/>'
        '<text x="96" y="138" font-size="108" text-anchor="middle">\U0001f4f0</text>'
        '</svg>'
    )
    return Response(svg, mimetype="image/svg+xml")


@app.route("/sw.js")
def service_worker():
    js = """
const CACHE = 'digest-v3';
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.add('/')));
  self.skipWaiting();
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys =>
    Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
  ));
  self.clients.claim();
});
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    fetch(e.request)
      .then(r => { caches.open(CACHE).then(c => c.put(e.request, r.clone())); return r; })
      .catch(() => caches.match(e.request))
  );
});
"""
    return Response(js, mimetype="application/javascript")


@app.route("/ping")
def ping():
    return Response("ok", mimetype="text/plain")


@app.route("/estado")
def estado():
    return jsonify(pipeline.get_estado())


# ---------------------------------------------------------------------------
# Arranque
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from config import ANTHROPIC_API_KEY as _key
    if _key in ("", None):
        print(
            f"[{datetime.now():%H:%M:%S}] ⚠  ANTHROPIC_API_KEY no configurada — "
            "el análisis IA estará desactivado. Usa SIN_IA=1 para silenciar este aviso."
        )

    pipeline.lanzar_generacion()
    threading.Thread(target=pipeline.scheduler, daemon=True).start()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
