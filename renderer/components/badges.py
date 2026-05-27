"""Badges y etiquetas visuales de sesgo, sentimiento y novedad."""

import html as _html

from analyzer import COLORES_SESGO

_LABELS_SESGO = {
    "izquierda":        "IZQ",
    "centro-izquierda": "C·IZQ",
    "centro":           "CTR",
    "centro-derecha":   "C·DER",
    "derecha":          "DER",
    "desconocido":      "?",
}

_CLASES_SENTIMIENTO = {
    "alarmista": "badge-sent-alarmista",
    "neutral":   "badge-sent-neutral",
    "optimista": "badge-sent-optimista",
}
_ICONOS_SENTIMIENTO = {"alarmista": "⚠", "neutral": "◉", "optimista": "✦"}


def badge(sesgo: str) -> str:
    color = COLORES_SESGO.get(sesgo, COLORES_SESGO["desconocido"])
    label = _LABELS_SESGO.get(sesgo, sesgo.upper())
    return f'<span class="badge" style="background:{color}" title="{sesgo}">{label}</span>'


def badge_sentimiento(sentimiento: str) -> str:
    if not sentimiento or sentimiento == "neutral":
        return ""
    cls  = _CLASES_SENTIMIENTO.get(sentimiento, "badge-sent-neutral")
    icon = _ICONOS_SENTIMIENTO.get(sentimiento, "")
    return f'<span class="badge-sent {cls}" title="Tono: {sentimiento}">{icon} {sentimiento.upper()}</span>'


def badge_novedad(articulo: dict) -> str:
    novedad = articulo.get("novedad", 2)
    if novedad == 3:
        return '<span class="badge-senal" title="Aporta información nueva">&#9670; Señal</span>'
    if novedad <= 1:
        return '<span class="badge-ruido" title="Repite información ya publicada">&#8762; Repetición</span>'
    return ""


def leyenda() -> str:
    """Bloque de leyenda clicable para filtrar por sesgo."""
    items = []
    for s, color in COLORES_SESGO.items():
        label = _LABELS_SESGO.get(s, s.upper())
        items.append(
            f'<span class="badge" style="background:{color}" '
            f'onclick="filtrarPorSesgo(\'{s}\',this)" '
            f'title="Filtrar por {s}">{label}</span>'
        )
    badges = " ".join(items)
    return f"""
<div class="leyenda">
  <span class="leyenda-titulo">Leyenda:</span>
  <div class="leyenda-items">{badges}</div>
  <span class="leyenda-tip">(clic para filtrar)</span>
  <span class="filtro-aviso" id="filtro-aviso" style="display:none"></span>
  <button class="filtro-clear-btn" id="filtro-clear" onclick="limpiarFiltro()" style="display:none">✕ Quitar filtro</button>
</div>"""
