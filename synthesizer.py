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
import hashlib

from config import CLAUDE_MODEL, IDIOMA_ANALISIS
from article_cache import shared as _cache
from claude_client import llamar_claude

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
      "titulo": "Título con verbo activo que capture la tensión o el ángulo central de la historia",
      "sintesis": "Texto completo de la síntesis...",
      "ids": [0, 3, 7]
    }}
  ]
}}

Si ningún artículo está relacionado con otro, responde con {{"grupos": []}}.
"""


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

    # Comprobar caché antes de llamar a Claude
    _clave_cache = hashlib.md5(
        "|".join(sorted(a["enlace"] for a in todos)).encode()
    ).hexdigest()
    cached = _cache.get_sintesis(_clave_cache)
    if cached is not None:
        print(f"  ✓ Síntesis desde caché ({len(cached)} historia(s), 0 tokens)")
        return cached

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
    resultado = llamar_claude(prompt, model=CLAUDE_MODEL, max_tokens=4096, temperature=0.3)

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

    _cache.set_sintesis(_clave_cache, grupos_finales)
    _cache.guardar()
    print(f"  ✓ {len(grupos_finales)} historia(s) detectada(s)")
    return grupos_finales
