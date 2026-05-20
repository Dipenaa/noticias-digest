"""
main.py — Punto de entrada del sistema de noticias.

Uso:
  python main.py            # Ciclo completo: fetch + análisis IA + HTML
  python main.py --sin-ia   # Solo descarga RSS, sin llamar a Gemini
  python main.py --ayuda    # Muestra esta ayuda
"""

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import time

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, CLAUDE_MODEL_ANALISIS
from fetcher import obtener_todas_las_noticias, obtener_noticias_alternativas
from analyzer import analizar_todas_las_noticias
from synthesizer import sintetizar_noticias
from renderer import renderizar_html, guardar_y_abrir


# ---------------------------------------------------------------------------
# Validaciones previas
# ---------------------------------------------------------------------------

def _verificar_configuracion() -> None:
    if ANTHROPIC_API_KEY in ("", None):
        print()
        print("  ⚠  ANTHROPIC_API_KEY no configurada.")
        print("  Define la variable de entorno ANTHROPIC_API_KEY.")
        print("  También puedes usar: python main.py --sin-ia")
        print()
        sys.exit(1)


def _ayuda() -> None:
    print(__doc__)
    sys.exit(0)


# ---------------------------------------------------------------------------
# Flujo principal
# ---------------------------------------------------------------------------

def main() -> None:
    args = set(sys.argv[1:])

    if "--ayuda" in args or "--help" in args:
        _ayuda()

    sin_ia = "--sin-ia" in args

    print("=" * 60)
    print("  📰  Sistema de Noticias — Digest Personal")
    print("=" * 60)

    if not sin_ia:
        _verificar_configuracion()
        print(f"\n  Modelos IA : análisis={CLAUDE_MODEL_ANALISIS}, síntesis={CLAUDE_MODEL}")
    else:
        print("\n  Modo: solo RSS (sin análisis de IA)")

    t0 = time.time()

    # ── 1. Noticias principales ──────────────────────────────────────────
    print("\n📡 Descargando noticias principales...")
    noticias = obtener_todas_las_noticias()
    total = sum(len(a) for a in noticias.values())
    print(f"\n  → {total} artículo(s) en fuentes principales")

    # ── 2. Noticias alternativas ─────────────────────────────────────────
    print("\n📡 Descargando prensa libertaria...")
    alternativas = obtener_noticias_alternativas()
    total_alt = sum(len(a) for a in alternativas.values())
    print(f"\n  → {total_alt} artículo(s) en fuentes alternativas")

    print(f"\n📊 Total descargado: {total + total_alt} artículo(s)")

    # ── 3. Análisis con Claude ───────────────────────────────────────────
    analisis:     dict[str, str] = {}
    analisis_alt: dict[str, str] = {}
    grupos_sintesis: list[dict]  = []

    if sin_ia:
        print("\n⏭  Saltando análisis de IA (--sin-ia activado)")
    else:
        print("\n🤖 Analizando noticias principales con Claude...")
        noticias, analisis = analizar_todas_las_noticias(noticias)

        print("\n🤖 Analizando prensa libertaria con Claude...")
        alternativas, analisis_alt = analizar_todas_las_noticias(alternativas)

        print("\n🔗 Detectando historias comunes y generando síntesis...")
        grupos_sintesis = sintetizar_noticias(noticias, alternativas)

    # ── 4. Renderizado y apertura ────────────────────────────────────────
    print("\n🎨 Generando HTML...")
    html = renderizar_html(noticias, analisis, alternativas, analisis_alt, grupos_sintesis)
    guardar_y_abrir(html)

    duracion = time.time() - t0
    print(f"\n⏱  Completado en {duracion:.1f} s")
    print("=" * 60)


if __name__ == "__main__":
    main()
