"""
sandbox_render.py — Genera sandbox.html con estilos de styles_sandbox.py.

Uso:
    python sandbox_render.py

Edita styles_sandbox.py para iterar el diseño sin tocar producción.
"""

import renderer
import styles_sandbox

# Patch: usa el CSS del sandbox en vez del de producción
renderer._CSS = styles_sandbox._CSS

# ── Datos de muestra (mismos que preview.py) ─────────────────────────────────

_NOTICIAS = {
    "Política": [
        {"titulo": "El gobierno aprueba los nuevos presupuestos generales del Estado", "fuente": "El País", "enlace": "https://example.com/1", "resumen": "El Consejo de Ministros ha aprobado esta mañana los presupuestos generales con el apoyo de los socios de la coalición de gobierno.", "fecha": "2026-05-24", "sesgo_fuente": "centro-izquierda", "destacado": True, "asombro": 0},
        {"titulo": "La oposición denuncia falta de transparencia en el proceso presupuestario", "fuente": "El Mundo", "enlace": "https://example.com/2", "resumen": "El PP y Vox han denunciado irregularidades en la tramitación de las cuentas públicas y piden comparecencia urgente.", "fecha": "2026-05-24", "sesgo_fuente": "centro-derecha", "destacado": False, "asombro": 0},
        {"titulo": "Analistas económicos valoran positivamente las medidas fiscales incluidas", "fuente": "Expansión", "enlace": "https://example.com/3", "resumen": "Los expertos destacan la reducción del déficit y las inversiones en infraestructuras previstas para el próximo ejercicio.", "fecha": "2026-05-24", "sesgo_fuente": "centro", "destacado": False, "asombro": 0},
    ],
    "Economía": [
        {"titulo": "El Ibex 35 sube un 1,2% impulsado por la banca y el sector energético", "fuente": "Cinco Días", "enlace": "https://example.com/4", "resumen": "Las bolsas europeas cierran en positivo tras los buenos datos de inflación en la eurozona publicados esta mañana.", "fecha": "2026-05-24", "sesgo_fuente": "centro", "destacado": True, "asombro": 0},
        {"titulo": "La inflación cae al 2,1% en mayo, el nivel más bajo desde 2021", "fuente": "El Confidencial", "enlace": "https://example.com/5", "resumen": "El INE publica los datos definitivos que confirman la moderación de los precios en el conjunto de la economía española.", "fecha": "2026-05-24", "sesgo_fuente": "centro", "destacado": False, "asombro": 0},
    ],
    "Tecnología": [
        {"titulo": "La IA generativa transforma el mercado laboral europeo más rápido de lo previsto", "fuente": "El País Tecnología", "enlace": "https://example.com/6", "resumen": "Un informe de la Comisión Europea advierte que el 30% de los empleos administrativos serán automatizados antes de 2030.", "fecha": "2026-05-24", "sesgo_fuente": "centro-izquierda", "destacado": False, "asombro": 2},
        {"titulo": "OpenAI lanza GPT-5 con capacidades de razonamiento extendido", "fuente": "Xataka", "enlace": "https://example.com/7", "resumen": "El nuevo modelo supera en benchmarks a todos los anteriores y puede mantener contextos de más de un millón de tokens.", "fecha": "2026-05-24", "sesgo_fuente": "centro", "destacado": True, "asombro": 1},
    ],
    "Ciencia": [
        {"titulo": "Descubren una nueva especie de homínido en las cuevas de Atapuerca", "fuente": "El País Ciencia", "enlace": "https://example.com/8", "resumen": "Los investigadores del CENIEH han encontrado restos de una especie desconocida que podría reescribir la historia de la evolución humana en Europa.", "fecha": "2026-05-24", "sesgo_fuente": "centro", "destacado": True, "asombro": 3},
    ],
    "Internacional": [
        {"titulo": "La ONU alerta del deterioro acelerado de la situación humanitaria en Gaza", "fuente": "El Confidencial", "enlace": "https://example.com/9", "resumen": "Los organismos internacionales piden acceso inmediato para el reparto de ayuda humanitaria ante el bloqueo de suministros básicos.", "fecha": "2026-05-24", "sesgo_fuente": "centro-izquierda", "destacado": True, "asombro": 0},
        {"titulo": "Trump anuncia nuevos aranceles al acero europeo desde julio", "fuente": "El Mundo", "enlace": "https://example.com/10", "resumen": "La Casa Blanca confirma una tasa del 25% sobre importaciones de acero y aluminio procedentes de la UE, desencadenando una respuesta de Bruselas.", "fecha": "2026-05-24", "sesgo_fuente": "centro-derecha", "destacado": False, "asombro": 0},
    ],
}

_ANALISIS = {
    "https://example.com/1": {"sesgo": "izquierda",  "critica": "Enfoque favorable al gobierno sin contrastar con fuentes críticas. Omite el coste real de las medidas sociales.", "sentimiento": "positivo",  "asombro": 0, "razon_asombro": ""},
    "https://example.com/2": {"sesgo": "derecha",    "critica": "Tono claramente opositor. Usa términos como 'irregularidades' sin aportar pruebas concretas.", "sentimiento": "negativo",  "asombro": 0, "razon_asombro": ""},
    "https://example.com/3": {"sesgo": "centro",     "critica": "Análisis equilibrado aunque centrado solo en aspectos positivos.", "sentimiento": "neutro",    "asombro": 0, "razon_asombro": ""},
    "https://example.com/4": {"sesgo": "centro",     "critica": "Información financiera precisa aunque sin contexto macroeconómico amplio.", "sentimiento": "optimista", "asombro": 0, "razon_asombro": ""},
    "https://example.com/5": {"sesgo": "centro",     "critica": "Dato correcto pero falta comparativa histórica más amplia.", "sentimiento": "neutro",    "asombro": 0, "razon_asombro": ""},
    "https://example.com/6": {"sesgo": "centro-izquierda", "critica": "Enfoque alarmista justificado por los datos, pero no menciona las nuevas ocupaciones que crea la IA.", "sentimiento": "alarmista", "asombro": 2, "razon_asombro": "Ritmo de automatización muy superior a predicciones anteriores."},
    "https://example.com/7": {"sesgo": "centro",     "critica": "Cobertura técnica sólida. Falta análisis de implicaciones éticas y regulatorias.", "sentimiento": "optimista", "asombro": 1, "razon_asombro": "Salto cualitativo inesperado en razonamiento."},
    "https://example.com/8": {"sesgo": "centro",     "critica": "Información científica rigurosa con fuentes primarias. Muy bien contextualizada.", "sentimiento": "asombro",   "asombro": 3, "razon_asombro": "Potencial para reescribir completamente el árbol evolutivo europeo."},
    "https://example.com/9": {"sesgo": "centro-izquierda", "critica": "Cobertura humanitaria necesaria pero sin contrastar con fuentes israelíes.", "sentimiento": "negativo",  "asombro": 0, "razon_asombro": ""},
    "https://example.com/10": {"sesgo": "derecha",   "critica": "Contextualiza bien la medida pero minimiza el impacto en exportadores europeos.", "sentimiento": "negativo",  "asombro": 0, "razon_asombro": ""},
}

_GRUPOS = [
    {
        "titulo": "Presupuestos: gobierno y oposición con narrativas opuestas",
        "sintesis": "El gobierno celebra la aprobación destacando inversión social; la oposición denuncia opacidad. Los analistas económicos dan un veredicto positivo moderado. La cobertura mediática refleja fielmente las líneas editoriales de cada cabecera sin apenas puntos de contacto entre narrativas.",
        "articulos": [
            {"fuente": "El País",   "titulo": "El gobierno aprueba los nuevos presupuestos", "enlace": "https://example.com/1", "categoria": "Política", "sesgo_fuente": "centro-izquierda", "alt": False},
            {"fuente": "El Mundo",  "titulo": "La oposición denuncia falta de transparencia", "enlace": "https://example.com/2", "categoria": "Política", "sesgo_fuente": "centro-derecha",   "alt": False},
            {"fuente": "Expansión", "titulo": "Analistas valoran las medidas fiscales",        "enlace": "https://example.com/3", "categoria": "Política", "sesgo_fuente": "centro",            "alt": False},
        ],
    },
    {
        "titulo": "IA avanza más rápido de lo que la sociedad puede absorber",
        "sintesis": "Dos noticias distintas apuntan al mismo fenómeno: la aceleración de la IA supera la capacidad de adaptación laboral y regulatoria. El informe europeo sobre automatización y el lanzamiento de GPT-5 son síntomas del mismo proceso estructural.",
        "articulos": [
            {"fuente": "El País Tecnología", "titulo": "La IA transforma el mercado laboral europeo", "enlace": "https://example.com/6", "categoria": "Tecnología", "sesgo_fuente": "centro-izquierda", "alt": False},
            {"fuente": "Xataka",             "titulo": "OpenAI lanza GPT-5",                           "enlace": "https://example.com/7", "categoria": "Tecnología", "sesgo_fuente": "centro",            "alt": False},
        ],
    },
]

# ── Generar HTML ──────────────────────────────────────────────────────────────

def _con_tab(html: str, tab: str) -> str:
    """Inyecta un script que activa una tab concreta al abrir el HTML."""
    script = f'<script>addEventListener("load",()=>{{var b=document.querySelector(\'[data-tab="{tab}"]\');if(b)b.click();}});</script>'
    return html.replace("</body>", script + "\n</body>")

if __name__ == "__main__":
    base = renderer.renderizar_html(_NOTICIAS, _ANALISIS, {}, {}, _GRUPOS)

    tabs = [
        ("sandbox.html",           None),
        ("sandbox_sintesis.html",  "sintesis"),
        ("sandbox_destacadas.html","destacadas"),
        ("sandbox_asombro.html",   "asombro"),
        ("sandbox_stats.html",     "estadisticas"),
    ]

    for fname, tab in tabs:
        html = _con_tab(base, tab) if tab else base
        with open(fname, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  {fname} ({len(html):,} chars)")

    print("Listo.")
