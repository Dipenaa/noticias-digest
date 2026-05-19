"""
fetcher.py — Descarga y parsea feeds RSS.

Responsabilidad única: dado el dict FUENTES de config.py,
devuelve un dict {categoría: [lista de artículos]} listos para analizar.
"""

import re
import time
import feedparser
from datetime import datetime

from config import FUENTES, FUENTES_ALTERNATIVAS, MAX_ARTICULOS_POR_FUENTE


# ---------------------------------------------------------------------------
# Utilidades de limpieza
# ---------------------------------------------------------------------------

def _quitar_html(texto: str) -> str:
    """Elimina etiquetas HTML de un texto plano."""
    return re.sub(r"<[^>]+>", "", texto or "").strip()


def _formatear_fecha(entry) -> str:
    """
    Extrae la fecha de publicación de un entry de feedparser.
    feedparser la expone como una tupla de tiempo en .published_parsed.
    """
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            dt = datetime(*entry.published_parsed[:6])
            return dt.strftime("%d/%m/%Y %H:%M")
        except Exception:
            pass
    return "Fecha desconocida"


# ---------------------------------------------------------------------------
# Lógica de descarga
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

        # feedparser marca bozo=True si el XML está mal formado,
        # pero a veces igual tiene entradas válidas; solo abortamos si
        # no hay entries en absoluto.
        if not feed.entries:
            print(f"  ⚠ Sin artículos en {fuente['nombre']} "
                  f"(¿feed caído o URL incorrecta?)")
            return []

        articulos = []
        for entry in feed.entries[:MAX_ARTICULOS_POR_FUENTE]:
            # Algunos feeds usan 'summary', otros 'description'
            resumen_crudo = entry.get("summary", "") or entry.get("description", "")
            resumen = _quitar_html(resumen_crudo)

            articulos.append({
                "titulo":       entry.get("title", "Sin título").strip(),
                "enlace":       entry.get("link", "#"),
                "resumen":      resumen[:500],   # tope para no saturar la API
                "fuente":       fuente["nombre"],
                "sesgo_fuente": fuente["sesgo"],
                "fecha":        _formatear_fecha(entry),
                # Campos que rellenará analyzer.py:
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
    Descarga artículos de todas las categorías del dict de fuentes dado.

    Parámetros:
        fuentes_dict — dict {categoría: [fuentes]}. Si es None usa FUENTES.

    Devuelve {categoría: [artículos]}.
    """
    if fuentes_dict is None:
        fuentes_dict = FUENTES

    resultado: dict[str, list[dict]] = {}

    for categoria, fuentes in fuentes_dict.items():
        print(f"\n📂 {categoria}")
        articulos_categoria: list[dict] = []

        for fuente in fuentes:
            articulos = _articulos_de_fuente(fuente)
            articulos_categoria.extend(articulos)
            time.sleep(0.3)

        resultado[categoria] = articulos_categoria

    return resultado


def obtener_noticias_alternativas() -> dict[str, list[dict]]:
    """Atajo para descargar las fuentes de FUENTES_ALTERNATIVAS."""
    return obtener_todas_las_noticias(FUENTES_ALTERNATIVAS)
