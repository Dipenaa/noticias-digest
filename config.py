"""
config.py — Configuración central del sistema de noticias.

Modifica este archivo para personalizar fuentes, temas y comportamiento.
"""

import os

# ---------------------------------------------------------------------------
# API de Anthropic (Claude) — análisis de sesgo y síntesis
# ---------------------------------------------------------------------------
ANTHROPIC_API_KEY     = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL          = "claude-sonnet-4-6"           # síntesis cruzada
CLAUDE_MODEL_ANALISIS = "claude-haiku-4-5-20251001"   # análisis masivo (20× más barato)

# ---------------------------------------------------------------------------
# API de Gemini — descubrimiento de fuentes (discoverer.py)
# ---------------------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL   = "gemini-2.0-flash"

# ---------------------------------------------------------------------------
# Parámetros generales
# ---------------------------------------------------------------------------
MAX_ARTICULOS_POR_FUENTE = 1   # 1 por fuente — suficiente señal, -50% tokens
ARCHIVO_SALIDA           = "noticias.html"
IDIOMA_ANALISIS          = "español"

# ---------------------------------------------------------------------------
# Fuentes RSS principales — organizadas por categoría
# ---------------------------------------------------------------------------
# Sesgo estimado: "izquierda" | "centro-izquierda" | "centro" |
#                 "centro-derecha" | "derecha" | "desconocido"

FUENTES = {
    "España": [
        {"nombre": "El País",          "url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada",  "sesgo": "centro-izquierda"},
        {"nombre": "El Mundo",         "url": "https://e00-elmundo.uecdn.es/elmundo/rss/portada.xml",              "sesgo": "centro-derecha"},
        {"nombre": "eldiario.es",      "url": "https://www.eldiario.es/rss/",                                      "sesgo": "izquierda"},
        {"nombre": "ABC",              "url": "https://www.abc.es/rss/feeds/abc_EspanaEspana.xml",                 "sesgo": "derecha"},
        {"nombre": "La Vanguardia",    "url": "https://www.lavanguardia.com/rss/home.xml",                         "sesgo": "centro"},
        {"nombre": "El Confidencial",  "url": "https://rss.elconfidencial.com/espana/",                            "sesgo": "centro"},
        {"nombre": "Público",          "url": "https://www.publico.es/rss/",                                       "sesgo": "izquierda"},
        {"nombre": "infoLibre",        "url": "https://www.infolibre.es/rss/portada.xml",                         "sesgo": "izquierda"},
        {"nombre": "El Español",       "url": "https://www.elespanol.com/rss/",                                    "sesgo": "centro-derecha"},
        {"nombre": "RTVE Noticias",    "url": "https://www.rtve.es/api/noticias.rss",                              "sesgo": "centro"},
    ],
    "Internacional": [
        {"nombre": "BBC Mundo",        "url": "https://feeds.bbci.co.uk/mundo/rss.xml",                            "sesgo": "centro"},
        {"nombre": "Al Jazeera",       "url": "https://www.aljazeera.com/xml/rss/all.xml",                        "sesgo": "centro-izquierda"},
        {"nombre": "DW Español",       "url": "https://rss.dw.com/rdf/rss-sp-all",                                "sesgo": "centro"},
        {"nombre": "France 24",        "url": "https://www.france24.com/es/rss",                                   "sesgo": "centro"},
        {"nombre": "The Guardian",     "url": "https://www.theguardian.com/world/rss",                             "sesgo": "centro-izquierda"},
        {"nombre": "Euronews",         "url": "https://es.euronews.com/rss?format=mrss&level=theme&name=news",     "sesgo": "centro"},
    ],
    "Tecnología": [
        {"nombre": "Xataka",           "url": "https://www.xataka.com/atom.xml",                                   "sesgo": "centro"},
        {"nombre": "Ars Technica",     "url": "https://feeds.arstechnica.com/arstechnica/index",                   "sesgo": "centro"},
        {"nombre": "Hipertextual",     "url": "https://hipertextual.com/feed",                                     "sesgo": "centro"},
        {"nombre": "Genbeta",          "url": "https://feeds.weblogssl.com/genbeta",                               "sesgo": "centro"},
        {"nombre": "The Verge",        "url": "https://www.theverge.com/rss/index.xml",                            "sesgo": "centro-izquierda"},
        {"nombre": "Wired",            "url": "https://www.wired.com/feed/rss",                                    "sesgo": "centro"},
    ],
    "Economía": [
        {"nombre": "Expansión",        "url": "https://e00-expansion.uecdn.es/rss/portada.xml",                   "sesgo": "centro-derecha"},
        {"nombre": "Cinco Días",       "url": "https://cincodias.elpais.com/rss/feed.htm?category=home",           "sesgo": "centro"},
        {"nombre": "El Economista",    "url": "https://www.eleconomista.es/rss/rss-portada.php",                   "sesgo": "centro-derecha"},
        {"nombre": "Bloomberg (EN)",   "url": "https://feeds.bloomberg.com/markets/news.rss",                      "sesgo": "centro"},
        {"nombre": "El Confidencial E","url": "https://rss.elconfidencial.com/mercados/",                          "sesgo": "centro"},
    ],
    "Ciencia": [
        {"nombre": "Muy Interesante",  "url": "https://www.muyinteresante.es/rss",                                 "sesgo": "centro"},
        {"nombre": "National Geo ES",  "url": "https://www.nationalgeographic.com.es/rss/latest",                  "sesgo": "centro"},
        {"nombre": "BBC Science",      "url": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",     "sesgo": "centro"},
        {"nombre": "New Scientist",    "url": "https://www.newscientist.com/feed/home/",                           "sesgo": "centro"},
    ],
    "Historia": [
        {"nombre": "National Geo Historia", "url": "https://www.nationalgeographic.com.es/historia/rss",           "sesgo": "centro"},
        {"nombre": "Muy Historia",          "url": "https://www.muyinteresante.es/historia/rss",                   "sesgo": "centro"},
        {"nombre": "History Extra (BBC)",   "url": "https://www.historyextra.com/feed/",                           "sesgo": "centro"},
        {"nombre": "History Today",         "url": "https://www.historytoday.com/feed",                            "sesgo": "centro"},
    ],
    "Antropología": [
        {"nombre": "Sapiens",               "url": "https://www.sapiens.org/feed/",                                "sesgo": "centro"},
        {"nombre": "SINC Agencia",          "url": "https://www.agenciasinc.es/rss/biologia-y-biomedicina",        "sesgo": "centro"},
        {"nombre": "Archaeology Magazine",  "url": "https://www.archaeology.org/feed",                             "sesgo": "centro"},
        {"nombre": "The Conversation ES",   "url": "https://theconversation.com/es/feeds",                         "sesgo": "centro"},
    ],
}

# ---------------------------------------------------------------------------
# Fuentes alternativas — izquierda crítica, anarquista e intelectual
# ---------------------------------------------------------------------------
# Se muestran en la pestaña "Izquierda Crítica" del digest.
# Criterio: rigor intelectual y crítica sistémica, no alarmismo ni propaganda.

FUENTES_ALTERNATIVAS = {
    "Izquierda Crítica España": [
        {"nombre": "El Salto Diario",  "url": "https://www.elsaltodiario.com/rss",                                 "sesgo": "izquierda"},
        {"nombre": "La Marea",         "url": "https://www.lamarea.com/feed/",                                     "sesgo": "izquierda"},
        {"nombre": "Rebelión",         "url": "https://rebelion.org/feed/",                                        "sesgo": "izquierda"},
        {"nombre": "Tierra y Libertad","url": "https://www.tierraylibertad.org/feed/",                             "sesgo": "izquierda"},
        {"nombre": "Pikara Magazine",  "url": "https://www.pikaramagazine.com/feed/",                              "sesgo": "izquierda"},
        {"nombre": "CGT España",       "url": "https://cgt.org.es/feed/",                                          "sesgo": "izquierda"},
    ],
    "Pensamiento Crítico Internacional": [
        {"nombre": "Sin Permiso",      "url": "https://sinpermiso.info/rss.xml",                                   "sesgo": "izquierda"},
        {"nombre": "Jacobin Lat.",     "url": "https://jacobinlat.com/feed/",                                      "sesgo": "izquierda"},
        {"nombre": "The Intercept",    "url": "https://theintercept.com/feed/?rss",                                "sesgo": "izquierda"},
        {"nombre": "Common Dreams",    "url": "https://rss.commondreams.org/commondreams/views05.rss",             "sesgo": "izquierda"},
        {"nombre": "Freedom News",     "url": "https://freedomnews.org.uk/feed/",                                  "sesgo": "izquierda"},
        {"nombre": "Mondoweiss",       "url": "https://mondoweiss.net/feed/",                                      "sesgo": "izquierda"},
    ],
}
