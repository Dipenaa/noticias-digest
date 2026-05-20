"""
analyzer.py — Análisis de sesgo y crítica periodística con la API de Claude.

Estrategia: en lugar de llamar a la API artículo por artículo (caro y lento),
enviamos todos los artículos de una categoría en una sola llamada y pedimos
una respuesta JSON estructurada.  Así el coste es O(categorías), no O(artículos).

Optimizaciones de coste:
- Caché persistente: artículos ya analizados no se re-envían a Claude (TTL 24h).
- Modelo Haiku para análisis masivo (≈20× más barato que Sonnet).
- Sonnet se reserva para la síntesis cruzada en synthesizer.py.
"""

import json
import time
import anthropic
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL_ANALISIS, IDIOMA_ANALISIS
from article_cache import shared as _cache


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

COLORES_SESGO: dict[str, str] = {
    "izquierda":        "#3b82f6",
    "centro-izquierda": "#60a5fa",
    "centro":           "#6b7280",
    "centro-derecha":   "#f97316",
    "derecha":          "#ef4444",
    "desconocido":      "#9ca3af",
}

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
_ESPERA_BASE_429 = 30
_ESPERA_BASE_5XX = 5


def _llamar_claude(prompt: str) -> dict | None:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    for intento in range(1, _REINTENTOS_MAX + 1):
        try:
            message = client.messages.create(
                model=CLAUDE_MODEL_ANALISIS,
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
# Análisis por categoría (con caché)
# ---------------------------------------------------------------------------

def _analizar_categoria(
    categoria: str,
    articulos: list[dict],
) -> tuple[list[dict], str]:
    if not articulos:
        return articulos, ""

    # Separar artículos nuevos de los ya cacheados
    nuevos_idx: list[int] = []
    for i, a in enumerate(articulos):
        cached = _cache.get_articulo(a["enlace"])
        if cached:
            a["sesgo_ia"]    = cached["sesgo_ia"]
            a["critica"]     = cached["critica"]
            a["sentimiento"] = cached["sentimiento"]
            a["importante"]  = False  # la importancia es relativa al ciclo actual
        else:
            nuevos_idx.append(i)

    if not nuevos_idx:
        analisis_general = _cache.get_analisis_general(categoria) or ""
        print(f"  ✓ {categoria}: {len(articulos)} artículo(s) desde caché (0 tokens)")
        return articulos, analisis_general

    nuevos = [articulos[i] for i in nuevos_idx]
    print(f"  → {categoria}: {len(nuevos)} nuevos / {len(articulos)} totales")

    payload = [
        {
            "id":      j,
            "titulo":  a["titulo"],
            "fuente":  a["fuente"],
            "resumen": a["resumen"],
        }
        for j, a in enumerate(nuevos)
    ]

    prompt = _PROMPT.format(
        idioma=IDIOMA_ANALISIS,
        articulos_json=json.dumps(payload, ensure_ascii=False, indent=2),
    )

    print(f"  → Enviando {len(nuevos)} artículo(s) a Claude Haiku...")
    resultado = _llamar_claude(prompt)

    if resultado is None:
        for i in nuevos_idx:
            articulos[i]["sesgo_ia"]    = "desconocido"
            articulos[i]["critica"]     = "No se pudo obtener análisis de IA."
            articulos[i]["importante"]  = False
            articulos[i]["sentimiento"] = "neutral"
        return articulos, _cache.get_analisis_general(categoria) or \
               "El análisis de IA no estuvo disponible para esta sección."

    analisis_articulos = resultado.get("articulos", [])
    for j, orig_idx in enumerate(nuevos_idx):
        datos_ia = analisis_articulos[j] if j < len(analisis_articulos) else {}
        a = articulos[orig_idx]
        a["sesgo_ia"]    = datos_ia.get("sesgo_ia", "desconocido")
        a["critica"]     = datos_ia.get("critica", "")
        a["importante"]  = bool(datos_ia.get("importante", False))
        a["sentimiento"] = datos_ia.get("sentimiento", "neutral")

        _cache.set_articulo(a["enlace"], {
            "sesgo_ia":    a["sesgo_ia"],
            "critica":     a["critica"],
            "sentimiento": a["sentimiento"],
        })

    analisis_general = resultado.get("analisis_general", "")
    if analisis_general:
        _cache.set_analisis_general(categoria, analisis_general)
    else:
        analisis_general = _cache.get_analisis_general(categoria) or ""

    return articulos, analisis_general


# ---------------------------------------------------------------------------
# Punto de entrada público
# ---------------------------------------------------------------------------

_MAX_WORKERS_ANALYSIS = 3


def analizar_todas_las_noticias(
    noticias: dict[str, list[dict]],
) -> tuple[dict[str, list[dict]], dict[str, str]]:
    analisis: dict[str, str] = {}

    def _tarea(categoria: str, articulos: list[dict]):
        print(f"\n🤖 Analizando: {categoria}")
        return categoria, _analizar_categoria(categoria, articulos)

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

    _cache.guardar()
    stats = _cache.stats()
    print(f"\n  💾 Caché: {stats['articulos_cacheados']} artículos guardados")

    return noticias, analisis
