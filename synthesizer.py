"""
synthesizer.py — Agrupa artículos relacionados y sintetiza perspectivas cruzadas.

Estrategia de una sola llamada a Claude:
  1. Envía todos los artículos (id + fuente + título + resumen corto)
  2. Pide que detecte grupos que cubren el MISMO evento concreto
  3. Para cada grupo genera una síntesis que contrasta perspectivas
  4. Devuelve los grupos con referencias a los artículos originales

El resultado alimenta la pestaña "Síntesis" del digest HTML.
"""

import json
import hashlib
import re

from config import CLAUDE_MODEL, IDIOMA_ANALISIS
from article_cache import shared as _cache
from claude_client import llamar_claude

# Tope de artículos candidatos que se mandan a Claude (tras el pre-filtro).
_MAX_ARTICULOS_SINTESIS = 80

# Palabras vacías en español (no sirven para detectar similitud temática).
_STOPWORDS = frozenset("""
a al algo ante año así aunque bajo bien como con cual cuando de del desde donde
durante el ella ellos en entre era es ese eso está este fue gran había han hay
hasta he hizo incluso ja la las le les lo los más me mi mismo muy ni no nos o
para pero poco por que quien se se ser si sin sobre su sus también tan te toda
todo tras tu un una uno unas unos va ya yo
""".split())


def _palabras_clave(titulo: str) -> frozenset[str]:
    """Extrae palabras significativas de un título (≥4 chars, no stopwords)."""
    palabras = re.findall(r"[a-záéíóúüñ]{4,}", titulo.lower())
    return frozenset(p for p in palabras if p not in _STOPWORDS)


def _pre_filtrar_candidatos(todos: list[dict]) -> list[dict]:
    """
    Devuelve solo los artículos que comparten ≥2 palabras clave con al menos
    otro artículo de DISTINTA fuente. El resto son temas únicos y no producirán
    grupos en síntesis — no tiene sentido mandárselos a Claude.
    """
    claves = [_palabras_clave(a.get("titulo", "")) for a in todos]
    fuentes = [a.get("fuente", "") for a in todos]
    n = len(todos)
    tiene_par = [False] * n

    for i in range(n):
        if not claves[i]:
            continue
        for j in range(i + 1, n):
            if fuentes[i] == fuentes[j]:
                continue  # misma fuente no cuenta
            if len(claves[i] & claves[j]) >= 2:
                tiene_par[i] = True
                tiene_par[j] = True

    return [a for a, ok in zip(todos, tiene_par) if ok]

# System prompt estático — se cachea entre llamadas (Sonnet: mínimo 1024 tokens).
_SYSTEM_SINTESIS = """Eres un editor periodístico experto en análisis comparativo de medios españoles e iberoamericanos. Tu especialidad es detectar cuándo distintas fuentes cubren el mismo hecho y sintetizar las diferencias de enfoque de forma rigurosa y útil.

════════════════════════════════════════
TAREA
════════════════════════════════════════

Recibirás una lista de artículos de distintas fuentes (ya pre-filtrados como candidatos a tener cobertura cruzada). Debes:

1. AGRUPAR los artículos que traten el MISMO evento o hecho noticioso concreto.
2. Para cada grupo, redactar una SÍNTESIS que contraste los enfoques de las distintas fuentes.

════════════════════════════════════════
REGLAS DE AGRUPACIÓN
════════════════════════════════════════

▸ Agrupa SOLO por hechos específicos y concretos, nunca por temas generales.
  CORRECTO: "El Congreso aprueba la reforma de la ley de vivienda en primera lectura"
  INCORRECTO: "Política de vivienda en España"
  CORRECTO: "Terremoto de magnitud 6.2 sacude el sur de Turquía"
  INCORRECTO: "Desastres naturales"

▸ Un grupo necesita mínimo 2 artículos de DISTINTAS fuentes. Un mismo medio con dos artículos sobre lo mismo no forma grupo válido.

▸ Si un artículo no encaja claramente con ningún otro, omítelo. Es preferible menos grupos de calidad que muchos grupos forzados.

▸ Un artículo solo puede pertenecer a un grupo. Si parece encajar en dos, elige el que más lo defina y omítelo del otro.

════════════════════════════════════════
ESTRUCTURA DE CADA SÍNTESIS
════════════════════════════════════════

Redacta en el idioma especificado. Cada síntesis tiene esta estructura:

Párrafo 1 — El hecho central
Describe qué ocurrió con precisión y objetividad. Sin adjetivos valorativos. Solo los datos que todas las fuentes confirman.

Párrafo 2 — Contraste de enfoques
Compara cómo cada fuente encuadra el hecho: qué enfatiza, qué minimiza, qué datos incluye y cuáles omite, qué fuentes cita. Nombra los medios explícitamente ("Mientras El País destaca X, ABC enfoca Y...").

Párrafo 3 — Divergencia significativa (solo si existe)
Solo si hay una diferencia de interpretación genuinamente relevante entre las fuentes: señala cuáles están más alejadas entre sí y qué revela esa brecha sobre sus líneas editoriales o audiencias.

════════════════════════════════════════
TÍTULO DEL GRUPO
════════════════════════════════════════

El título debe:
— Contener un verbo activo que capture la tensión o el ángulo central ("España congela...", "El BCE sube...", "Investigación revela...")
— Ser específico, no genérico
— Tener entre 6 y 12 palabras
— NO ser un resumen neutro tipo "Cobertura mediática de X"

Ejemplos MALOS:
× "Situación política en Cataluña"
× "Noticias sobre el conflicto en Ucrania"

Ejemplos BUENOS:
✓ "El Gobierno congela las pensiones mientras la inflación supera el 4%"
✓ "La OTAN activa el artículo 4 ante el avance ruso en Zaporiyia"
✓ "Bruselas abre expediente a España por déficit excesivo tras el dato de julio"

════════════════════════════════════════
ERRORES COMUNES A EVITAR
════════════════════════════════════════

— No agrupes artículos por tema general cuando cubren hechos distintos. Dos artículos sobre "la economía española" que no hablan del mismo dato o evento no forman grupo.
— No hagas síntesis que resuman sin contrastar. El valor está en mostrar la diferencia de enfoque, no en parafrasear lo que cada uno dice.
— No uses lenguaje valorativo en el párrafo 1 (el factual). "Gravísima crisis" o "histórico acuerdo" son juicios, no hechos.
— No inventes datos que no estén en los resúmenes. Si no tienes suficiente información para contrastar, di solo lo que sabes.
— El párrafo 3 es opcional. Si las fuentes simplemente enfatizan lo mismo de forma diferente pero sin divergencia real, omítelo.

════════════════════════════════════════
FORMATO DE RESPUESTA
════════════════════════════════════════

JSON puro, sin bloques markdown, sin texto antes ni después:
{"grupos": [{"titulo": "...", "sintesis": "...", "ids": [0, 3, 7]}]}

Si ningún artículo forma un grupo válido con otro: {"grupos": []}"""

# Template de usuario — solo los artículos dinámicos
_USER_TMPL_SINTESIS = """Artículos disponibles (idioma de respuesta: {idioma}):
{articulos_json}

Responde ÚNICAMENTE con JSON válido."""


def sintetizar_noticias(
    noticias: dict[str, list[dict]],
    alternativas: dict[str, list[dict]] | None = None,
) -> list[dict]:
    """
    Detecta historias comunes entre artículos y genera síntesis cruzadas.

    Incluye tanto fuentes principales como alternativas para que la síntesis
    refleje también la diferencia entre medios mainstream y contrainformativos.

    Devuelve lista de grupos:
    [
        {
            "titulo":    str,
            "sintesis":  str,
            "articulos": [
                {
                    "fuente":       str,
                    "titulo":       str,
                    "enlace":       str,
                    "categoria":    str,
                    "sesgo_fuente": str,
                }
            ]
        }
    ]
    """
    todos: list[dict] = []

    for cat, arts in noticias.items():
        for a in arts:
            # Omitir ruido puro — no aporta a la síntesis cruzada
            if not a.get("es_ruido"):
                todos.append({**a, "_categoria": cat, "_alt": False})

    if alternativas:
        for cat, arts in alternativas.items():
            for a in arts:
                if not a.get("es_ruido"):
                    todos.append({**a, "_categoria": cat, "_alt": True})

    if not todos:
        return []

    # Pre-filtro local: solo artículos con ≥2 palabras clave en común con otro
    # artículo de distinta fuente. Evita mandar a Claude temas únicos.
    total_antes = len(todos)
    todos = _pre_filtrar_candidatos(todos)
    if not todos:
        print(f"  ℹ Pre-filtro: 0 candidatos de {total_antes} — ningún tema compartido")
        return []

    if len(todos) > _MAX_ARTICULOS_SINTESIS:
        # Priorizar artículos con más novedad antes de truncar
        todos.sort(key=lambda a: a.get("novedad", 2), reverse=True)
        print(f"  ℹ Limitando a {_MAX_ARTICULOS_SINTESIS} artículos para síntesis "
              f"(de {len(todos)} totales, ya sin ruido)")
        todos = todos[:_MAX_ARTICULOS_SINTESIS]

    print(f"  ℹ Pre-filtro: {len(todos)} candidatos de {total_antes} artículos totales")

    # Comprobar caché antes de llamar a Claude
    _clave_cache = hashlib.md5(
        "|".join(sorted(a["enlace"] for a in todos)).encode()
    ).hexdigest()
    cached = _cache.get_sintesis(_clave_cache)
    if cached is not None:
        print(f"  ✓ Síntesis desde caché ({len(cached)} historia(s), 0 tokens)")
        return cached

    payload = [
        {
            "id":      i,
            "fuente":  a["fuente"],
            "titulo":  a["titulo"],
            "resumen": (a.get("resumen") or "")[:120],
        }
        for i, a in enumerate(todos)
    ]

    user_msg = _USER_TMPL_SINTESIS.format(
        idioma=IDIOMA_ANALISIS,
        articulos_json=json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
    )

    print(f"  → Enviando {len(todos)} candidatos a Claude para síntesis...")
    resultado = llamar_claude(
        user_msg,
        system=_SYSTEM_SINTESIS,
        model=CLAUDE_MODEL,
        max_tokens=4096,
        temperature=0.3,
        cache_system=True,
    )

    if resultado is None:
        return []

    grupos_finales: list[dict] = []

    for grupo in resultado.get("grupos", []):
        ids = grupo.get("ids", [])
        articulos_grupo = []

        for i in ids:
            if 0 <= i < len(todos):
                a = todos[i]
                articulos_grupo.append({
                    "fuente":       a["fuente"],
                    "titulo":       a["titulo"],
                    "enlace":       a["enlace"],
                    "categoria":    a["_categoria"],
                    "sesgo_fuente": a.get("sesgo_fuente", "desconocido"),
                    "alt":          a["_alt"],
                })

        fuentes_unicas = {art["fuente"] for art in articulos_grupo}
        if len(fuentes_unicas) >= 2:
            grupos_finales.append({
                "titulo":    grupo.get("titulo", "Historia sin título"),
                "sintesis":  grupo.get("sintesis", ""),
                "articulos": articulos_grupo,
            })

    grupos_finales.sort(key=lambda g: len(g["articulos"]), reverse=True)

    _cache.set_sintesis(_clave_cache, grupos_finales)
    _cache.guardar()
    print(f"  ✓ {len(grupos_finales)} historia(s) detectada(s)")
    return grupos_finales
