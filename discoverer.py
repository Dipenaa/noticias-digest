"""
discoverer.py — Descubre y evalúa nuevos canales de información.

Dos mecanismos complementarios:

  1. Autodescubrimiento desde una URL
     Dado el dominio de cualquier medio (ej: "https://www.elconfidencial.com"),
     rastrea su HTML buscando la etiqueta estándar que los sitios publican para
     anunciar su feed RSS/Atom.  No necesita Gemini.

  2. Sugerencia por tema con Gemini
     Dado un tema o nicho (ej: "periodismo de datos en América Latina"),
     pregunta a Gemini qué fuentes RSS son relevantes, fiables y cuál es su
     sesgo editorial estimado.  Devuelve candidatos listos para copiar a config.py.

Uso como script independiente:
  python discoverer.py --url https://www.elconfidencial.com
  python discoverer.py --tema "economía latinoamericana"
  python discoverer.py --interactivo
"""

import re
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import json
import requests
import feedparser

from config import GEMINI_API_KEY, GEMINI_MODEL


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

_GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# Patrones de rutas RSS que muchos sitios usan por convención
_RUTAS_COMUNES = [
    "/rss", "/rss.xml", "/feed", "/feed.xml", "/feeds/posts/default",
    "/atom.xml", "/rss/all", "/rss/feed", "/news/rss", "/rss/noticias",
]


# ---------------------------------------------------------------------------
# Mecanismo 1: Autodescubrimiento desde una URL
# ---------------------------------------------------------------------------

def descubrir_desde_url(url: str) -> list[dict]:
    """
    Rastrea el HTML de una URL buscando feeds RSS/Atom declarados
    con la etiqueta estándar <link rel="alternate" type="application/...+xml">.

    Si no encuentra ninguno, prueba rutas RSS convencionales.

    Devuelve una lista de dicts:
      {"url": str, "titulo": str, "tipo": "rss"|"atom"|"desconocido"}
    """
    # Normaliza la URL: asegura que tenga esquema
    if not url.startswith("http"):
        url = "https://" + url

    print(f"\n🔍 Buscando feeds en: {url}")
    feeds_encontrados: list[dict] = []

    # ── Paso 1: parsea el HTML buscando <link rel="alternate"> ──────────
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        html = resp.text

        # Extrae todos los <link> con type rss/atom (puede ser en una línea o multilínea)
        patron = re.compile(
            r'<link[^>]+type=["\']application/(rss|atom)\+xml["\'][^>]*>',
            re.IGNORECASE,
        )
        for match in patron.finditer(html):
            tag = match.group(0)

            # Extrae href
            href_match = re.search(r'href=["\']([^"\']+)["\']', tag, re.IGNORECASE)
            if not href_match:
                continue
            href = href_match.group(1)

            # Extrae title (opcional)
            title_match = re.search(r'title=["\']([^"\']+)["\']', tag, re.IGNORECASE)
            titulo = title_match.group(1) if title_match else "Sin título"

            # Convierte href relativo a absoluto
            if href.startswith("//"):
                href = "https:" + href
            elif href.startswith("/"):
                from urllib.parse import urlparse
                base = urlparse(url)
                href = f"{base.scheme}://{base.netloc}{href}"

            tipo = "rss" if "rss" in match.group(1).lower() else "atom"
            feeds_encontrados.append({"url": href, "titulo": titulo, "tipo": tipo})

    except requests.exceptions.RequestException as e:
        print(f"  ⚠ No se pudo descargar {url}: {e}")

    # ── Paso 2: prueba rutas convencionales si no encontró nada ─────────
    if not feeds_encontrados:
        print("  ↳ No se encontraron <link> RSS/Atom; probando rutas comunes...")
        from urllib.parse import urlparse
        base = urlparse(url)
        raiz = f"{base.scheme}://{base.netloc}"

        for ruta in _RUTAS_COMUNES:
            candidato = raiz + ruta
            try:
                feed = feedparser.parse(candidato)
                if feed.entries:
                    feeds_encontrados.append({
                        "url":    candidato,
                        "titulo": feed.feed.get("title", ruta),
                        "tipo":   "rss",
                    })
                    print(f"  ✓ Encontrado en ruta común: {candidato}")
            except Exception:
                pass

    # ── Resultado ────────────────────────────────────────────────────────
    if feeds_encontrados:
        print(f"\n  ✅ {len(feeds_encontrados)} feed(s) encontrado(s):")
        for f in feeds_encontrados:
            print(f"     [{f['tipo'].upper()}] {f['titulo']}")
            print(f"            {f['url']}")
    else:
        print("  ❌ No se encontraron feeds RSS/Atom en este sitio.")

    return feeds_encontrados


# ---------------------------------------------------------------------------
# Mecanismo 2: Sugerencia por tema con Gemini
# ---------------------------------------------------------------------------

_PROMPT_SUGERENCIAS = """
Eres un experto en periodismo digital y fuentes de información de calidad.

El usuario quiere encontrar fuentes RSS fiables sobre el siguiente tema o nicho:
"{tema}"

Proporciona entre 5 y 8 sugerencias de fuentes RSS en {idioma}.
Para cada una incluye:
- "nombre": nombre del medio o blog
- "url_rss": URL directa del feed RSS (debe ser una URL real y funcional)
- "url_web": URL del sitio web principal
- "sesgo": sesgo editorial estimado (uno de: "izquierda", "centro-izquierda",
  "centro", "centro-derecha", "derecha", "desconocido")
- "descripcion": 1 oración describiendo el enfoque editorial

Prioriza fuentes reales, activas y con RSS verificable.
Incluye fuentes de diferente sesgo para ofrecer perspectivas diversas.

Responde ÚNICAMENTE con JSON válido (sin bloques de código markdown):
{{
  "fuentes": [
    {{
      "nombre": "...",
      "url_rss": "...",
      "url_web": "...",
      "sesgo": "...",
      "descripcion": "..."
    }}
  ]
}}
"""


def sugerir_fuentes(tema: str, idioma: str = "español") -> list[dict]:
    """
    Pide a Gemini que sugiera feeds RSS relevantes para un tema dado.

    Devuelve lista de dicts con: nombre, url_rss, url_web, sesgo, descripcion.
    """
    print(f"\n🤖 Consultando a Gemini sobre: '{tema}'...")

    prompt = _PROMPT_SUGERENCIAS.format(tema=tema, idioma=idioma)
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 2048},
    }

    try:
        resp = requests.post(_GEMINI_URL, json=payload, timeout=60)
        resp.raise_for_status()

        texto = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        if texto.startswith("```"):
            texto = "\n".join(texto.splitlines()[1:-1]).strip()

        datos = json.loads(texto)
        fuentes = datos.get("fuentes", [])

    except Exception as e:
        print(f"  ✗ Error al consultar Gemini: {e}")
        return []

    # ── Verifica cuáles feeds realmente responden ────────────────────────
    print(f"\n  Verificando {len(fuentes)} sugerencia(s)...")
    verificadas: list[dict] = []
    for f in fuentes:
        url_rss = f.get("url_rss", "")
        try:
            feed = feedparser.parse(url_rss)
            activo = bool(feed.entries)
        except Exception:
            activo = False

        f["activo"] = activo
        verificadas.append(f)
        estado = "✓" if activo else "⚠"
        print(f"  {estado} {f.get('nombre', '?'):<30} {url_rss}")

    return verificadas


# ---------------------------------------------------------------------------
# Formateo de resultados como bloque para config.py
# ---------------------------------------------------------------------------

def formatear_para_config(fuentes: list[dict], categoria: str = "Nueva categoría") -> str:
    """
    Genera el bloque Python listo para pegar en la sección FUENTES de config.py.
    """
    lineas = [f'    "{categoria}": [']
    for f in fuentes:
        nombre = f.get("nombre", "?")
        url    = f.get("url_rss", f.get("url", ""))
        sesgo  = f.get("sesgo", "desconocido")
        activo = f.get("activo")
        nota   = "" if activo is None or activo else "  # ⚠ feed no verificado"

        lineas.append(f'        {{')
        lineas.append(f'            "nombre": "{nombre}",')
        lineas.append(f'            "url":    "{url}",{nota}')
        lineas.append(f'            "sesgo":  "{sesgo}",')
        lineas.append(f'        }},')
    lineas.append("    ],")

    bloque = "\n".join(lineas)
    return f"\n# ── Copia esto en FUENTES dentro de config.py ──\n{bloque}\n"


# ---------------------------------------------------------------------------
# CLI interactivo
# ---------------------------------------------------------------------------

def _modo_interactivo() -> None:
    print("\n🔎 Modo interactivo de descubrimiento de fuentes")
    print("=" * 50)
    print("Opciones:")
    print("  1 — Buscar RSS en un sitio web")
    print("  2 — Sugerir fuentes por tema (usa Gemini)")
    print("  q — Salir")

    while True:
        opcion = input("\n> Elige opción: ").strip().lower()

        if opcion == "q":
            break
        elif opcion == "1":
            url = input("  URL del sitio (ej: https://www.elconfidencial.com): ").strip()
            if url:
                feeds = descubrir_desde_url(url)
                if feeds:
                    categoria = input("  ¿En qué categoría añadirías estos feeds? ").strip()
                    fuentes_fmt = [{"nombre": f["titulo"], "url_rss": f["url"], "sesgo": "desconocido"} for f in feeds]
                    print(formatear_para_config(fuentes_fmt, categoria or "Nueva"))
        elif opcion == "2":
            tema = input("  Tema o nicho (ej: 'economía argentina'): ").strip()
            if tema:
                fuentes = sugerir_fuentes(tema)
                if fuentes:
                    categoria = input("  ¿Cómo llamarías a esta categoría? ").strip()
                    print(formatear_para_config(fuentes, categoria or tema.title()))
        else:
            print("  Opción no reconocida.")


# ---------------------------------------------------------------------------
# Punto de entrada cuando se ejecuta como script
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or "--interactivo" in args:
        _modo_interactivo()

    elif "--url" in args:
        idx = args.index("--url")
        if idx + 1 < len(args):
            feeds = descubrir_desde_url(args[idx + 1])
            if feeds:
                fuentes_fmt = [{"nombre": f["titulo"], "url_rss": f["url"], "sesgo": "desconocido"} for f in feeds]
                print(formatear_para_config(fuentes_fmt))
        else:
            print("Uso: python discoverer.py --url https://ejemplo.com")

    elif "--tema" in args:
        idx = args.index("--tema")
        if idx + 1 < len(args):
            tema = " ".join(args[idx + 1:])
            fuentes = sugerir_fuentes(tema)
            if fuentes:
                print(formatear_para_config(fuentes, tema.title()))
        else:
            print("Uso: python discoverer.py --tema 'economía latinoamericana'")

    else:
        print(__doc__)
