"""
analyzer.py — Análisis de sesgo y crítica periodística con Claude Haiku.

Una llamada por categoría (no por artículo). Coste: O(categorías), no O(artículos).
Optimizaciones:
- Caché Redis/disco: artículos ya analizados no van a Claude (TTL 24h).
- Prompt caching: las instrucciones del sistema se cachean entre llamadas (~80% menos tokens).
- Haiku: 20× más barato que Sonnet para análisis masivo.
- 5 categorías en paralelo.
"""

import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import IDIOMA_ANALISIS
from article_cache import shared as _cache
from claude_client import llamar_claude


COLORES_SESGO: dict[str, str] = {
    "izquierda":        "#3b82f6",
    "centro-izquierda": "#60a5fa",
    "centro":           "#6b7280",
    "centro-derecha":   "#f97316",
    "derecha":          "#ef4444",
    "desconocido":      "#9ca3af",
}

# System prompt — se cachea entre llamadas de la misma generación
_SYSTEM = """Eres un analista periodístico crítico e imparcial. Responde ÚNICAMENTE con JSON válido.

Para cada artículo del array, devuelve en {idioma}:
- "sesgo_ia": sesgo del ARTÍCULO (no del medio). Valores: "izquierda"|"centro-izquierda"|"centro"|"centro-derecha"|"derecha"|"desconocido"
- "critica": 1-2 frases concretas sobre el ángulo, omisiones o framing. No genérico.
- "importante": true solo para los 1-2 artículos más relevantes del lote (alto impacto público). false en el resto.
- "sentimiento": "alarmista"|"neutral"|"optimista"
- "asombro": 0-3. ¿Amplía genuinamente la comprensión del mundo? 0=rutinario, 1=algo interesante, 2=fascinante, 3=excepcional. Sé exigente: máximo 1-2 artículos con 2+ por lote.
- "asombro_razon": si asombro>=2, frase de 15-25 palabras explicando por qué. Si no, null.

Además: "analisis_general": párrafo crítico del conjunto. ¿Qué domina? ¿Qué falta? ¿Qué patrones ves?"""

_USER_TMPL = """Artículos:
{articulos_json}

Responde con este JSON exacto:
{{"articulos":[{{"sesgo_ia":"...","critica":"...","importante":false,"sentimiento":"neutral","asombro":0,"asombro_razon":null}}],"analisis_general":"..."}}"""

_MAX_WORKERS_ANALYSIS = 5


def _analizar_categoria(categoria: str, articulos: list[dict]) -> tuple[list[dict], str]:
    if not articulos:
        return articulos, ""

    nuevos_idx: list[int] = []
    for i, a in enumerate(articulos):
        cached = _cache.get_articulo(a["enlace"])
        if cached:
            a["sesgo_ia"]      = cached["sesgo_ia"]
            a["critica"]       = cached["critica"]
            a["sentimiento"]   = cached["sentimiento"]
            a["asombro"]       = cached.get("asombro", 0)
            a["asombro_razon"] = cached.get("asombro_razon")
            a["importante"]    = False
        else:
            nuevos_idx.append(i)

    if not nuevos_idx:
        analisis_general = _cache.get_analisis_general(categoria) or ""
        print(f"  ✓ {categoria}: {len(articulos)} artículo(s) desde caché (0 tokens)")
        return articulos, analisis_general

    nuevos = [articulos[i] for i in nuevos_idx]
    print(f"  → {categoria}: {len(nuevos)} nuevos / {len(articulos)} totales")

    payload = [
        {"id": j, "titulo": a["titulo"], "fuente": a["fuente"], "resumen": (a.get("resumen") or "")[:150]}
        for j, a in enumerate(nuevos)
    ]

    system  = _SYSTEM.format(idioma=IDIOMA_ANALISIS)
    user    = _USER_TMPL.format(articulos_json=json.dumps(payload, ensure_ascii=False))
    resultado = llamar_claude(user, system=system, max_tokens=1024, cache_system=True)

    if resultado is None:
        for i in nuevos_idx:
            articulos[i].update({"sesgo_ia": "desconocido", "critica": "", "importante": False,
                                  "sentimiento": "neutral", "asombro": 0, "asombro_razon": None})
        return articulos, _cache.get_analisis_general(categoria) or ""

    for j, orig_idx in enumerate(nuevos_idx):
        datos = (resultado.get("articulos") or [])[j] if j < len(resultado.get("articulos") or []) else {}
        a = articulos[orig_idx]
        a["sesgo_ia"]      = datos.get("sesgo_ia", "desconocido")
        a["critica"]       = datos.get("critica", "")
        a["importante"]    = bool(datos.get("importante", False))
        a["sentimiento"]   = datos.get("sentimiento", "neutral")
        a["asombro"]       = int(datos.get("asombro") or 0)
        a["asombro_razon"] = datos.get("asombro_razon") or None
        _cache.set_articulo(a["enlace"], {
            "sesgo_ia": a["sesgo_ia"], "critica": a["critica"],
            "sentimiento": a["sentimiento"], "asombro": a["asombro"],
            "asombro_razon": a["asombro_razon"],
        })

    analisis_general = resultado.get("analisis_general", "")
    if analisis_general:
        _cache.set_analisis_general(categoria, analisis_general)
    else:
        analisis_general = _cache.get_analisis_general(categoria) or ""

    return articulos, analisis_general


def analizar_todas_las_noticias(
    noticias: dict[str, list[dict]],
) -> tuple[dict[str, list[dict]], dict[str, str]]:
    analisis: dict[str, str] = {}

    def _tarea(categoria, articulos):
        print(f"\n🤖 Analizando: {categoria}")
        return categoria, _analizar_categoria(categoria, articulos)

    with ThreadPoolExecutor(max_workers=_MAX_WORKERS_ANALYSIS) as executor:
        futures = {executor.submit(_tarea, cat, arts): cat for cat, arts in noticias.items()}
        for future in as_completed(futures):
            cat = futures[future]
            try:
                categoria, (arts, ag) = future.result()
                noticias[categoria] = arts
                analisis[categoria] = ag
            except Exception as e:
                print(f"  ✗ Error analizando {cat}: {e}")
                analisis[cat] = ""

    _cache.guardar()
    stats = _cache.stats()
    print(f"\n  💾 Caché: {stats['articulos_cacheados']} artículos ({stats['backend']})")
    return noticias, analisis
