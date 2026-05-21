"""
Script de autoresearch para optimizar el prompt de synthesizer.py.
Usa artículos ficticios diseñados para tener solapamientos claros.
"""
import json
import sys
import anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL

# ---------------------------------------------------------------------------
# Artículos ficticios — diseñados con solapamientos intencionales
# ---------------------------------------------------------------------------

# Grupo A: reforma laboral (3 artículos, distintas fuentes y ángulos)
# Grupo B: ola de calor (2 artículos)
# Outlier: cuervos (no encaja con nada)
# Outlier: presupuestos UE (no encaja con nada)

ARTICULOS_TEST = [
    {
        "id": 0,
        "fuente": "El País",
        "titulo": "El Congreso aprueba la reforma laboral con el apoyo de los sindicatos",
        "resumen": "La nueva reforma laboral salió adelante con 176 votos. CCOO y UGT la celebran como una victoria histórica que refuerza la estabilidad en el empleo y limita los contratos temporales abusivos.",
    },
    {
        "id": 1,
        "fuente": "ABC",
        "titulo": "La reforma laboral aprobada dispara la incertidumbre entre las pymes",
        "resumen": "Organizaciones empresariales advierten de que la nueva norma laboral encarecerá los despidos y reducirá la flexibilidad que necesitan las pequeñas empresas. Calculan que puede destruir hasta 80.000 empleos en el primer año.",
    },
    {
        "id": 2,
        "fuente": "Expansión",
        "titulo": "Los mercados reaccionan con calma a la aprobación de la reforma del mercado laboral",
        "resumen": "El Ibex-35 cerró prácticamente plano tras la votación parlamentaria de la reforma laboral. Los analistas señalan que ya estaba descontada y que su impacto real dependerá del desarrollo reglamentario.",
    },
    {
        "id": 3,
        "fuente": "La Vanguardia",
        "titulo": "Mayo de 2025 bate todos los récords de temperatura en España",
        "resumen": "La Agencia Estatal de Meteorología confirma que mayo fue el más caluroso desde 1950, con una media de 2,3 grados por encima de lo normal. Doce provincias declararon alerta por calor extremo.",
    },
    {
        "id": 4,
        "fuente": "El Mundo",
        "titulo": "La ola de calor de mayo deja al menos tres muertos y colapsa urgencias",
        "resumen": "Los hospitales de Sevilla, Córdoba y Badajoz registraron colapsos en urgencias por golpes de calor durante la primera quincena de mayo. La Junta de Andalucía activó el plan de contingencia sanitaria.",
    },
    {
        "id": 5,
        "fuente": "Nature",
        "titulo": "Los cuervos demuestran capacidad de planificación futura equiparable a la humana",
        "resumen": "Un experimento publicado en Nature demuestra que los cuervos pueden renunciar a una recompensa inmediata para obtener una mayor en el futuro, anticipando escenarios que nunca han vivido.",
    },
    {
        "id": 6,
        "fuente": "El Confidencial",
        "titulo": "La UE aprueba un presupuesto récord para 2026 con más fondos para defensa",
        "resumen": "El Parlamento Europeo votó a favor del presupuesto comunitario para 2026, que incluye un aumento del 15% en partidas de defensa y una reducción de fondos agrícolas para financiarlo.",
    },
]

PROMPT_TEMPLATE = """
Eres un editor periodístico experto en análisis comparativo de medios.
Recibes una lista de artículos de distintas fuentes y debes:

1. AGRUPAR los artículos que traten el MISMO evento o hecho noticioso concreto.
   - Agrupa solo por HECHOS específicos, no por temas generales.
     Ejemplo correcto: "Aprobación de la ley X en el parlamento".
     Ejemplo incorrecto: "Política española".
   - Un grupo debe tener mínimo 2 artículos.
   - Si un artículo no encaja con ningún otro, omítelo.

2. Para cada grupo, redacta en español una SÍNTESIS que:
   - Párrafo 1: describe el hecho central con precisión y objetividad.
   - Párrafo 2: contrasta cómo lo enfocan las distintas fuentes
     (diferencias de énfasis, ángulos, datos que incluye cada una o que omite).
   - Párrafo 3 (opcional, solo si hay divergencia notable): señala
     las perspectivas más alejadas entre sí y qué revela esa diferencia.

Artículos disponibles:
{articulos_json}

Responde ÚNICAMENTE con JSON válido sin bloques de código markdown:
{{
  "grupos": [
    {{
      "titulo": "Título con verbo activo que capture la tensión o el ángulo central de la historia",
      "sintesis": "Texto completo de la síntesis...",
      "ids": [0, 3, 7]
    }}
  ]
}}

Si ningún artículo está relacionado con otro, responde con {{"grupos": []}}.
"""

# ---------------------------------------------------------------------------
# Evaluación — 7 checks
# ---------------------------------------------------------------------------

def evaluar(resultado: dict) -> tuple[int, list[str]]:
    checks_ok = 0
    fallos = []
    grupos = resultado.get("grupos", [])

    # Check 1: JSON válido con campo "grupos"
    if isinstance(grupos, list):
        checks_ok += 1
    else:
        fallos.append("CHECK 1 FALLO: respuesta no tiene campo 'grupos' como lista")
        return 0, fallos

    # Check 2: detecta exactamente 2 grupos (reforma laboral + ola de calor)
    if len(grupos) == 2:
        checks_ok += 1
    else:
        fallos.append(f"CHECK 2 FALLO: detectó {len(grupos)} grupos, esperaba 2 (reforma + calor)")

    # Check 3: los grupos tienen mínimo 2 artículos de fuentes distintas
    grupos_validos = 0
    for g in grupos:
        ids = g.get("ids", [])
        fuentes = {ARTICULOS_TEST[i]["fuente"] for i in ids if 0 <= i < len(ARTICULOS_TEST)}
        if len(fuentes) >= 2:
            grupos_validos += 1
    if grupos_validos == len(grupos):
        checks_ok += 1
    else:
        fallos.append(f"CHECK 3 FALLO: {len(grupos) - grupos_validos} grupos sin fuentes distintas")

    # Check 4: títulos son específicos (más de 5 palabras, no solo "Política" o "Clima")
    titulos_genericos = [
        g.get("titulo", "") for g in grupos
        if len(g.get("titulo", "").split()) < 5
    ]
    if not titulos_genericos:
        checks_ok += 1
    else:
        fallos.append(f"CHECK 4 FALLO: títulos demasiado genéricos: {titulos_genericos}")

    # Check 5: síntesis mencionan al menos una fuente concreta en el párrafo de contraste
    fuentes_conocidas = {"El País", "ABC", "Expansión", "La Vanguardia", "El Mundo", "Nature", "El Confidencial"}
    sintesis_sin_fuentes = []
    for i, g in enumerate(grupos):
        sintesis = g.get("sintesis", "")
        menciona_fuente = any(f in sintesis for f in fuentes_conocidas)
        if not menciona_fuente:
            sintesis_sin_fuentes.append(i)
    if not sintesis_sin_fuentes:
        checks_ok += 1
    else:
        fallos.append(f"CHECK 5 FALLO: síntesis sin fuentes nombradas en grupos {sintesis_sin_fuentes}")

    # Check 6: cuervos (id=5) y presupuestos UE (id=6) NO están en ningún grupo (outliers correctos)
    ids_usados = {i for g in grupos for i in g.get("ids", [])}
    outliers_incluidos = ids_usados & {5, 6}
    if not outliers_incluidos:
        checks_ok += 1
    else:
        nombres = [ARTICULOS_TEST[i]["titulo"][:40] for i in outliers_incluidos]
        fallos.append(f"CHECK 6 FALLO: outliers incluidos incorrectamente: {nombres}")

    # Check 7: síntesis tienen sustancia (> 60 palabras totales)
    sintesis_cortas = [
        i for i, g in enumerate(grupos)
        if len(g.get("sintesis", "").split()) < 60
    ]
    if not sintesis_cortas:
        checks_ok += 1
    else:
        fallos.append(f"CHECK 7 FALLO: síntesis demasiado cortas en grupos {sintesis_cortas}")

    # Check 8: síntesis atribuyen datos concretos a fuentes ("Según X", "X señala", "Para X", "X apunta")
    verbos_atribucion = ["según", "señala", "apunta", "destaca", "indica", "afirma", "sostiene", "para "]
    sin_atribucion = []
    for i, g in enumerate(grupos):
        sintesis = g.get("sintesis", "").lower()
        tiene_atribucion = any(v in sintesis for v in verbos_atribucion)
        if not tiene_atribucion:
            sin_atribucion.append(i)
    if not sin_atribucion:
        checks_ok += 1
    else:
        fallos.append(f"CHECK 8 FALLO: síntesis sin atribución explícita a fuentes en grupos {sin_atribucion}")

    # Check 9: títulos de grupos reflejan tensión o ángulo, no solo el evento
    # Un buen título tiene un verbo o un contraste, no es solo un sustantivo
    titulos_planos = [
        g.get("titulo", "") for g in grupos
        if not any(c in g.get("titulo", "").lower() for c in
                   ["aprueba", "bate", "alerta", "crisis", "dispara", "colapsa", "récord", "frente", "entre", "divide", "contra"])
    ]
    if not titulos_planos:
        checks_ok += 1
    else:
        fallos.append(f"CHECK 9 FALLO: títulos sin tensión/verbo activo: {titulos_planos}")

    return checks_ok, fallos


# ---------------------------------------------------------------------------
# Llamada a la API
# ---------------------------------------------------------------------------

def llamar_claude(prompt_template: str) -> dict | None:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    prompt = prompt_template.format(
        articulos_json=json.dumps(ARTICULOS_TEST, ensure_ascii=False, indent=2)
    )
    try:
        msg = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4096,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}],
        )
        texto = msg.content[0].text.strip()
        if texto.startswith("```"):
            texto = "\n".join(texto.splitlines()[1:-1]).strip()
        return json.loads(texto)
    except Exception as e:
        print(f"  ERROR: {e}")
        return None


def medir(prompt_template: str, runs: int = 2) -> tuple[float, list[str]]:
    scores = []
    todos_fallos = []
    for i in range(runs):
        resultado = llamar_claude(prompt_template)
        if resultado is None:
            scores.append(0)
            todos_fallos.append(f"Run {i+1}: Error de API")
            continue
        score, fallos = evaluar(resultado)
        scores.append(score)
        todos_fallos.extend([f"Run {i+1}: {f}" for f in fallos])
        print(f"    Run {i+1}: {score}/7")
    media = sum(scores) / len(scores) if scores else 0
    return media, todos_fallos


if __name__ == "__main__":
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    print(f"\nMidiendo prompt synthesizer ({runs} runs)...")
    score, fallos = medir(PROMPT_TEMPLATE, runs)
    print(f"\n  Score medio: {score:.1f}/7")
    if fallos:
        print("\n  Fallos detectados:")
        for f in fallos:
            print(f"    - {f}")
    else:
        print("  OK - Todos los checks pasaron")
