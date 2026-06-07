"""Pestaña Todas — secciones independientes, título ocupa 2 filas."""

import random
from datetime import date, datetime

from renderer.components.tarjeta import tarjeta


def _score(art: dict) -> int:
    s = int(art.get('asombro') or 0) * 3
    s += 2 if art.get('importante') else 0
    s += 1 if art.get('destacado') else 0
    try:
        age = (date.today() - datetime.strptime(art.get('fecha', '2000-01-01'), '%Y-%m-%d').date()).days
        s += max(0, 4 - age)
    except Exception:
        pass
    return s


TAB_ID    = "todas"
TAB_LABEL = "Todas las noticias"
TAB_ICON  = "📰"


def nav(categorias: list[str]) -> str:
    links = "".join(
        f'<a href="#{cat.lower().replace(" ", "-")}">{cat}</a>'
        for cat in categorias
    )
    return f'<nav id="cat-nav">{links}</nav>'


def _seccion(categoria: str, articulos: list[dict],
             verificados: frozenset = frozenset()) -> str:
    if not articulos:
        return ''

    anchor = categoria.lower().replace(' ', '-')
    ordenados = sorted(articulos, key=_score, reverse=True)

    # Título siempre primero: ocupa 2 filas con grid-row: span 2
    # Las noticias fluyen a su derecha y debajo (grid-auto-flow: dense)
    titulo = (
        f'<div class="grid-titulo-celda" data-titulo-pos="0">'
        f'<h2 class="seccion-titulo">{categoria}</h2>'
        f'</div>'
    )
    items = [titulo] + [tarjeta(a, verificados, i) for i, a in enumerate(ordenados)]

    return (
        f'<section id="{anchor}" class="seccion">'
        f'<div class="grid">{"".join(items)}</div>'
        f'</section>'
    )


def render(noticias: dict[str, list[dict]],
           analisis: dict[str, str],
           verificados: frozenset = frozenset(), **_) -> str:
    return '\n'.join(
        _seccion(cat, arts, verificados)
        for cat, arts in noticias.items()
        if arts
    )
