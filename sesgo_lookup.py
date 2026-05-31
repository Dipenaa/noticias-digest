"""
sesgo_lookup.py — Mapa medio → sesgo editorial estimado.

Para las fuentes dinámicas (Google News) que no están en config.py.
Ampliable a mano; las desconocidas devuelven "desconocido" (el front las
muestra igual, sin posición en el espectro). Una estimación única con
discoverer.py (Gemini) puede rellenar huecos y cachearse aquí en el futuro.
"""

# Claves en minúscula. Coincidencia exacta primero, luego "contiene".
_MAPA = {
    # España
    "el país": "centro-izquierda", "el pais": "centro-izquierda",
    "el mundo": "centro-derecha", "abc": "derecha",
    "eldiario.es": "izquierda", "eldiario": "izquierda",
    "la vanguardia": "centro", "el confidencial": "centro",
    "público": "izquierda", "publico": "izquierda",
    "infolibre": "izquierda", "el español": "centro-derecha", "el espanol": "centro-derecha",
    "la razón": "derecha", "la razon": "derecha",
    "rtve": "centro", "20 minutos": "centro", "el periódico": "centro-izquierda",
    "el periodico": "centro-izquierda", "okdiario": "derecha", "libertad digital": "derecha",
    "vozpópuli": "centro-derecha", "huffpost": "centro-izquierda", "the objective": "centro-derecha",
    "diario sur": "centro", "canal sur": "centro", "la sexta": "centro-izquierda",
    "antena 3": "centro", "telecinco": "centro", "cope": "derecha", "cadena ser": "centro-izquierda",
    "onda cero": "centro",
    # Económicos
    "expansión": "centro-derecha", "expansion": "centro-derecha",
    "cinco días": "centro", "cinco dias": "centro", "el economista": "centro-derecha",
    # Agencias
    "europa press": "centro", "efe": "centro", "agencia efe": "centro",
    "reuters": "centro", "associated press": "centro", "ap": "centro", "bloomberg": "centro",
    # Internacional
    "bbc": "centro", "bbc mundo": "centro", "bbc news": "centro",
    "the guardian": "centro-izquierda", "the new york times": "centro-izquierda",
    "the washington post": "centro-izquierda", "washington post": "centro-izquierda",
    "the wall street journal": "centro-derecha", "wall street journal": "centro-derecha",
    "financial times": "centro", "the economist": "centro", "cnn": "centro-izquierda",
    "fox news": "derecha", "al jazeera": "centro-izquierda", "le monde": "centro-izquierda",
    "le figaro": "centro-derecha", "deutsche welle": "centro", "dw": "centro",
    "france 24": "centro", "euronews": "centro", "politico": "centro",
    "the times": "centro-derecha", "the telegraph": "derecha", "the independent": "centro-izquierda",
    "associated press news": "centro", "ap news": "centro",
}


def sesgo_de_fuente(nombre: str) -> str:
    """Devuelve el sesgo estimado de un medio, o 'desconocido'."""
    if not nombre:
        return "desconocido"
    n = nombre.lower().strip().rstrip("|").strip()
    if n in _MAPA:
        return _MAPA[n]
    # coincidencia parcial (ej. "el país tecnología" → "el país")
    for clave, val in _MAPA.items():
        if clave in n:
            return val
    return "desconocido"
