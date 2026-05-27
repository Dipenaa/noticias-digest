"""
renderer.py — Shim de compatibilidad.

El código real está en el paquete renderer/.
Este fichero se mantiene para que los imports existentes (app.py, main.py)
sigan funcionando sin cambios.
"""

from renderer import renderizar_html, guardar_y_abrir  # noqa: F401

__all__ = ["renderizar_html", "guardar_y_abrir"]
