"""
analyzer.py — Análisis de sesgo y crítica periodística con la API de Claude.

Estrategia: en lugar de llamar a la API artículo por artículo (caro y lento),
enviamos todos los artículos de una categoría en una sola llamada y pedimos
una respuesta JSON estructurada.  Así el coste es O(categorías), no O(artículos).
"""

import json
import time
import anthropic
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, IDIOMA_ANALISIS


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

# Colores CSS para cada nivel de sesgo (compartidos con renderer.py)
COLORES_SESGO: dict[str, str] = {
    "izquierda":        "#3b82f6",  # azul
    "centro-izquierda": "#60a5fa",  # azul claro
    "centro":           "#6b7280",  # gris
    "centro-derecha":   "#f97316",  # naranja
    "derecha":          "#ef4444",  # rojo
    "desconocido":      "#9ca3af",  # gris claro
}

# Instrucción que se envía a Claude.
# {idioma} y {articulos_json} se rellenan en tiempo de ejecución.
_PROMPT = """
Eres un analista periodístico crítico e imparcial. Tu tarea es analizar \
los siguientes artículos de noticias y responder ÚNICAMENTE con JSON válido.

Para cada artículo, proporciona en {idioma}:
- "sesgo_ia": el sesgo ideológico que percibes en el ARTÍCULO (no en el medio).
  Usa exactamente uno de estos valores:
  "izquierda" | "centro-izquierda" | "centro" | "centro-derecha" | "derecha" | "desconocido"
- "critica": 1-2 oraciones señalando el ángulo, lo que se omite, el framing,
  o lo que merece cuestionarse. Sé concreto, no genérico.
- "importante": true si este artículo es uno de los 2 más relevantes e impactantes
  del lote (noticia de primer orden, alto impacto público), false en todos los demás.
  Marca exactamente 1 o 2 por lote, nunca más.
- "sentimiento": el tono emocional predominante del artículo.
  Usa exactamente uno de: "alarmista" | "neutral" | "optimista"
  alarmista = urgencia, miedo, catastrofismo, indignación exagerada.
  optimista  = esperanza, progreso, logro, solución destacada.
  neutral    = informativo, factual, sin carga emocional marcada.

Además proporciona:
- "analisis_general": un párrafo de análisis crítico del conjunto de noticias
  de esta sección. ¿Qué historia domina? ¿Qué perspectivas faltan?
  ¿Qué patrones o silencios ves?

Artículos (JSON):
{articulos_json}

Responde ÚNICAMENTE con este JSON (sin bloques de código, sin texto extra):
{{
  "articulos": [
    {{"sesgo_ia": "...", "critica": "...", "importante": false, "sentimiento": "neutral"}},
    ...
  ],
  "analisis_general": "..."
}}
"""


# ---------------------------------------------------------------------------
# Llamada a la API
# ---------------------------------------------------------------------------

_REINTENTOS_MAX  = 4
_ESPERA_BASE_429 = 30   # segundos de espera inicial tras rate limit
_ESPERA_BASE_5XX = 5    # segundos de espera inicial tras error de servidor


def _llamar_claude(prompt: str) -> dict | None:
    """
    Envía un prompt a la API de Claude y devuelve el dict parseado.
    Reintenta con espera exponencial en rate limit y errores 5xx.
    Devuelve None si se agotan los reintentos o hay un error no recuperable.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    for intento in range(1, _REINTENTOS_MAX + 1):
        try:
            message = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=4096,
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}],
            )
            texto = message.content[0].text.strip()

            if texto.startswith("```"):
                lineas = texto.splitlines()
                texto = "\n".join(lineas[1:-1]).strip()

            return json.loads(texto)

        except anthropic.RateLimitError:
            if intento == _REINTENTOS_MAX:
                print(f"  ✗ Rate limit — reintentos agotados ({_REINTENTOS_MAX})")
                return None
            espera = _ESPERA_BASE_429 * (2 ** (intento - 1))
            print(f"  ⏳ Rate limit — esperando {espera} s (intento {intento}/{_REINTENTOS_MAX})...")
            time.sleep(espera)

        except anthropic.APIStatusError as e:
            if e.status_code >= 500:
                if intento == _REINTENTOS_MAX:
                    print(f"  ✗ Error {e.status_code} — reintentos agotados")
                    return None
                espera = _ESPERA_BASE_5XX * (2 ** (intento - 1))
                print(f"  ⏳ Error {e.status_code} — esperando {espera} s (intento {intento}/{_REINTENTOS_MAX})...")
                time.sleep(espera)
            else:
                print(f"  ✗ Error API {e.status_code}: {str(e)[:300]}")
                return None

        except json.JSONDecodeError as e:
            print(f"  ✗ JSON inválido en la respuesta de Claude: {e}")
            return None

        except Exception as e:
            print(f"  ✗ Error inesperado: {e}")
            return None

    return None


# ---------------------------------------------------------------------------
# Análisis por categoría
# ---------------------------------------------------------------------------

def _analizar_categoria(
    articulos: list[dict],
) -> tuple[list[dict], str]:
    """
    Analiza todos los artículos de una categoría en una sola llamada.

    Devuelve:
        (articulos_enriquecidos, texto_analisis_general)
    """
    if not articulos:
        return articulos, ""

    payload_articulos = [
        {
            "id":      i,
            "titulo":  a["titulo"],
            "fuente":  a["fuente"],
            "resumen": a["resumen"],
        }
        for i, a in enumerate(articulos)
    ]

    prompt = _PROMPT.format(
        idioma=IDIOMA_ANALISIS,
        articulos_json=json.dumps(payload_articulos, ensure_ascii=False, indent=2),
    )

    print(f"  → Enviando {len(articulos)} artículo(s) a Claude...")
    resultado = _llamar_claude(prompt)

    if resultado is None:
        for a in articulos:
            a["sesgo_ia"] = "desconocido"
            a["critica"]  = "No se pudo obtener análisis de IA."
        return articulos, "El análisis de IA no estuvo disponible para esta sección."

    analisis_articulos = resultado.get("articulos", [])
    for i, articulo in enumerate(articulos):
        datos_ia = analisis_articulos[i] if i < len(analisis_articulos) else {}
        articulo["sesgo_ia"]    = datos_ia.get("sesgo_ia", "desconocido")
        articulo["critica"]     = datos_ia.get("critica", "")
        articulo["importante"]  = bool(datos_ia.get("importante", False))
        articulo["sentimiento"] = datos_ia.get("sentimiento", "neutral")

    return articulos, resultado.get("analisis_general", "")


# ---------------------------------------------------------------------------
# Punto de entrada público
# ---------------------------------------------------------------------------

_MAX_WORKERS_ANALYSIS = 3  # categorías analizadas en paralelo (respeta rate limits)


def analizar_todas_las_noticias(
    noticias: dict[str, list[dict]],
) -> tuple[dict[str, list[dict]], dict[str, str]]:
    """
    Analiza todas las categorías en paralelo (hasta 3 a la vez) y devuelve:
        noticias_enriquecidas  → mismo dict pero con sesgo_ia y critica rellenos
        analisis_por_categoria → {categoría: texto_análisis_general}
    """
    analisis: dict[str, str] = {}

    def _tarea(categoria: str, articulos: list[dict]):
        print(f"\n🤖 Analizando: {categoria}")
        return categoria, _analizar_categoria(articulos)

    with ThreadPoolExecutor(max_workers=_MAX_WORKERS_ANALYSIS) as executor:
        futures = {
            executor.submit(_tarea, cat, arts): cat
            for cat, arts in noticias.items()
        }
        for future in as_completed(futures):
            cat = futures[future]
            try:
                categoria, (arts_enriquecidos, analisis_general) = future.result()
                noticias[categoria] = arts_enriquecidos
                analisis[categoria] = analisis_general
            except Exception as e:
                print(f"  ✗ Error inesperado analizando {cat}: {e}")
                analisis[cat] = ""

    return noticias, analisis
