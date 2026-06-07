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
        {"titulo": "El gobierno aprueba los nuevos presupuestos generales del Estado", "fuente": "El País", "enlace": "https://example.com/1", "resumen": "El Consejo de Ministros ha aprobado esta mañana los presupuestos generales con el apoyo de los socios de la coalición de gobierno.", "fecha": "2026-06-07", "sesgo_fuente": "centro-izquierda", "destacado": True, "asombro": 0, "importante": True, "tags": ["presupuestos", "gobierno"], "pregunta": "¿Qué partidas se han priorizado y cuáles han sido recortadas?", "titulo_es": "El gobierno aprueba los presupuestos"},
        {"titulo": "La oposición denuncia falta de transparencia en el proceso presupuestario", "fuente": "El Mundo", "enlace": "https://example.com/2", "resumen": "El PP y Vox han denunciado irregularidades en la tramitación de las cuentas públicas y piden comparecencia urgente.", "fecha": "2026-06-06", "sesgo_fuente": "centro-derecha", "destacado": False, "asombro": 0, "importante": False, "tags": ["oposición", "presupuestos"], "pregunta": "", "titulo_es": "La oposición denuncia falta de transparencia"},
        {"titulo": "Analistas económicos valoran positivamente las medidas fiscales incluidas", "fuente": "Expansión", "enlace": "https://example.com/3", "resumen": "Los expertos destacan la reducción del déficit y las inversiones en infraestructuras previstas para el próximo ejercicio.", "fecha": "2026-06-06", "sesgo_fuente": "centro", "destacado": False, "asombro": 0, "importante": False, "tags": ["economía", "fiscalidad"], "pregunta": "", "titulo_es": "Analistas valoran las medidas fiscales"},
        {"titulo": "El Senado bloqueará la ley de amnistía por cuarta vez consecutiva", "fuente": "ABC", "enlace": "https://example.com/1b", "resumen": "Los populares anuncian su veto en la cámara alta, forzando un nuevo proceso de mediación entre el gobierno y los independentistas.", "fecha": "2026-06-07", "sesgo_fuente": "derecha", "destacado": False, "asombro": 0, "importante": False, "tags": ["amnistía", "senado"], "pregunta": "", "titulo_es": "El Senado bloqueará la ley de amnistía"},
        {"titulo": "Puigdemont anuncia que regresará a España antes de verano", "fuente": "La Vanguardia", "enlace": "https://example.com/1c", "resumen": "El expresidente catalán asegura tener garantías suficientes para volver al territorio español sin ser detenido.", "fecha": "2026-06-07", "sesgo_fuente": "centro", "destacado": False, "asombro": 0, "importante": False, "tags": ["Puigdemont", "independencia"], "pregunta": "", "titulo_es": "Puigdemont anuncia su regreso a España"},
    ],
    "Economía": [
        {"titulo": "El Ibex 35 sube un 1,2% impulsado por la banca y el sector energético", "fuente": "Cinco Días", "enlace": "https://example.com/4", "resumen": "Las bolsas europeas cierran en positivo tras los buenos datos de inflación en la eurozona publicados esta mañana.", "fecha": "2026-06-07", "sesgo_fuente": "centro", "destacado": True, "asombro": 0, "importante": True, "tags": ["ibex", "bolsa", "banca"], "pregunta": "¿Refleja esta subida una recuperación sostenida o es puntual?", "titulo_es": "El Ibex sube impulsado por banca y energía"},
        {"titulo": "La inflación cae al 2,1% en mayo, el nivel más bajo desde 2021", "fuente": "El Confidencial", "enlace": "https://example.com/5", "resumen": "El INE publica los datos definitivos que confirman la moderación de los precios en el conjunto de la economía española.", "fecha": "2026-06-06", "sesgo_fuente": "centro", "destacado": False, "asombro": 0, "importante": False, "tags": ["inflación", "IPC"], "pregunta": "", "titulo_es": "La inflación cae al 2,1% en mayo"},
        {"titulo": "El BCE anuncia una bajada de tipos de 25 puntos básicos en julio", "fuente": "El Economista", "enlace": "https://example.com/5b", "resumen": "Christine Lagarde confirma que la evolución favorable de los precios permite relajar la política monetaria por tercer mes consecutivo.", "fecha": "2026-06-07", "sesgo_fuente": "centro", "destacado": False, "asombro": 0, "importante": False, "tags": ["BCE", "tipos", "inflación"], "pregunta": "", "titulo_es": "El BCE baja tipos en julio"},
        {"titulo": "La vivienda nueva en Madrid supera los 6.000€/m² por primera vez en la historia", "fuente": "El País Economía", "enlace": "https://example.com/5c", "resumen": "Los precios de la vivienda en las grandes ciudades siguen disparados mientras el alquiler social apenas cubre el 3% del parque total.", "fecha": "2026-06-07", "sesgo_fuente": "centro-izquierda", "destacado": False, "asombro": 0, "importante": True, "tags": ["vivienda", "Madrid", "precios"], "pregunta": "¿Es sostenible el mercado inmobiliario español o estamos ante una burbuja?", "titulo_es": "La vivienda nueva en Madrid supera 6.000€/m²"},
    ],
    "Tecnología": [
        {"titulo": "La IA generativa transforma el mercado laboral europeo más rápido de lo previsto", "fuente": "El País Tecnología", "enlace": "https://example.com/6", "resumen": "Un informe de la Comisión Europea advierte que el 30% de los empleos administrativos serán automatizados antes de 2030.", "fecha": "2026-06-07", "sesgo_fuente": "centro-izquierda", "destacado": False, "asombro": 2, "asombro_razon": "Ritmo de automatización muy superior a predicciones anteriores, desbordando los modelos de los propios economistas de la UE.", "importante": True, "tags": ["IA", "empleo", "automatización"], "pregunta": "¿Qué sectores europeos tienen mayor riesgo de automatización antes de 2030?", "titulo_es": "La IA transforma el empleo europeo más rápido de lo previsto"},
        {"titulo": "Descubren que los pulpos sueñan con cambios de color similares a experiencias vividas", "fuente": "Quanta Magazine", "enlace": "https://example.com/7", "resumen": "Investigadores de la Universidad de Washington documentan por primera vez patrones de coloración durante el sueño REM en pulpos, sugiriendo procesamiento de memorias visuales.", "fecha": "2026-06-07", "sesgo_fuente": "centro", "destacado": False, "asombro": 3, "asombro_razon": "Los pulpos son daltónicos pero procesan memoria visual durante el sueño — implica que la conciencia puede evolucionar por caminos radicalmente distintos al nuestro.", "importante": False, "tags": ["neurociencia", "pulpos", "sueño"], "pregunta": "Si los pulpos daltónicos codifican experiencias visuales, ¿qué nos dice eso sobre la subjetividad de la conciencia?", "titulo_es": "Pulpos sueñan y cambian de color al dormir"},
        {"titulo": "OpenAI presenta GPT-5 con capacidad de razonamiento científico autónomo", "fuente": "MIT Technology Review", "enlace": "https://example.com/6b", "resumen": "El nuevo modelo puede diseñar y ejecutar experimentos virtuales para probar hipótesis científicas sin intervención humana.", "fecha": "2026-06-07", "sesgo_fuente": "centro", "destacado": True, "asombro": 3, "asombro_razon": "Un modelo que puede hacer ciencia de forma autónoma colapsa la distinción entre herramienta e investigador.", "importante": True, "tags": ["OpenAI", "GPT-5", "ciencia"], "pregunta": "¿Qué significa que la IA pueda hacer ciencia por sí sola?", "titulo_es": "GPT-5 puede hacer investigación científica autónoma"},
    ],
    "Internacional": [
        {"titulo": "Trump impone nuevos aranceles del 25% a productos europeos desde julio", "fuente": "Reuters", "enlace": "https://example.com/i1", "resumen": "La Casa Blanca anuncia una nueva ronda de aranceles que afecta especialmente al sector del automóvil y la alimentación.", "fecha": "2026-06-07", "sesgo_fuente": "centro", "destacado": True, "asombro": 0, "importante": True, "tags": ["aranceles", "Trump", "UE"], "pregunta": "¿Qué capacidad de respuesta tiene la UE ante una escalada comercial con EE.UU.?", "titulo_es": "Trump impone aranceles del 25% a Europa"},
        {"titulo": "La India supera a China como mayor economía emergente en PIB ajustado por paridad", "fuente": "The Economist", "enlace": "https://example.com/i2", "resumen": "Por primera vez desde 1890, India produce más riqueza real per cápita ajustada que China según los nuevos cálculos del FMI.", "fecha": "2026-06-06", "sesgo_fuente": "centro", "destacado": False, "asombro": 2, "asombro_razon": "Un cambio de hegemonía económica que sucede en silencio, sin cobertura proporcional a su importancia histórica.", "importante": False, "tags": ["India", "China", "economía"], "pregunta": "", "titulo_es": "India supera a China en PIP ajustado"},
    ],
    "Ciencia": [
        {"titulo": "Investigadores crean el primer mapa completo del conectoma del cerebro de un ratón", "fuente": "Nature", "enlace": "https://example.com/s1", "resumen": "El proyecto MICrONS mapea 100.000 neuronas y 1.000 millones de sinapsis, el atlas neuronal más completo jamás realizado.", "fecha": "2026-06-07", "sesgo_fuente": "centro", "destacado": False, "asombro": 3, "asombro_razon": "El mapa más detallado del cerebro que existe — y aun así es solo el 1% del cerebro de un ratón, que es 1.000 veces más pequeño que el humano.", "importante": False, "tags": ["neurociencia", "cerebro", "conectoma"], "pregunta": "¿Qué nos enseña este mapa sobre cómo funciona la memoria y el aprendizaje?", "titulo_es": "Primer mapa completo del conectoma de un ratón"},
    ],
}

_ANALISIS = {
    "https://example.com/1":  {"sesgo": "izquierda",          "critica": "Enfoque favorable al gobierno sin contrastar con fuentes críticas. Omite el coste real de las medidas sociales.", "sentimiento": "positivo",    "asombro": 0, "asombro_razon": ""},
    "https://example.com/2":  {"sesgo": "derecha",            "critica": "Tono claramente opositor. Usa términos como irregularidades sin aportar pruebas concretas.", "sentimiento": "negativo",    "asombro": 0, "asombro_razon": ""},
    "https://example.com/3":  {"sesgo": "centro",             "critica": "Análisis equilibrado aunque centrado solo en aspectos positivos.", "sentimiento": "neutro",      "asombro": 0, "asombro_razon": ""},
    "https://example.com/1b": {"sesgo": "derecha",            "critica": "Anticipa el resultado sin matices sobre el proceso parlamentario real.", "sentimiento": "negativo",    "asombro": 0, "asombro_razon": ""},
    "https://example.com/1c": {"sesgo": "centro",             "critica": "Escasa verificación de las garantías mencionadas por Puigdemont.", "sentimiento": "neutro",      "asombro": 0, "asombro_razon": ""},
    "https://example.com/4":  {"sesgo": "centro",             "critica": "Información financiera precisa aunque sin contexto macroeconómico amplio.", "sentimiento": "optimista",   "asombro": 0, "asombro_razon": ""},
    "https://example.com/5":  {"sesgo": "centro",             "critica": "Dato correcto pero falta comparativa histórica más amplia.", "sentimiento": "neutro",      "asombro": 0, "asombro_razon": ""},
    "https://example.com/5b": {"sesgo": "centro",             "critica": "Buena cobertura técnica pero no aborda el impacto sobre hipotecas variables activas.", "sentimiento": "neutro",      "asombro": 0, "asombro_razon": ""},
    "https://example.com/5c": {"sesgo": "centro-izquierda",   "critica": "El dato del 3% de vivienda pública necesita fuente explícita.", "sentimiento": "alarmista",   "asombro": 0, "asombro_razon": ""},
    "https://example.com/6":  {"sesgo": "centro-izquierda",   "critica": "Enfoque alarmista justificado por los datos, pero no menciona las nuevas ocupaciones que crea la IA.", "sentimiento": "alarmista",   "asombro": 2, "asombro_razon": "Ritmo de automatización muy superior a predicciones anteriores."},
    "https://example.com/6b": {"sesgo": "centro",             "critica": "Cobertura rigurosa de un hito técnico con implicaciones filosóficas que el artículo apenas toca.", "sentimiento": "maravillado", "asombro": 3, "asombro_razon": "Un modelo que puede hacer ciencia autónoma colapsa la distinción entre herramienta e investigador."},
    "https://example.com/7":  {"sesgo": "centro",             "critica": "Ciencia sólida y bien explicada. El titular podría ser más preciso sobre las limitaciones del estudio.", "sentimiento": "maravillado", "asombro": 3, "asombro_razon": "Los pulpos son daltónicos pero procesan memoria visual durante el sueño."},
    "https://example.com/i1": {"sesgo": "centro",             "critica": "Cobertura factual sin análisis del impacto específico sobre sectores europeos.", "sentimiento": "negativo",    "asombro": 0, "asombro_razon": ""},
    "https://example.com/i2": {"sesgo": "centro",             "critica": "El dato es correcto pero el titular simplifica un cálculo muy matizado del FMI.", "sentimiento": "positivo",    "asombro": 2, "asombro_razon": "Un cambio de hegemonía económica que sucede en silencio."},
    "https://example.com/s1": {"sesgo": "centro",             "critica": "Rigor científico impecable. Falta perspectiva sobre aplicaciones médicas concretas.", "sentimiento": "maravillado", "asombro": 3, "asombro_razon": "El mapa más detallado del cerebro que existe — y es solo el 1% del cerebro de un ratón."},
}

_PROCESOS = [
    {
        "id": "ucrania", "nombre": "Guerra en Ucrania", "importancia": 9,
        "descripcion": "Conflicto armado en curso desde febrero 2022. Frente oriental estabilizado pero con avances tácticos rusos en Járkov.",
        "resumen_hoy": "Avances rusos en Járkov y nuevas sanciones occidentales acordadas en Bruselas. Zelenski pide más sistemas antiaéreos.",
        "estado": "escalada", "dias_activo": 848, "horizonte": "años", "tendencia_pct": 15,
        "articulos": [
            {"titulo": "Rusia avanza en Járkov tras bombardeos masivos", "fuente": "BBC Mundo", "enlace": "https://example.com/u1", "sesgo_fuente": "centro"},
            {"titulo": "La UE aprueba un nuevo paquete de sanciones energéticas", "fuente": "El País", "enlace": "https://example.com/u2", "sesgo_fuente": "centro-izquierda"},
            {"titulo": "Zelenski pide misiles de largo alcance a Biden en llamada urgente", "fuente": "Reuters", "enlace": "https://example.com/u3", "sesgo_fuente": "centro"},
            {"titulo": "Rusia dice que las sanciones no frenarán la operación militar especial", "fuente": "RT en Español", "enlace": "https://example.com/u4", "sesgo_fuente": "izquierda"},
        ],
        "historial": [{"fecha": f"2026-05-{d:02d}", "cobertura": c} for d, c in zip(range(7, 22), [6,8,7,9,5,6,8,7,10,6,8,9,7,5,8])],
    },
    {
        "id": "aranceles-trump", "nombre": "Guerra comercial EE.UU.–UE", "importancia": 8,
        "descripcion": "Trump reimpone aranceles del 25% sobre automóviles y productos agrícolas europeos desde julio 2026.",
        "resumen_hoy": "Bruselas prepara contramedidas sobre bienes americanos por valor de €90.000M. El sector del automóvil alemán en alerta máxima.",
        "estado": "escalada", "dias_activo": 32, "horizonte": "meses", "tendencia_pct": 45,
        "articulos": [
            {"titulo": "La UE estudia aranceles de represalia sobre bienes tecnológicos americanos", "fuente": "Financial Times", "enlace": "https://example.com/t1", "sesgo_fuente": "centro"},
            {"titulo": "VW y BMW advierten de un impacto de €15.000M si no hay acuerdo", "fuente": "Handelsblatt", "enlace": "https://example.com/t2", "sesgo_fuente": "centro"},
            {"titulo": "Trump: 'Europa lleva años robándole a América, esto acaba ahora'", "fuente": "Fox News", "enlace": "https://example.com/t3", "sesgo_fuente": "derecha"},
            {"titulo": "Los aranceles golpearán al consumidor americano más que al europeo", "fuente": "The Guardian", "enlace": "https://example.com/t4", "sesgo_fuente": "centro-izquierda"},
        ],
        "historial": [{"fecha": f"2026-05-{d:02d}", "cobertura": c} for d, c in zip(range(7, 22), [0,0,0,1,2,3,4,5,4,6,7,8,9,8,10])],
    },
    {
        "id": "clima-med", "nombre": "Crisis climática mediterránea", "importancia": 8,
        "descripcion": "Olas de calor récord en sur de Europa. Grecia, Turquía y el norte de África en emergencia desde mayo.",
        "resumen_hoy": "Temperatura récord de 47°C en Atenas. Portugal declara alerta roja. 12 muertos confirmados en tres países.",
        "estado": "escalada", "dias_activo": 45, "horizonte": "semanas", "tendencia_pct": 30,
        "articulos": [
            {"titulo": "Atenas registra 47°C, temperatura récord en junio para Europa", "fuente": "Euronews", "enlace": "https://example.com/c1", "sesgo_fuente": "centro"},
            {"titulo": "Portugal declara alerta roja: riesgo extremo de incendios en todo el país", "fuente": "DW Español", "enlace": "https://example.com/c2", "sesgo_fuente": "centro"},
            {"titulo": "Los climatólogos advierten: sin acción inmediata, el Mediterráneo será inhabitable en verano", "fuente": "The Guardian", "enlace": "https://example.com/c3", "sesgo_fuente": "centro-izquierda"},
        ],
        "historial": [{"fecha": f"2026-05-{d:02d}", "cobertura": c} for d, c in zip(range(7, 22), [1,2,1,2,3,2,3,4,5,6,7,8,8,9,9])],
    },
    {
        "id": "ia-regulacion", "nombre": "Regulación global de la IA", "importancia": 7,
        "descripcion": "Debate internacional sobre cómo regular los modelos de IA de alto riesgo. EE.UU., UE y China con enfoques radicalmente distintos.",
        "resumen_hoy": "El Parlamento Europeo aprueba enmiendas que endurecen los requisitos de transparencia para GPT-5 y modelos similares.",
        "estado": "estable", "dias_activo": 180, "horizonte": "años", "tendencia_pct": 5,
        "articulos": [
            {"titulo": "El Parlamento Europeo endurece la AI Act con requisitos de auditoría obligatoria", "fuente": "Politico Europe", "enlace": "https://example.com/r1", "sesgo_fuente": "centro"},
            {"titulo": "Silicon Valley critica la regulación europea como 'freno a la innovación'", "fuente": "Wired", "enlace": "https://example.com/r2", "sesgo_fuente": "centro"},
            {"titulo": "China presenta su propio marco regulatorio para IA, alineado con valores socialistas", "fuente": "South China Morning Post", "enlace": "https://example.com/r3", "sesgo_fuente": "centro"},
        ],
        "historial": [{"fecha": f"2026-05-{d:02d}", "cobertura": c} for d, c in zip(range(7, 22), [4,3,5,4,5,6,5,4,6,5,7,6,5,6,7])],
    },
    {
        "id": "vivienda-espana", "nombre": "Crisis de vivienda en España", "importancia": 7,
        "descripcion": "Los precios de la vivienda superan máximos históricos en Madrid y Barcelona mientras el alquiler social cubre solo el 3% del parque.",
        "resumen_hoy": "Madrid supera los 6.000€/m² en obra nueva. El gobierno anuncia 50.000 viviendas públicas pero los expertos dicen que llegan tarde.",
        "estado": "estable", "dias_activo": 320, "horizonte": "años", "tendencia_pct": 8,
        "articulos": [
            {"titulo": "Madrid: obra nueva supera 6.000€/m² por primera vez", "fuente": "El Confidencial", "enlace": "https://example.com/v1", "sesgo_fuente": "centro"},
            {"titulo": "El gobierno anuncia 50.000 viviendas de protección oficial para 2028", "fuente": "El País", "enlace": "https://example.com/v2", "sesgo_fuente": "centro-izquierda"},
            {"titulo": "La solución a la vivienda no es más regulación sino menos burocracia urbanística", "fuente": "Expansión", "enlace": "https://example.com/v3", "sesgo_fuente": "centro-derecha"},
            {"titulo": "Una generación atrapada: el 70% de menores de 35 no puede comprar piso en España", "fuente": "CTXT", "enlace": "https://example.com/v4", "sesgo_fuente": "izquierda"},
        ],
        "historial": [{"fecha": f"2026-05-{d:02d}", "cobertura": c} for d, c in zip(range(7, 22), [5,4,6,5,7,6,5,6,7,5,6,7,8,7,6])],
    },
]

_GRUPOS = [
    {
        "titulo": "Presupuestos 2026: el gobierno celebra, la oposición denuncia opacidad",
        "sintesis": "El Ejecutivo ha aprobado los presupuestos con un apoyo parlamentario ajustado. La prensa progresista destaca las inversiones sociales y la reducción del déficit. La prensa conservadora critica la falta de transparencia y pide comparecencia urgente. Los analistas económicos coinciden en que las medidas son estructuralmente sólidas aunque advierten de riesgos inflacionistas a medio plazo si el gasto no se contiene.",
        "articulos": [
            {"fuente": "El País",   "titulo": "El gobierno aprueba los nuevos presupuestos generales", "enlace": "https://example.com/1", "categoria": "Política", "sesgo_fuente": "centro-izquierda", "alt": False, "fecha": "2026-06-07"},
            {"fuente": "El Mundo",  "titulo": "La oposición denuncia falta de transparencia presupuestaria", "enlace": "https://example.com/2", "categoria": "Política", "sesgo_fuente": "centro-derecha",   "alt": False, "fecha": "2026-06-06"},
            {"fuente": "Expansión", "titulo": "Analistas valoran positivamente las medidas fiscales", "enlace": "https://example.com/3", "categoria": "Política", "sesgo_fuente": "centro", "alt": False, "fecha": "2026-06-06"},
            {"fuente": "ABC",       "titulo": "El Senado bloqueará la ley de amnistía por cuarta vez", "enlace": "https://example.com/1b", "categoria": "Política", "sesgo_fuente": "derecha", "alt": False, "fecha": "2026-06-07"},
        ],
        "perspectivas_extra": [
            {"fuente": "The Guardian", "titulo": "Spain passes budget amid coalition tensions", "enlace": "https://example.com/g1", "sesgo_fuente": "centro-izquierda", "_extra": True},
            {"fuente": "Reuters",      "titulo": "Spanish government approves 2026 budget",    "enlace": "https://example.com/r1", "sesgo_fuente": "centro",           "_extra": True},
            {"fuente": "Le Figaro",    "titulo": "L'Espagne adopte son budget 2026",            "enlace": "https://example.com/f1", "sesgo_fuente": "centro-derecha",   "_extra": True},
        ],
    },
    {
        "titulo": "Trump recarga los aranceles: la UE busca respuesta contundente sin agravar la crisis",
        "sintesis": "La derecha americana ve los aranceles como corrección de un desequilibrio histórico. Los medios europeos los leen como proteccionismo disfrazado de política de seguridad. La prensa económica advierte que el impacto real recaerá sobre el consumidor americano, no sobre los productores europeos. El sector del automóvil alemán es el más expuesto y el que más presiona a Bruselas para una respuesta negociada.",
        "articulos": [
            {"fuente": "Fox News",       "titulo": "Trump: Europa lleva décadas robándole a América", "enlace": "https://example.com/t3", "categoria": "Internacional", "sesgo_fuente": "derecha",          "alt": False, "fecha": "2026-06-07"},
            {"fuente": "Financial Times","titulo": "La UE estudia aranceles de represalia sobre bienes tecnológicos", "enlace": "https://example.com/t1", "categoria": "Internacional", "sesgo_fuente": "centro",           "alt": False, "fecha": "2026-06-07"},
            {"fuente": "The Guardian",   "titulo": "Los aranceles golpearán al consumidor americano más que al europeo", "enlace": "https://example.com/t4", "categoria": "Internacional", "sesgo_fuente": "centro-izquierda", "alt": False, "fecha": "2026-06-06"},
        ],
        "perspectivas_extra": [
            {"fuente": "Handelsblatt",   "titulo": "VW und BMW warnen vor Milliardenverlusten", "enlace": "https://example.com/t2", "sesgo_fuente": "centro", "_extra": True},
            {"fuente": "Le Monde",       "titulo": "Les États-Unis relancent la guerre commerciale", "enlace": "https://example.com/t5", "sesgo_fuente": "centro-izquierda", "_extra": True},
        ],
    },
    {
        "titulo": "La IA destruye empleos más rápido de lo previsto — o no, según a quién le preguntes",
        "sintesis": "Los organismos europeos presentan proyecciones alarmantes: 30% de empleos administrativos automatizados antes de 2030. La industria tecnológica rebate que cada trabajo eliminado genera 2-3 nuevos roles en IA y datos. Los sindicatos piden regulación inmediata. El debate de fondo es si la velocidad del cambio deja tiempo suficiente para reconvertir a los trabajadores afectados.",
        "articulos": [
            {"fuente": "El País Tecnología", "titulo": "La IA generativa transforma el empleo más rápido de lo previsto", "enlace": "https://example.com/6", "categoria": "Tecnología", "sesgo_fuente": "centro-izquierda", "alt": False, "fecha": "2026-06-07"},
            {"fuente": "MIT Technology Review", "titulo": "GPT-5 puede diseñar y ejecutar investigación científica autónoma", "enlace": "https://example.com/6b", "categoria": "Tecnología", "sesgo_fuente": "centro", "alt": False, "fecha": "2026-06-07"},
            {"fuente": "Wired", "titulo": "Silicon Valley critica la regulación europea como freno a la innovación", "enlace": "https://example.com/r2", "categoria": "Tecnología", "sesgo_fuente": "centro", "alt": False, "fecha": "2026-06-06"},
        ],
        "perspectivas_extra": [
            {"fuente": "CTXT",  "titulo": "La automatización sin red de seguridad es una catástrofe social programada", "enlace": "https://example.com/ia1", "sesgo_fuente": "izquierda", "_extra": True},
            {"fuente": "Forbes","titulo": "Why AI will create more jobs than it destroys", "enlace": "https://example.com/ia2", "sesgo_fuente": "centro-derecha", "_extra": True},
        ],
    },
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
