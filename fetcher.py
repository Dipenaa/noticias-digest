"""
fetcher.py — Descarga y parsea feeds RSS en paralelo.

Responsabilidad única: dado el dict FUENTES de config.py,
devuelve un dict {categoría: [lista de artículos]} listos para analizar.
"""

import re
import feedparser
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from config import FUENTES, FUENTES_ALTERNATIVAS, MAX_ARTICULOS_POR_FUENTE

_MAX_WORKERS = 12  # feeds descargados en paralelo


# ---------------------------------------------------------------------------
# Utilidades de limpieza
# ---------------------------------------------------------------------------

def _quitar_html(texto: str) -> str:
    """Elimina etiquetas HTML de un texto plano."""
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
    """
    Descarga el feed RSS de una fuente y devuelve artículos normalizados.

    Cada artículo tiene estos campos:
      titulo, enlace, resumen, fuente, sesgo_fuente, fecha
      sesgo_ia, critica → se rellenan en analyzer.py (aquí quedan en None)
    """
    try:
        feed = feedparser.parse(fuente["url"])

        if not feed.entries:
            print(f"  ⚠ Sin artículos en {fuente['nombre']} "
                  f"(¿feed caído o URL incorrecta?)")
            return []

        articulos = []
        for entry in feed.entries[:MAX_ARTICULOS_POR_FUENTE]:
            resumen_crudo = entry.get("summary", "") or entry.get("description", "")
            resumen = _quitar_html(resumen_crudo)

            articulos.append({
                "titulo":       entry.get("title", "Sin título").strip(),
                "enlace":       entry.get("link", "#"),
                "resumen":      resumen[:500],
                "fuente":       fuente["nombre"],
                "sesgo_fuente": fuente["sesgo"],
                "fecha":        _formatear_fecha(entry),
                "sesgo_ia":     None,
                "critica":      None,
            })

        print(f"  ✓ {fuente['nombre']}: {len(articulos)} artículo(s)")
        return articulos

    except Exception as e:
        print(f"  ✗ {fuente['nombre']}: {e}")
        return []


# ---------------------------------------------------------------------------
# Punto de entrada público
# ---------------------------------------------------------------------------

def obtener_todas_las_noticias(
    fuentes_dict: dict | None = None,
) -> dict[str, list[dict]]:
    """
    Descarga artículos de todas las categorías en paralelo.

    Parámetros:
        fuentes_dict — dict {categoría: [fuentes]}. Si es None usa FUENTES.

    Devuelve {categoría: [artículos]}.
    """
    if fuentes_dict is None:
        fuentes_dict = FUENTES

    # Preserva el orden de categorías; los artículos dentro de cada categoría
    # llegan en orden de as_completed, pero eso es aceptable.
    resultado: dict[str, list[dict]] = {cat: [] for cat in fuentes_dict}
    tareas = [
        (cat, fuente)
        for cat, fuentes in fuentes_dict.items()
        for fuente in fuentes
    ]

    total = len(tareas)
    print(f"  Descargando {total} feed(s) en paralelo ({_MAX_WORKERS} workers)...")

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

    return resultado


def obtener_noticias_alternativas() -> dict[str, list[dict]]:
    """Atajo para descargar las fuentes de FUENTES_ALTERNATIVAS."""
    return obtener_todas_las_noticias(FUENTES_ALTERNATIVAS)
