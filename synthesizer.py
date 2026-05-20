"""
synthesizer.py — Agrupa artículos relacionados y sintetiza perspectivas cruzadas.

Estrategia de una sola llamada a Claude:
  1. Envía todos los artículos (id + fuente + título + resumen corto)
  2. Pide que detecte grupos que cubren el MISMO evento concreto
  3. Para cada grupo genera una síntesis que contrasta perspectivas
  4. Devuelve los grupos con referencias a los artículos originales

El resultado alimenta la pestaña "Síntesis" del digest HTML.
"""

import json
import time
import anthropic

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, IDIOMA_ANALISIS

# Máximo de artículos que se envían a Claude.
_MAX_ARTICULOS_SINTESIS = 120

_PROMPT = """
Eres un editor periodístico experto en análisis comparativo de medios.
Recibes una lista de artículos de distintas fuentes y debes:

1. AGRUPAR los artículos que traten el MISMO evento o hecho noticioso concreto.
   - Agrupa solo por HECHOS específicos, no por temas generales.
     Ejemplo correcto: "Aprobación de la ley X en el parlamento".
     Ejemplo incorrecto: "Política española".
   - Un grupo debe tener mínimo 2 artículos.
   - Si un artículo no encaja con ningún otro, omítelo.

2. Para cada grupo, redacta en {idioma} una SÍNTESIS que:
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
      "titulo": "Título claro y conciso de la historia",
      "sintesis": "Texto completo de la síntesis...",
      "ids": [0, 3, 7]
    }}
  ]
}}

Si ningún artículo está relacionado con otro, responde con {{"grupos": []}}.
"""


_REINTENTOS_MAX  = 3
_ESPERA_BASE_429 = 30
_ESPERA_BASE_5XX = 5


def _llamar_claude(prompt: str) -> dict | None:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    for intento in range(1, _REINTENTOS_MAX + 1):
        try:
            message = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=8192,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}],
            )
            texto = message.content[0].text.strip()
            if texto.startswith("```"):
                texto = "\n".join(texto.splitlines()[1:-1]).strip()
            return json.loads(texto)

        except anthropic.RateLimitError:
            if intento == _REINTENTOS_MAX:
                print(f"  ✗ Rate limit en síntesis — reintentos agotados")
                return None
            espera = _ESPERA_BASE_429 * (2 ** (intento - 1))
            print(f"  ⏳ Rate limit — esperando {espera}s (intento {intento}/{_REINTENTOS_MAX})...")
            time.sleep(espera)

        except anthropic.APIStatusError as e:
            if e.status_code >= 500:
                if intento == _REINTENTOS_MAX:
                    print(f"  ✗ Error {e.status_code} — reintentos agotados")
                    return None
                espera = _ESPERA_BASE_5XX * (2 ** (intento - 1))
                print(f"  ⏳ Error {e.status_code} — esperando {espera}s (intento {intento}/{_REINTENTOS_MAX})...")
                time.sleep(espera)
            else:
                print(f"  ✗ Error API {e.status_code}: {str(e)[:200]}")
                return None

        except json.JSONDecodeError as e:
            print(f"  ✗ JSON inválido en la respuesta: {e}")
            return None

        except Exception as e:
            print(f"  ✗ Error inesperado: {e}")
            return None

    return None


def sintetizar_noticias(
    noticias: dict[str, list[dict]],
    alternativas: dict[str, list[dict]] | None = None,
) -> list[dict]:
    """
    Detecta historias comunes entre artículos y genera síntesis cruzadas.

    Incluye tanto fuentes principales como alternativas para que la síntesis
    refleje también la diferencia entre medios mainstream y contrainformativos.

    Devuelve lista de grupos:
    [
        {
            "titulo":    str,
            "sintesis":  str,
            "articulos": [
                {
                    "fuente":       str,
                    "titulo":       str,
                    "enlace":       str,
                    "categoria":    str,
                    "sesgo_fuente": str,
                }
            ]
        }
    ]
    """
    todos: list[dict] = []

    for cat, arts in noticias.items():
        for a in arts:
            todos.append({**a, "_categoria": cat, "_alt": False})

    if alternativas:
        for cat, arts in alternativas.items():
            for a in arts:
                todos.append({**a, "_categoria": cat, "_alt": True})

    if not todos:
        return []

    if len(todos) > _MAX_ARTICULOS_SINTESIS:
        print(f"  ℹ Limitando a {_MAX_ARTICULOS_SINTESIS} artículos para síntesis "
              f"(de {len(todos)} totales)")
        todos = todos[:_MAX_ARTICULOS_SINTESIS]

    payload = [
        {
            "id":      i,
            "fuente":  a["fuente"],
            "titulo":  a["titulo"],
            "resumen": (a.get("resumen") or "")[:180],
        }
        for i, a in enumerate(todos)
    ]

    prompt = _PROMPT.format(
        idioma=IDIOMA_ANALISIS,
        articulos_json=json.dumps(payload, ensure_ascii=False, indent=2),
    )

    print(f"  → Analizando {len(todos)} artículos en busca de historias comunes...")
    resultado = _llamar_claude(prompt)

    if resultado is None:
        return []

    grupos_finales: list[dict] = []

    for grupo in resultado.get("grupos", []):
        ids = grupo.get("ids", [])
        articulos_grupo = []

        for i in ids:
            if 0 <= i < len(todos):
                a = todos[i]
                articulos_grupo.append({
                    "fuente":       a["fuente"],
                    "titulo":       a["titulo"],
                    "enlace":       a["enlace"],
                    "categoria":    a["_categoria"],
                    "sesgo_fuente": a.get("sesgo_fuente", "desconocido"),
                    "alt":          a["_alt"],
                })

        fuentes_unicas = {art["fuente"] for art in articulos_grupo}
        if len(fuentes_unicas) >= 2:
            grupos_finales.append({
                "titulo":    grupo.get("titulo", "Historia sin título"),
                "sintesis":  grupo.get("sintesis", ""),
                "articulos": articulos_grupo,
            })

    grupos_finales.sort(key=lambda g: len(g["articulos"]), reverse=True)

    print(f"  ✓ {len(grupos_finales)} historia(s) detectada(s)")
    return grupos_finales
