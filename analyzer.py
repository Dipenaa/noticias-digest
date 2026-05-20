"""
analyzer.py — Análisis de sesgo y crítica periodística con la API de Gemini.

Estrategia: en lugar de llamar a la API artículo por artículo (caro y lento),
enviamos todos los artículos de una categoría en una sola llamada y pedimos
una respuesta JSON estructurada.  Así el coste es O(categorías), no O(artículos).
"""

import json
import time
import requests

from config import GEMINI_API_KEY, GEMINI_MODEL, IDIOMA_ANALISIS


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

_GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
)

# Colores CSS para cada nivel de sesgo (compartidos con renderer.py)
COLORES_SESGO: dict[str, str] = {
    "izquierda":        "#3b82f6",  # azul
    "centro-izquierda": "#60a5fa",  # azul claro
    "centro":           "#6b7280",  # gris
    "centro-derecha":   "#f97316",  # naranja
    "derecha":          "#ef4444",  # rojo
    "desconocido":      "#9ca3af",  # gris claro
}

# Instrucción que se envía a Gemini.
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

_REINTENTOS_MAX  = 4      # intentos totales por llamada
_ESPERA_BASE_429 = 30     # segundos de espera inicial tras un 429
_ESPERA_BASE_5XX = 5      # segundos de espera inicial tras error de servidor


def _llamar_gemini(prompt: str) -> dict | None:
    """
    Envía un prompt a la API de Gemini y devuelve el dict parseado.
    Reintenta automáticamente con espera exponencial en 429 y errores 5xx.
    Devuelve None si se agotan los reintentos o hay un error no recuperable.
    """
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature":     0.2,
            "maxOutputTokens": 4096,
        },
    }

    for intento in range(1, _REINTENTOS_MAX + 1):
        try:
            resp = requests.post(_GEMINI_URL, json=payload, timeout=90)

            # 429 — cuota agotada: espera larga con backoff exponencial
            if resp.status_code == 429:
                if intento == _REINTENTOS_MAX:
                    print(f"  ✗ 429 cuota agotada — reintentos agotados ({_REINTENTOS_MAX})")
                    return None
                espera = _ESPERA_BASE_429 * (2 ** (intento - 1))  # 30 s, 60 s, 120 s
                print(f"  ⏳ 429 cuota agotada — esperando {espera} s (intento {intento}/{_REINTENTOS_MAX})...")
                time.sleep(espera)
                continue

            # 5xx — error de servidor: espera corta con backoff
            if resp.status_code >= 500:
                if intento == _REINTENTOS_MAX:
                    print(f"  ✗ Error {resp.status_code} — reintentos agotados")
                    return None
                espera = _ESPERA_BASE_5XX * (2 ** (intento - 1))  # 5 s, 10 s, 20 s
                print(f"  ⏳ Error {resp.status_code} — esperando {espera} s (intento {intento}/{_REINTENTOS_MAX})...")
                time.sleep(espera)
                continue

            resp.raise_for_status()

            texto = (
                resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                .strip()
            )

            # Gemini a veces envuelve el JSON en ```json ... ``` aunque le dijimos
            # que no lo hiciera; lo limpiamos por si acaso.
            if texto.startswith("```"):
                lineas = texto.splitlines()
                texto = "\n".join(lineas[1:-1]).strip()

            return json.loads(texto)

        except requests.exceptions.Timeout:
            if intento == _REINTENTOS_MAX:
                print("  ✗ Gemini tardó demasiado (timeout 90 s) — reintentos agotados")
                return None
            print(f"  ⏳ Timeout — reintentando ({intento}/{_REINTENTOS_MAX})...")
            time.sleep(_ESPERA_BASE_5XX * intento)
        except requests.exceptions.HTTPError as e:
            print(f"  ✗ Error HTTP {e.response.status_code}: {e.response.text[:300]}")
            return None
        except json.JSONDecodeError as e:
            print(f"  ✗ JSON inválido en la respuesta de Gemini: {e}")
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

    # Solo enviamos a Gemini los campos que necesita para analizar
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

    print(f"  → Enviando {len(articulos)} artículo(s) a Gemini...")
    resultado = _llamar_gemini(prompt)

    if resultado is None:
        # Si la API falla, devolvemos los artículos sin enriquecer
        for a in articulos:
            a["sesgo_ia"] = "desconocido"
            a["critica"]  = "No se pudo obtener análisis de IA."
        return articulos, "El análisis de IA no estuvo disponible para esta sección."

    # Enriquece cada artículo con los datos que devolvió Gemini
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

def analizar_todas_las_noticias(
    noticias: dict[str, list[dict]],
) -> tuple[dict[str, list[dict]], dict[str, str]]:
    """
    Analiza todas las categorías y devuelve:
        noticias_enriquecidas  → mismo dict pero con sesgo_ia y critica rellenos
        analisis_por_categoria → {categoría: texto_análisis_general}
    """
    analisis: dict[str, str] = {}

    for categoria, articulos in noticias.items():
        print(f"\n🤖 Analizando: {categoria}")
        articulos_enriquecidos, analisis_general = _analizar_categoria(articulos)
        noticias[categoria] = articulos_enriquecidos
        analisis[categoria] = analisis_general

    return noticias, analisis
