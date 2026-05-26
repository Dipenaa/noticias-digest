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
import re

from config import CLAUDE_MODEL, IDIOMA_ANALISIS
from article_cache import shared as _cache
from claude_client import llamar_claude

# Tope de artículos candidatos que se mandan a Claude (tras el pre-filtro).
_MAX_ARTICULOS_SINTESIS = 60

# Palabras vacías en español (no sirven para detectar similitud temática).
_STOPWORDS = frozenset("""
a al algo ante año así aunque bajo bien como con cual cuando de del desde donde
durante el ella ellos en entre era es ese eso está este fue gran había han hay
hasta he hizo incluso ja la las le les lo los más me mi mismo muy ni no nos o
para pero poco por que quien se se ser si sin sobre su sus también tan te toda
todo tras tu un una uno unas unos va ya yo
""".split())


def _palabras_clave(titulo: str) -> frozenset[str]:
    """Extrae palabras significativas de un título (≥4 chars, no stopwords)."""
    palabras = re.findall(r"[a-záéíóúüñ]{4,}", titulo.lower())
    return frozenset(p for p in palabras if p not in _STOPWORDS)


def _pre_filtrar_candidatos(todos: list[dict]) -> list[dict]:
    """
    Devuelve solo los artículos que comparten ≥2 palabras clave con al menos
    otro artículo de DISTINTA fuente. El resto son temas únicos y no producirán
    grupos en síntesis — no tiene sentido mandárselos a Claude.
    """
    claves = [_palabras_clave(a.get("titulo", "")) for a in todos]
    fuentes = [a.get("fuente", "") for a in todos]
    n = len(todos)
    tiene_par = [False] * n

    for i in range(n):
        if not claves[i]:
            continue
        for j in range(i + 1, n):
            if fuentes[i] == fuentes[j]:
                continue  # misma fuente no cuenta
            if len(claves[i] & claves[j]) >= 2:
                tiene_par[i] = True
                tiene_par[j] = True

    return [a for a, ok in zip(todos, tiene_par) if ok]

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

    # Pre-filtro local: solo artículos con ≥2 palabras clave en común con otro
    # artículo de distinta fuente. Evita mandar a Claude temas únicos.
    total_antes = len(todos)
    todos = _pre_filtrar_candidatos(todos)
    if not todos:
        print(f"  ℹ Pre-filtro: 0 candidatos de {total_antes} — ningún tema compartido")
        return []

    if len(todos) > _MAX_ARTICULOS_SINTESIS:
        todos = todos[:_MAX_ARTICULOS_SINTESIS]

    print(f"  ℹ Pre-filtro: {len(todos)} candidatos de {total_antes} artículos totales")

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

    print(f"  → Enviando {len(todos)} candidatos a Claude para síntesis...")
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
