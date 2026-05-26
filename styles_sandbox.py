"""
styles_sandbox.py — Hereda styles.py y sobreescribe solo variables de sandbox.

Edita _OVERRIDES para experimentar con diseño sin duplicar 1000 líneas de CSS.
Cualquier cambio en styles.py (nuevos componentes, fixes) llega aquí automáticamente.
"""

from styles import _CSS as _BASE

# Variables que difieren del tema de producción.
# Añade aquí lo que quieras probar; no toques styles.py hasta estar seguro.
_OVERRIDES = """
/* ── Sandbox overrides ────────────────────────────────────────────────── */
:root {
  --txt-2: #86868b;
  --txt-3: #3d3d3f;
}
"""

# Los overrides van al final para ganar en cascada CSS sobre :root de _BASE.
_CSS = _BASE + _OVERRIDES
