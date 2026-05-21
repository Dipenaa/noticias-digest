"""
fetcher.py — Descarga y parsea feeds RSS en paralelo.

Responsabilidad única: dado el dict FUENTES de config.py,
devuelve un dict {categoría: [artículos]} listos para analizar.
"""

import re
import threading
import feedparser
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from config import FUENTES, FUENTES_ALTERNATIVAS, MAX_ARTICULOS_POR_FUENTE

_MAX_WORKERS = 12

_fuentes_fallidas: list[str] = []
_lock_fallidas = threading.Lock()

# ---------------------------------------------------------------------------
# Filtro de ruido — títulos que contienen estas palabras se descartan
# ---------------------------------------------------------------------------

_PALABRAS_RUIDO = {
    # Deportes
    "fútbol", "futbol", "gol", "liga", "champions", "mundial", "baloncesto",
    "tenis", "moto gp", "formula 1", "f1", "ciclismo", "atletismo", "nadal",
    "real madrid", "barcelona", "atlético", "atletico", "nba", "eurocopa",
    # Famosos / televisión / corazón
    "celebrities", "celebrity", "famoso", "famosa", "cantante", "actor",
    "actriz", "influencer", "reality", "gran hermano", "supervivientes",
    "masterchef", "got talent", "eurovisión", "eurovision", "boda real",
    "alfombra roja", "look", "bikini", "novio", "novia", "ruptura",
    # Sucesos menores / crónica negra local
    "accidente de tráfico", "atropello", "incendio forestal", "herido leve",
    "detenido por", "arrestado por", "robo en", "asalto a",
    # Tiempo y lotería
    "previsión del tiempo", "tiempo en", "ola de calor", "borrasca",
    "lotería", "euromillones", "bonoloto", "primitiva", "cupón",
    # Horóscopo / entretenimiento vacío
    "horóscopo", "horoscopo", "tarot", "receta", "recetas de",
    "los mejores restaurantes", "destinos para",
}


def _es_ruido(titulo: str) -> bool:
    t = titulo.lower()
    return any(p in t for p in _PALABRAS_RUIDO)


def get_fuentes_fallidas() -> list[str]:
    with _lock_fallidas:
        return list(_fuentes_fallidas)


# ---------------------------------------------------------------------------
# Utilidades de limpieza
# ---------------------------------------------------------------------------

def _quitar_html(texto: str) -> str:
    return re.sub(r"<[^>]+>", "", texto or "").strip()


def _formatear_fecha(entry) -> str:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            dt = datetime(*entry.published_parsed[:6])
            return dt.strftime("%d/%m/%Y %H:%M")
        except Exception:
            pass
    return "Fecha desconocida"


# ---------------------------------------------------------------------------
# Lógica de descarga (una fuente)
# ---------------------------------------------------------------------------

def _articulos_de_fuente(fuente: dict) -> list[dict]:
    try:
        feed = feedparser.parse(fuente["url"])

        if not feed.entries:
            print(f"  ⚠ Sin artículos en {fuente['nombre']}")
            with _lock_fallidas:
                _fuentes_fallidas.append(fuente["nombre"])
            return []

        articulos = []
        # Leemos más entradas de las necesarias para poder filtrar ruido
        for entry in feed.entries[:MAX_ARTICULOS_POR_FUENTE * 3]:
            titulo = entry.get("title", "Sin título").strip()

            if _es_ruido(titulo):
                continue

            resumen_crudo = entry.get("summary", "") or entry.get("description", "")
            resumen = _quitar_html(resumen_crudo)

            articulos.append({
                "titulo":       titulo,
                "enlace":       entry.get("link", "#"),
                "resumen":      resumen[:500],
                "fuente":       fuente["nombre"],
                "sesgo_fuente": fuente["sesgo"],
                "fecha":        _formatear_fecha(entry),
                "sesgo_ia":     None,
                "critica":      None,
            })

            if len(articulos) >= MAX_ARTICULOS_POR_FUENTE:
                break

        print(f"  ✓ {fuente['nombre']}: {len(articulos)} artículo(s)")
        return articulos

    except Exception as e:
        print(f"  ✗ {fuente['nombre']}: {e}")
        with _lock_fallidas:
            _fuentes_fallidas.append(fuente["nombre"])
        return []


# ---------------------------------------------------------------------------
# Punto de entrada público
# ---------------------------------------------------------------------------

def obtener_todas_las_noticias(
    fuentes_dict: dict | None = None,
) -> dict[str, list[dict]]:
    if fuentes_dict is None:
        fuentes_dict = FUENTES

    with _lock_fallidas:
        _fuentes_fallidas.clear()

    resultado: dict[str, list[dict]] = {cat: [] for cat in fuentes_dict}
    tareas = [
        (cat, fuente)
        for cat, fuentes in fuentes_dict.items()
        for fuente in fuentes
    ]

    print(f"  Descargando {len(tareas)} feed(s) en paralelo ({_MAX_WORKERS} workers)...")

    with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as executor:
        future_map = {
            executor.submit(_articulos_de_fuente, fuente): (cat, fuente)
            for cat, fuente in tareas
        }
        for future in as_completed(future_map):
            cat, fuente = future_map[future]
            try:
                arts = future.result()
                resultado[cat].extend(arts)
            except Exception as e:
                print(f"  ✗ Error inesperado en {fuente['nombre']}: {e}")

    # Deduplicar por URL
    total_antes = sum(len(v) for v in resultado.values())
    for cat in resultado:
        vistos: set[str] = set()
        unicos = []
        for a in resultado[cat]:
            if a["enlace"] not in vistos:
                vistos.add(a["enlace"])
                unicos.append(a)
        resultado[cat] = unicos
    total_despues = sum(len(v) for v in resultado.values())
    if total_antes != total_despues:
        print(f"  ℹ Deduplicación: {total_antes - total_despues} duplicado(s) eliminado(s)")

    return resultado


def obtener_noticias_alternativas() -> dict[str, list[dict]]:
    return obtener_todas_las_noticias(FUENTES_ALTERNATIVAS)
