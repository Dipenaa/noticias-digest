"""
preview.py — Servidor de preview local para iterar diseño sin gastar tokens.

Uso:
    python preview.py

Luego abre http://localhost:5001 en el navegador.
Pulsa el botón flotante "🔄 Regenerar" para ver los cambios después de editar renderer.py.
"""

import importlib
import sys
from flask import Flask, Response, jsonify

app = Flask(__name__)

# ── Datos de muestra (suficientes para ver todos los elementos visuales) ──────

_NOTICIAS = {
    "Política": [
        {"titulo": "El gobierno aprueba los nuevos presupuestos generales del Estado", "fuente": "El País", "enlace": "https://example.com/1", "resumen": "El Consejo de Ministros ha aprobado esta mañana los presupuestos generales con el apoyo de los socios de la coalición de gobierno.", "fecha": "2026-05-21", "sesgo_fuente": "centro-izquierda", "destacado": True, "asombro": 0},
        {"titulo": "La oposición denuncia falta de transparencia en el proceso presupuestario", "fuente": "El Mundo", "enlace": "https://example.com/2", "resumen": "El PP y Vox han denunciado irregularidades en la tramitación de las cuentas públicas y piden comparecencia urgente.", "fecha": "2026-05-21", "sesgo_fuente": "centro-derecha", "destacado": False, "asombro": 0},
        {"titulo": "Analistas económicos valoran positivamente las medidas fiscales incluidas", "fuente": "Expansión", "enlace": "https://example.com/3", "resumen": "Los expertos destacan la reducción del déficit y las inversiones en infraestructuras previstas para el próximo ejercicio.", "fecha": "2026-05-21", "sesgo_fuente": "centro", "destacado": False, "asombro": 0},
    ],
    "Economía": [
        {"titulo": "El Ibex 35 sube un 1,2% impulsado por la banca y el sector energético", "fuente": "Cinco Días", "enlace": "https://example.com/4", "resumen": "Las bolsas europeas cierran en positivo tras los buenos datos de inflación en la eurozona publicados esta mañana.", "fecha": "2026-05-21", "sesgo_fuente": "centro", "destacado": True, "asombro": 0},
        {"titulo": "La inflación cae al 2,1% en mayo, el nivel más bajo desde 2021", "fuente": "El Confidencial", "enlace": "https://example.com/5", "resumen": "El INE publica los datos definitivos que confirman la moderación de los precios en el conjunto de la economía española.", "fecha": "2026-05-21", "sesgo_fuente": "centro", "destacado": False, "asombro": 0},
    ],
    "Tecnología": [
        {"titulo": "La IA generativa transforma el mercado laboral europeo más rápido de lo previsto", "fuente": "El País Tecnología", "enlace": "https://example.com/6", "resumen": "Un informe de la Comisión Europea advierte que el 30% de los empleos administrativos serán automatizados antes de 2030.", "fecha": "2026-05-21", "sesgo_fuente": "centro-izquierda", "destacado": False, "asombro": 2},
    ],
}

_ANALISIS = {
    "https://example.com/1": {"sesgo": "izquierda",  "critica": "Enfoque favorable al gobierno sin contrastar con fuentes críticas. Omite el coste real de las medidas sociales.", "sentimiento": "positivo",  "asombro": 0, "razon_asombro": ""},
    "https://example.com/2": {"sesgo": "derecha",    "critica": "Tono claramente opositor. Usa términos como irregularidades sin aportar pruebas concretas.", "sentimiento": "negativo",  "asombro": 0, "razon_asombro": ""},
    "https://example.com/3": {"sesgo": "centro",     "critica": "Análisis equilibrado aunque centrado solo en aspectos positivos.", "sentimiento": "neutro",    "asombro": 0, "razon_asombro": ""},
    "https://example.com/4": {"sesgo": "centro",     "critica": "Información financiera precisa aunque sin contexto macroeconómico amplio.", "sentimiento": "optimista", "asombro": 0, "razon_asombro": ""},
    "https://example.com/5": {"sesgo": "centro",     "critica": "Dato correcto pero falta comparativa histórica más amplia.", "sentimiento": "neutro",    "asombro": 0, "razon_asombro": ""},
    "https://example.com/6": {"sesgo": "centro-izquierda", "critica": "Enfoque alarmista justificado por los datos, pero no menciona las nuevas ocupaciones que crea la IA.", "sentimiento": "alarmista", "asombro": 2, "razon_asombro": "Ritmo de automatización muy superior a predicciones anteriores."},
}

_GRUPOS = [
    {
        "titulo": "Aprobación de los presupuestos: visiones cruzadas en los medios",
        "sintesis": "El gobierno ha aprobado los presupuestos con apoyo parlamentario ajustado. La prensa de izquierda destaca las inversiones sociales y la reducción del déficit, mientras la de derecha critica la opacidad del proceso y pide más control parlamentario. Los analistas económicos señalan mejoras estructurales aunque advierten de riesgos inflacionistas a medio plazo.",
        "articulos": [
            {"fuente": "El País",   "titulo": "El gobierno aprueba los nuevos presupuestos", "enlace": "https://example.com/1", "categoria": "Política", "sesgo_fuente": "centro-izquierda", "alt": False},
            {"fuente": "El Mundo",  "titulo": "La oposición denuncia falta de transparencia", "enlace": "https://example.com/2", "categoria": "Política", "sesgo_fuente": "centro-derecha",   "alt": False},
            {"fuente": "Expansión", "titulo": "Analistas valoran las medidas fiscales",        "enlace": "https://example.com/3", "categoria": "Política", "sesgo_fuente": "centro",            "alt": False},
        ],
    }
]

_BOTON_PREVIEW = """
<div id="_prev-btn" style="
  position:fixed; bottom:1.5rem; right:1.5rem; z-index:9999;
  display:flex; flex-direction:column; gap:.5rem; align-items:flex-end;">
  <div id="_prev-msg" style="
    background:#1a1208; color:#fff; font-size:.75rem; padding:.35rem .75rem;
    border-radius:.375rem; opacity:0; transition:opacity .3s; white-space:nowrap;">
  </div>
  <button onclick="_regen()" style="
    background:#2d5a2d; color:#fff; border:none; border-radius:.5rem;
    padding:.6rem 1.1rem; font-size:.85rem; font-weight:600; cursor:pointer;
    box-shadow:0 2px 8px rgba(0,0,0,.2); font-family:inherit;">
    🔄 Regenerar
  </button>
</div>
<script>
function _regen() {
  var msg = document.getElementById('_prev-msg');
  msg.textContent = 'Regenerando...'; msg.style.opacity = '1';
  fetch('/regen').then(function(r){ return r.json(); }).then(function(d){
    msg.textContent = d.ok ? '✓ Listo' : '✗ Error';
    if(d.ok) setTimeout(function(){ location.reload(); }, 200);
    else setTimeout(function(){ msg.style.opacity='0'; }, 3000);
  });
}
</script>
"""


def _generar_html():
    # Recarga renderer en cada llamada para pillar los cambios del CSS
    import renderer
    importlib.reload(renderer)
    html = renderer.renderizar_html(_NOTICIAS, _ANALISIS, {}, {}, _GRUPOS)
    # Inyecta el botón justo antes de </body>
    return html.replace("</body>", _BOTON_PREVIEW + "\n</body>")


_cache_html: str | None = None


@app.route("/")
def index():
    global _cache_html
    if _cache_html is None:
        _cache_html = _generar_html()
    return Response(_cache_html, mimetype="text/html; charset=utf-8")


@app.route("/regen")
def regen():
    global _cache_html
    try:
        _cache_html = _generar_html()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


if __name__ == "__main__":
    print("Preview server en http://localhost:5001")
    print("Pulsa el botón 🔄 en el navegador para ver cambios tras editar renderer.py")
    _cache_html = _generar_html()
    app.run(port=5001, debug=False)
