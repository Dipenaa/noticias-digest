"""
Script de autoresearch para optimizar el prompt de analyzer.py.
Usa artículos ficticios para evaluar calidad del output sin datos reales.
"""
import json
import sys
import anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL_ANALISIS

# ---------------------------------------------------------------------------
# Artículos ficticios de prueba
# ---------------------------------------------------------------------------

ARTICULOS_TEST = [
    {
        "id": 0,
        "titulo": "El Gobierno aprueba la reforma laboral en votación ajustada",
        "fuente": "El País",
        "resumen": "El Congreso aprobó ayer la nueva reforma laboral con 176 votos a favor y 174 en contra. El Ejecutivo la presenta como un avance histórico para los trabajadores, mientras la oposición denuncia que beneficia principalmente a grandes empresas y precariza los contratos temporales.",
    },
    {
        "id": 1,
        "titulo": "Científicos descubren que los cuervos planifican el futuro igual que los humanos",
        "fuente": "El Mundo",
        "resumen": "Un estudio publicado en Nature revela que los cuervos son capaces de resistir recompensas inmediatas para obtener mayores beneficios futuros, un comportamiento hasta ahora considerado exclusivamente humano. Los experimentos demuestran que anticipan escenarios que nunca han experimentado.",
    },
    {
        "id": 2,
        "titulo": "Récord de llegadas de migrantes a Canarias en lo que va de año",
        "fuente": "ABC",
        "resumen": "Las costas canarias han registrado 23.000 llegadas en los primeros cinco meses del año, un 40% más que en el mismo período de 2024. El Gobierno central mantiene su política de acogida, pero los ayuntamientos insulares alertan del colapso de los servicios sociales.",
    },
    {
        "id": 3,
        "titulo": "El IPC sube al 3,2% en mayo impulsado por la energía y los alimentos",
        "fuente": "Expansión",
        "resumen": "El Instituto Nacional de Estadística confirmó ayer una inflación del 3,2% interanual en mayo, tres décimas por encima de abril. La energía sube un 8,1% y los alimentos un 4,3%, mientras los bienes industriales se mantienen estables.",
    },
    {
        "id": 4,
        "titulo": "Las temperaturas de mayo de 2025 son las más altas desde que hay registros",
        "fuente": "La Vanguardia",
        "resumen": "La Agencia Estatal de Meteorología confirma que mayo de 2025 ha sido el mes de mayo más caluroso registrado en España desde 1950, con una temperatura media 2,3 grados por encima de la media histórica. Los expertos vinculan el dato al cambio climático acelerado.",
    },
]

PROMPT_TEMPLATE = """
Eres un analista periodístico crítico e imparcial. Tu tarea es analizar \
los siguientes artículos de noticias y responder ÚNICAMENTE con JSON válido.

Para cada artículo, proporciona en español:
- "sesgo_ia": el sesgo ideológico que percibes en el ARTÍCULO (no en el medio).
  Usa exactamente uno de estos valores:
  "izquierda" | "centro-izquierda" | "centro" | "centro-derecha" | "derecha" | "desconocido"
- "critica": 1-2 oraciones señalando el ángulo, lo que se omite, el framing,
  o lo que merece cuestionarse. Sé concreto, no genérico.
  NO empieces con "El artículo", "Este artículo", "La noticia" o "El texto".
  Empieza directamente con la observación crítica.
- "importante": true si este artículo es uno de los 2 más relevantes e impactantes
  del lote (noticia de primer orden, alto impacto público), false en todos los demás.
  Marca exactamente 1 o 2 por lote, nunca más.
- "sentimiento": el tono emocional predominante del artículo.
  Usa exactamente uno de: "alarmista" | "neutral" | "optimista"
  alarmista = urgencia, miedo, catastrofismo, indignación exagerada.
  optimista  = esperanza, progreso, logro, solución destacada.
  neutral    = informativo, factual, sin carga emocional marcada.
- "asombro": puntuación del 0 al 3 que indica cuánto amplía este artículo
  la comprensión del mundo desde una perspectiva genuinamente humana.
  Es completamente independiente del sesgo político y del impacto noticioso.
  Pregúntate: ¿revela algo fascinante sobre cómo funciona el mundo, la gente,
  la historia o la condición humana? ¿Conecta el presente con algo más grande?
  ¿Es de esos artículos que te hacen parar y pensar aunque no sean urgentes?
  0 = noticia rutinaria, sin dimensión más profunda
  1 = algo interesante pero sin gran valor de asombro
  2 = revela algo genuinamente fascinante (patrón histórico inesperado,
      comportamiento humano sorprendente, descubrimiento que cambia perspectivas)
  3 = excepcional: de esos artículos raros que expanden cómo entiendes el mundo
  Sé muy exigente: en un lote de 10 artículos lo normal es 0 o 1 con puntuación 3,
  y 1 o 2 con puntuación 2. La mayoría deberían ser 0 o 1.
- "asombro_razon": si asombro es 2 o 3, una frase corta (15-25 palabras) que explique
  por qué este artículo es fascinante desde una perspectiva humana o histórica.
  Si asombro es 0 o 1, pon null.

Además proporciona:
- "analisis_general": un párrafo de análisis crítico del conjunto de noticias
  de esta sección. ¿Qué historia domina? ¿Qué perspectivas faltan?
  ¿Qué patrones o silencios ves?

Artículos (JSON):
{articulos_json}

Responde ÚNICAMENTE con este JSON (sin bloques de código, sin texto extra):
{{
  "articulos": [
    {{"sesgo_ia": "...", "critica": "...", "importante": false, "sentimiento": "neutral", "asombro": 0, "asombro_razon": null}},
    ...
  ],
  "analisis_general": "..."
}}
"""

VALORES_SESGO = {"izquierda", "centro-izquierda", "centro", "centro-derecha", "derecha", "desconocido"}
VALORES_SENTIMIENTO = {"alarmista", "neutral", "optimista"}

# ---------------------------------------------------------------------------
# Evaluación
# ---------------------------------------------------------------------------

def evaluar(resultado: dict) -> tuple[int, list[str]]:
    """Devuelve (score de 0 a 6, lista de checks fallidos)."""
    checks_ok = 0
    fallos = []

    articulos = resultado.get("articulos", [])
    analisis = resultado.get("analisis_general", "")

    # Check 1: JSON tiene todos los campos requeridos
    campos = ["sesgo_ia", "critica", "importante", "sentimiento", "asombro", "asombro_razon"]
    todos_campos = all(all(c in a for c in campos) for a in articulos)
    if todos_campos and len(articulos) == len(ARTICULOS_TEST):
        checks_ok += 1
    else:
        fallos.append("CHECK 1 FALLO: faltan campos requeridos o número incorrecto de artículos")

    # Check 2: critica es específica (> 20 palabras en cada artículo)
    criticas_ok = all(len(a.get("critica", "").split()) >= 20 for a in articulos)
    if criticas_ok:
        checks_ok += 1
    else:
        cortas = [i for i, a in enumerate(articulos) if len(a.get("critica", "").split()) < 20]
        fallos.append(f"CHECK 2 FALLO: críticas demasiado cortas en artículos {cortas}")

    # Check 3: sesgo_ia usa solo valores permitidos
    sesgos_ok = all(a.get("sesgo_ia") in VALORES_SESGO for a in articulos)
    if sesgos_ok:
        checks_ok += 1
    else:
        invalidos = [a.get("sesgo_ia") for a in articulos if a.get("sesgo_ia") not in VALORES_SESGO]
        fallos.append(f"CHECK 3 FALLO: valores de sesgo inválidos: {invalidos}")

    # Check 4: asombro es conservador (máximo 1 artículo con puntuación 3 en lote de 5)
    asombros_3 = sum(1 for a in articulos if a.get("asombro") == 3)
    asombros_2_o_mas = sum(1 for a in articulos if a.get("asombro", 0) >= 2)
    if asombros_3 <= 1 and asombros_2_o_mas <= 2:
        checks_ok += 1
    else:
        fallos.append(f"CHECK 4 FALLO: asombro inflado — {asombros_3} artículos con puntuación 3, {asombros_2_o_mas} con ≥2")

    # Check 5: analisis_general es específico (menciona algo concreto, > 40 palabras)
    if len(analisis.split()) >= 40 and analisis != "":
        checks_ok += 1
    else:
        fallos.append(f"CHECK 5 FALLO: analisis_general demasiado corto o vacío ({len(analisis.split())} palabras)")

    # Check 6: exactamente 1 o 2 artículos marcados como importante
    importantes = sum(1 for a in articulos if a.get("importante") is True)
    if 1 <= importantes <= 2:
        checks_ok += 1
    else:
        fallos.append(f"CHECK 6 FALLO: {importantes} artículos marcados como importante (debe ser 1 o 2)")

    # Check 7: artículo de cuervos (id=1) recibe asombro >= 2 (descubrimiento científico fascinante)
    if len(articulos) > 1 and articulos[1].get("asombro", 0) >= 2:
        checks_ok += 1
    else:
        val = articulos[1].get("asombro", 0) if len(articulos) > 1 else "N/A"
        fallos.append(f"CHECK 7 FALLO: cuervos debería tener asombro >= 2, tiene {val}")

    # Check 8: artículo del IPC (id=3) recibe asombro = 0 (noticia económica rutinaria)
    if len(articulos) > 3 and articulos[3].get("asombro", -1) == 0:
        checks_ok += 1
    else:
        val = articulos[3].get("asombro", "N/A") if len(articulos) > 3 else "N/A"
        fallos.append(f"CHECK 8 FALLO: IPC debería tener asombro = 0, tiene {val}")

    # Check 9: críticas no empiezan con frases genéricas
    frases_genericas = ["el artículo presenta", "este artículo", "el texto presenta", "el artículo ofrece", "la noticia presenta"]
    criticas_genericas = [
        i for i, a in enumerate(articulos)
        if any(a.get("critica", "").lower().startswith(f) for f in frases_genericas)
    ]
    if not criticas_genericas:
        checks_ok += 1
    else:
        fallos.append(f"CHECK 9 FALLO: críticas con frases genéricas en artículos {criticas_genericas}")

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
            model=CLAUDE_MODEL_ANALISIS,
            max_tokens=2048,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}],
        )
        texto = msg.content[0].text.strip()
        if texto.startswith("```"):
            texto = "\n".join(texto.splitlines()[1:-1]).strip()
        return json.loads(texto)
    except Exception as e:
        print(f"  ERROR: {e}")
        return None


# ---------------------------------------------------------------------------
# Main — ejecuta N runs y devuelve score medio
# ---------------------------------------------------------------------------

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
        print(f"    Run {i+1}: {score}/6")
    media = sum(scores) / len(scores) if scores else 0
    return media, todos_fallos


if __name__ == "__main__":
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    print(f"\nMidiendo prompt actual ({runs} runs)...")
    score, fallos = medir(PROMPT_TEMPLATE, runs)
    print(f"\n  Score medio: {score:.1f}/6")
    if fallos:
        print("\n  Fallos detectados:")
        for f in fallos:
            print(f"    · {f}")
    else:
        print("  OK - Todos los checks pasaron")
