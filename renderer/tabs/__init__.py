"""
Registro de pestañas del digest.

Para añadir una nueva pestaña:
  1. Crea renderer/tabs/mi_pestaña.py con TAB_ID, TAB_LABEL y render()
  2. Añádelo a la lista TABS en el orden deseado
"""

from renderer.tabs import (
    destacadas,
    actualidad,
    asombro,
    sintesis,
    todas,
    libertaria,
    para_leer,
    estadisticas,
)

# Orden en el sidebar. Cada módulo debe tener TAB_ID, TAB_LABEL y render().
TABS = [
    destacadas,
    actualidad,
    asombro,
    sintesis,
    todas,
    libertaria,
    para_leer,
    estadisticas,
]
