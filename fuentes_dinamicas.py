"""
fuentes_dinamicas.py — Ángulos extra por tema vía Google News RSS (B-lite).

Para cada historia del día, trae perspectivas de medios de todo el mundo que
cubren ESA noticia, sin coste de IA (Google News es RSS gratuito). El sesgo de
cada medio sale de sesgo_lookup.py; los desconocidos se muestran sin posición
en el espectro.

Uso típico (desde el pipeline, tras la síntesis):
    extra = buscar_angulos("aprobación de los presupuestos", fuentes_excluidas={"El País","ABC"})
"""

import urllib.parse

import feedparser

from sesgo_lookup import sesgo_de_fuente

_GNEWS = "https://news.google.com/rss/search?q={q}&hl=es-419&gl=ES&ceid=ES:es"
_TIMEOUT = 8


def _limpiar_titulo(titulo: str, fuente: str) -> str:
    """Google News añade ' - Medio' al final del título; lo quitamos."""
    if fuente and titulo.endswith(f" - {fuente}"):
        return titulo[: -len(fuente) - 3].strip()
    return titulo.strip()


def _norm(s: str) -> str:
    return s.lower().strip().rstrip("|").strip()


def buscar_angulos(query: str, n: int = 3,
                   fuentes_excluidas: frozenset = frozenset()) -> list[dict]:
    """
    Busca en Google News medios que cubren `query` y devuelve hasta `n`
    perspectivas de fuentes NUEVAS (una por medio), con su sesgo estimado.
    """
    if not query.strip():
        return []
    url = _GNEWS.format(q=urllib.parse.quote(query))
    try:
        feed = feedparser.parse(url)
    except Exception:
        return []

    excl = {_norm(f) for f in fuentes_excluidas}
    vistos: set[str] = set()
    salida: list[dict] = []

    for e in feed.entries:
        fuente = ((e.get("source") or {}).get("title") or "").strip()
        if not fuente:
            continue
        clave = _norm(fuente)
        if clave in vistos:
            continue
        # excluir medios que ya están en el grupo (por coincidencia parcial)
        if any(ex in clave or clave in ex for ex in excl if ex):
            continue
        vistos.add(clave)
        salida.append({
            "fuente": fuente,
            "titulo": _limpiar_titulo(e.get("title", ""), fuente),
            "enlace": e.get("link", ""),
            "fecha": (e.get("published", "") or "")[:16],
            "sesgo_fuente": sesgo_de_fuente(fuente),
            "_extra": True,
        })
        if len(salida) >= n:
            break
    return salida


def enriquecer_grupos(grupos: list[dict], max_grupos: int = 4,
                      por_grupo: int = 3) -> list[dict]:
    """
    Añade `perspectivas_extra` a los primeros `max_grupos` grupos de síntesis,
    excluyendo los medios que ya aparecen en cada grupo. Modifica in situ y
    devuelve la lista. Pensado para llamarse tras sintetizar_noticias().
    """
    for grupo in grupos[:max_grupos]:
        ya = {a.get("fuente", "") for a in grupo.get("articulos", [])}
        extra = buscar_angulos(
            grupo.get("titulo", ""),
            n=por_grupo,
            fuentes_excluidas=frozenset(ya),
        )
        if extra:
            grupo["perspectivas_extra"] = extra
    return grupos
