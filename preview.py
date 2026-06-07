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
        {"titulo": "El gobierno aprueba los nuevos presupuestos generales del Estado", "fuente": "El País", "enlace": "https://example.com/1", "resumen": "El Consejo de Ministros ha aprobado esta mañana los presupuestos generales con el apoyo de los socios de la coalición de gobierno.", "fecha": "2026-05-21", "sesgo_fuente": "centro-izquierda", "destacado": True, "asombro": 0, "importante": True, "tags": ["presupuestos", "gobierno"], "pregunta": "¿Qué partidas se han priorizado y cuáles han sido recortadas?", "titulo_es": "El gobierno aprueba los presupuestos"},
        {"titulo": "La oposición denuncia falta de transparencia en el proceso presupuestario", "fuente": "El Mundo", "enlace": "https://example.com/2", "resumen": "El PP y Vox han denunciado irregularidades en la tramitación de las cuentas públicas y piden comparecencia urgente.", "fecha": "2026-05-21", "sesgo_fuente": "centro-derecha", "destacado": False, "asombro": 0, "importante": False, "tags": ["oposición", "presupuestos"], "pregunta": "", "titulo_es": "La oposición denuncia falta de transparencia"},
        {"titulo": "Analistas económicos valoran positivamente las medidas fiscales incluidas", "fuente": "Expansión", "enlace": "https://example.com/3", "resumen": "Los expertos destacan la reducción del déficit y las inversiones en infraestructuras previstas para el próximo ejercicio.", "fecha": "2026-05-21", "sesgo_fuente": "centro", "destacado": False, "asombro": 0, "importante": False, "tags": ["economía", "fiscalidad"], "pregunta": "", "titulo_es": "Analistas valoran las medidas fiscales"},
    ],
    "Economía": [
        {"titulo": "El Ibex 35 sube un 1,2% impulsado por la banca y el sector energético", "fuente": "Cinco Días", "enlace": "https://example.com/4", "resumen": "Las bolsas europeas cierran en positivo tras los buenos datos de inflación en la eurozona publicados esta mañana.", "fecha": "2026-05-21", "sesgo_fuente": "centro", "destacado": True, "asombro": 0, "importante": True, "tags": ["ibex", "bolsa", "banca"], "pregunta": "¿Refleja esta subida una recuperación sostenida o es puntual?", "titulo_es": "El Ibex sube impulsado por banca y energía"},
        {"titulo": "La inflación cae al 2,1% en mayo, el nivel más bajo desde 2021", "fuente": "El Confidencial", "enlace": "https://example.com/5", "resumen": "El INE publica los datos definitivos que confirman la moderación de los precios en el conjunto de la economía española.", "fecha": "2026-05-21", "sesgo_fuente": "centro", "destacado": False, "asombro": 0, "importante": False, "tags": ["inflación", "IPC"], "pregunta": "", "titulo_es": "La inflación cae al 2,1% en mayo"},
    ],
    "Tecnología": [
        {"titulo": "La IA generativa transforma el mercado laboral europeo más rápido de lo previsto", "fuente": "El País Tecnología", "enlace": "https://example.com/6", "resumen": "Un informe de la Comisión Europea advierte que el 30% de los empleos administrativos serán automatizados antes de 2030.", "fecha": "2026-05-21", "sesgo_fuente": "centro-izquierda", "destacado": False, "asombro": 2, "asombro_razon": "Ritmo de automatización muy superior a predicciones anteriores, desbordando los modelos de los propios economistas de la UE.", "importante": True, "tags": ["IA", "empleo", "automatización"], "pregunta": "¿Qué sectores europeos tienen mayor riesgo de automatización antes de 2030?", "titulo_es": "La IA transforma el empleo europeo más rápido de lo previsto"},
        {"titulo": "Descubren que los pulpos sueñan con cambios de color similares a experiencias vividas", "fuente": "Quanta Magazine", "enlace": "https://example.com/7", "resumen": "Investigadores de la Universidad de Washington documentan por primera vez patrones de coloración durante el sueño REM en pulpos, sugiriendo procesamiento de memorias visuales.", "fecha": "2026-05-21", "sesgo_fuente": "centro", "destacado": False, "asombro": 3, "asombro_razon": "Los pulpos son daltónicos pero procesan memoria visual durante el sueño — implica que la conciencia puede evolucionar por caminos radicalmente distintos al nuestro.", "importante": False, "tags": ["neurociencia", "pulpos", "sueño"], "pregunta": "Si los pulpos daltónicos codifican experiencias visuales, ¿qué nos dice eso sobre la subjetividad de la conciencia?", "titulo_es": "Pulpos sueñan y cambian de color al dormir"},
    ],
}

_ANALISIS = {
    "https://example.com/1": {"sesgo": "izquierda",  "critica": "Enfoque favorable al gobierno sin contrastar con fuentes críticas. Omite el coste real de las medidas sociales.", "sentimiento": "positivo",  "asombro": 0, "asombro_razon": ""},
    "https://example.com/2": {"sesgo": "derecha",    "critica": "Tono claramente opositor. Usa términos como irregularidades sin aportar pruebas concretas.", "sentimiento": "negativo",  "asombro": 0, "asombro_razon": ""},
    "https://example.com/3": {"sesgo": "centro",     "critica": "Análisis equilibrado aunque centrado solo en aspectos positivos.", "sentimiento": "neutro",    "asombro": 0, "asombro_razon": ""},
    "https://example.com/4": {"sesgo": "centro",     "critica": "Información financiera precisa aunque sin contexto macroeconómico amplio.", "sentimiento": "optimista", "asombro": 0, "asombro_razon": ""},
    "https://example.com/5": {"sesgo": "centro",     "critica": "Dato correcto pero falta comparativa histórica más amplia.", "sentimiento": "neutro",    "asombro": 0, "asombro_razon": ""},
    "https://example.com/6": {"sesgo": "centro-izquierda", "critica": "Enfoque alarmista justificado por los datos, pero no menciona las nuevas ocupaciones que crea la IA.", "sentimiento": "alarmista", "asombro": 2, "asombro_razon": "Ritmo de automatización muy superior a predicciones anteriores."},
    "https://example.com/7": {"sesgo": "centro",     "critica": "Ciencia sólida y bien explicada. El titular podría ser más preciso sobre las limitaciones del estudio.", "sentimiento": "maravillado", "asombro": 3, "asombro_razon": "Los pulpos son daltónicos pero procesan memoria visual durante el sueño."},
}

_PROCESOS = [
    {
        "id": "ucrania", "nombre": "Guerra en Ucrania", "importancia": 9,
        "descripcion": "Conflicto armado en curso desde febrero 2022.",
        "resumen_hoy": "Avances rusos en Járkov y nuevas sanciones occidentales acordadas en Bruselas.",
        "estado": "escalada", "dias_activo": 848, "horizonte": "años", "tendencia_pct": 15,
        "articulos": [
            {"titulo": "Rusia avanza en Járkov tras bombardeos", "fuente": "BBC Mundo", "enlace": "https://example.com/u1"},
            {"titulo": "La UE aprueba un nuevo paquete de sanciones", "fuente": "El País", "enlace": "https://example.com/u2"},
        ],
        "historial": [{"fecha": f"2026-05-{d}", "cobertura": c} for d, c in zip(range(7, 22), [6,8,7,9,5,6,8,7,10,6,8,9,7,5,8])],
    },
    {
        "id": "francia", "nombre": "Elecciones Francia 2027", "importancia": 6,
        "descripcion": "Ciclo electoral francés. Le Pen lidera sondeos para segunda vuelta.",
        "resumen_hoy": "Nuevas encuestas sitúan a Le Pen 8 puntos por encima de Macron en intención de voto.",
        "estado": "estable", "dias_activo": 210, "horizonte": "meses", "tendencia_pct": 0,
        "articulos": [
            {"titulo": "Le Pen amplía ventaja en sondeos presidenciales", "fuente": "France 24", "enlace": "https://example.com/f1"},
        ],
        "historial": [{"fecha": f"2026-05-{d}", "cobertura": c} for d, c in zip(range(7, 22), [3,4,3,5,4,3,4,5,4,3,4,6,5,4,4])],
    },
    {
        "id": "clima-med", "nombre": "Crisis climática mediterránea", "importancia": 8,
        "descripcion": "Olas de calor récord en sur de Europa. Grecia y Turquía en emergencia.",
        "resumen_hoy": "Temperatura récord de 47°C en Atenas. Portugal declara alerta roja.",
        "estado": "escalada", "dias_activo": 45, "horizonte": "semanas", "tendencia_pct": 30,
        "articulos": [
            {"titulo": "Atenas registra 47°C, temperatura récord en junio", "fuente": "Euronews", "enlace": "https://example.com/c1"},
            {"titulo": "Portugal declara alerta roja por ola de calor", "fuente": "DW Español", "enlace": "https://example.com/c2"},
        ],
        "historial": [{"fecha": f"2026-05-{d}", "cobertura": c} for d, c in zip(range(7, 22), [1,2,1,2,3,2,3,4,5,6,7,8,8,9,9])],
    },
]

_GRUPOS = [
    {
        "titulo": "Aprobación de los presupuestos: visiones cruzadas en los medios",
        "sintesis": "El gobierno ha aprobado los presupuestos con apoyo parlamentario ajustado. La prensa de izquierda destaca las inversiones sociales y la reducción del déficit, mientras la de derecha critica la opacidad del proceso y pide más control parlamentario. Los analistas económicos señalan mejoras estructurales aunque advierten de riesgos inflacionistas a medio plazo.",
        "articulos": [
            {"fuente": "El País",   "titulo": "El gobierno aprueba los nuevos presupuestos", "enlace": "https://example.com/1", "categoria": "Política", "sesgo_fuente": "centro-izquierda", "alt": False, "fecha": "2026-06-07"},
            {"fuente": "El Mundo",  "titulo": "La oposición denuncia falta de transparencia", "enlace": "https://example.com/2", "categoria": "Política", "sesgo_fuente": "centro-derecha",   "alt": False, "fecha": "2026-06-06"},
            {"fuente": "Expansión", "titulo": "Analistas valoran las medidas fiscales",        "enlace": "https://example.com/3", "categoria": "Política", "sesgo_fuente": "centro",            "alt": False, "fecha": "2026-06-06"},
        ],
        "perspectivas_extra": [
            {"fuente": "The Guardian", "titulo": "Spain passes budget amid coalition tensions", "enlace": "https://example.com/g1", "sesgo_fuente": "centro-izquierda", "_extra": True},
            {"fuente": "Reuters",      "titulo": "Spanish government approves 2026 budget",      "enlace": "https://example.com/r1", "sesgo_fuente": "centro",           "_extra": True},
            {"fuente": "Le Figaro",    "titulo": "L'Espagne adopte son budget 2026",            "enlace": "https://example.com/f1", "sesgo_fuente": "centro-derecha",   "_extra": True},
            {"fuente": "Valencia News","titulo": "Reacciones autonómicas al nuevo presupuesto",  "enlace": "https://example.com/v1", "sesgo_fuente": "desconocido",      "_extra": True},
        ],
    }
]

_BOTON_PREVIEW = ""


def _generar_html():
    # Borrar todos los módulos renderer para reimportar frescos (evita problemas de orden en reload)
    for name in [k for k in sys.modules if k == "renderer" or k.startswith("renderer.")]:
        del sys.modules[name]
    import renderer
    html = renderer.renderizar_html(
        _NOTICIAS, _ANALISIS,
        grupos_sintesis=_GRUPOS,
        procesos=_PROCESOS,
    )
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
    print("Pulsa el boton [Regenerar] en el navegador para ver cambios tras editar renderer.py")
    _cache_html = _generar_html()
    app.run(port=5001, debug=False)
