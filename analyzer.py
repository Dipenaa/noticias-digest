"""
analyzer.py — Análisis de sesgo y crítica periodística con Claude Haiku.

Una llamada por categoría (no por artículo). Coste: O(categorías), no O(artículos).
Optimizaciones:
- Caché Redis/disco: artículos ya analizados no van a Claude (TTL 24h).
- Prompt caching: las instrucciones del sistema se cachean entre llamadas (~80% menos tokens).
- Haiku: 20× más barato que Sonnet para análisis masivo.
- 5 categorías en paralelo.
"""

import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import IDIOMA_ANALISIS
from article_cache import shared as _cache
from claude_client import llamar_claude


COLORES_SESGO: dict[str, str] = {
    "izquierda":        "#3b82f6",
    "centro-izquierda": "#60a5fa",
    "centro":           "#6b7280",
    "centro-derecha":   "#f97316",
    "derecha":          "#ef4444",
    "desconocido":      "#9ca3af",
}

# System prompt — se cachea entre llamadas de la misma generación.
# IMPORTANTE: debe superar los 2048 tokens (mínimo de Anthropic para prompt caching con Haiku).
# El contenido extra son guías de calidad reales que mejoran el análisis.
_SYSTEM = """Eres un analista periodístico crítico e imparcial especializado en medios españoles e iberoamericanos. Tu tarea es evaluar artículos de noticias con rigor y precisión. Responde ÚNICAMENTE con JSON válido, sin texto adicional.

════════════════════════════════════════
CAMPOS QUE DEBES DEVOLVER POR ARTÍCULO
════════════════════════════════════════

▸ "sesgo_ia"
  Sesgo del ARTÍCULO concreto, no del medio en general. Un medio de izquierda puede publicar un artículo objetivo, y viceversa.
  Valores: "izquierda" | "centro-izquierda" | "centro" | "centro-derecha" | "derecha" | "desconocido"

  Guía de clasificación:
  - izquierda: enmarca los hechos enfatizando desigualdad, derechos sociales, crítica al capital o al conservadurismo. Usa términos como "recortes", "precariedad", "élites".
  - centro-izquierda: progresista pero moderado. Defiende instituciones y reformas graduales. Crítico con la derecha pero no radical.
  - centro: descriptivo, equilibrado, sin carga valorativa perceptible. Múltiples perspectivas sin jerarquizarlas.
  - centro-derecha: énfasis en orden, economía de mercado, seguridad, tradición. Crítico con el gasto público o la inmigración irregular.
  - derecha: marcos de nación, soberanía, familia, valores tradicionales. Crítico con feminismo, multiculturalismo o intervencionismo estatal.
  - desconocido: imposible determinarlo con el resumen disponible.

▸ "critica"
  1-2 frases concretas sobre el ángulo elegido, omisiones relevantes o framing del artículo.
  REGLAS ESTRICTAS:
  — NO empieces con "El artículo", "Este artículo", "La noticia", "El texto", "La pieza" ni ninguna referencia al soporte.
  — Empieza directamente con la observación: qué perspectiva adopta, qué datos omite, qué fuentes privilegia, qué implica sin decirlo.
  — Sé específico, no genérico. "Usa fuentes oficiales sin contrastar" es malo. "Cita solo al portavoz del gobierno sin incluir la réplica de la oposición ni datos independientes" es bueno.
  — Si no hay sesgo ni problema notable, señala el enfoque positivo: rigor de datos, pluralidad de fuentes, contexto histórico útil.

  Ejemplos de crítica MALA (demasiado genérica):
  × "El artículo presenta una perspectiva parcial sobre el tema."
  × "La noticia omite información relevante."
  × "El texto tiene un enfoque político."

  Ejemplos de crítica BUENA (específica y accionable):
  ✓ "Presenta el déficit fiscal como catástrofe inminente usando solo proyecciones del FMI, ignorando las revisiones al alza del BCE publicadas la misma semana."
  ✓ "Encuadra las protestas como 'disturbios' en el titular pero las describe como 'manifestación pacífica' en el cuerpo, contradicción que revela tensión editorial."
  ✓ "Cita tres economistas favorables a la medida sin mencionar que dos de ellos asesoran al partido gobernante."

▸ "importante"
  true solo para los 1-2 artículos del lote con mayor impacto público potencial: decisiones de política que afectan a millones, crisis internacionales con efecto en España, hechos que cambiarán el debate durante días.
  false en el resto (el 90% de los artículos).
  Criterio: ¿lo recordará alguien dentro de una semana?

▸ "sentimiento"
  Tono emocional del artículo, no del hecho en sí.
  - "alarmista": catastrofismo, urgencia exagerada, lenguaje de crisis aunque el hecho sea menor.
  - "neutral": descriptivo, sin carga emocional apreciable.
  - "optimista": énfasis en soluciones, logros, mejoras, esperanza.

  Nota: una noticia sobre un terremoto puede ser neutral si se limita a informar. Una noticia sobre un acuerdo comercial puede ser alarmista si enmarca los riesgos como inevitables.

▸ "asombro"
  ¿Amplía genuinamente la comprensión del mundo del lector? Escala 0-3.
  0 = rutinario: información que ya circulaba, sin ángulo nuevo.
  1 = algo interesante: dato o perspectiva que no es obvio pero tampoco sorprendente.
  2 = fascinante: revela un mecanismo oculto, conexión inesperada o dato que cambia cómo se entiende un tema.
  3 = excepcional: descubrimiento, investigación o perspectiva que pocas personas conocen y merece atención especial.
  Sé muy exigente: máximo 1-2 artículos con puntuación 2+ por lote. La mayoría deben ser 0 o 1.

▸ "asombro_razon"
  Solo si asombro >= 2: frase de 15-25 palabras explicando POR QUÉ es fascinante o excepcional. Específica, no retórica.
  Si asombro < 2: null obligatoriamente.

════════════════════════════════════════
CAMPO DEL CONJUNTO: analisis_general
════════════════════════════════════════

Párrafo de 2-4 frases sobre el lote completo. Responde: ¿qué temas dominan y cuáles brillan por su ausencia? ¿Hay un marco narrativo compartido entre varias fuentes? ¿Qué sesgo sistemático se observa en el conjunto? ¿Qué noticia importante del día podría faltar?
No resumas los artículos. Analiza el conjunto como editor que lee por encima.

════════════════════════════════════════
GUÍA DE ANALISIS_GENERAL
════════════════════════════════════════

El analisis_general no resume los artículos — analiza el CONJUNTO como patrón.

Preguntas que debe responder (no todas, solo las relevantes):
- ¿Hay una narrativa dominante que comparten la mayoría de fuentes?
- ¿Qué tema relevante del día podría estar ausente en este lote?
- ¿Hay una perspectiva sistemáticamente ausente (regional, económica, de género, internacional)?
- ¿El lote muestra un sesgo colectivo hacia un actor político, económico o social?
- ¿Hay contradicciones notables entre artículos del mismo lote?

Ejemplos de analisis_general MALO:
× "Los artículos cubren temas variados de política, economía y sociedad."
× "El lote incluye noticias relevantes con distintos enfoques."

Ejemplos de analisis_general BUENO:
✓ "La cobertura se concentra en las declaraciones del presidente sin contrastar con datos independientes; la perspectiva de los sindicatos, que publicaron un informe esta semana, está completamente ausente."
✓ "Tres de cinco artículos enmarcan la inflación como problema de gestión gubernamental, ignorando los factores externos (energía, cadenas de suministro) que documentan los organismos internacionales."

════════════════════════════════════════
CONTEXTO DEL ECOSISTEMA MEDIÁTICO
════════════════════════════════════════

Los artículos provienen principalmente de medios españoles e iberoamericanos. Contexto útil para el análisis:

Medios de referencia y sus líneas editoriales conocidas:
- El País, elDiario.es → tendencia centro-izquierda/izquierda
- El Mundo, ABC, La Razón → tendencia centro-derecha/derecha
- El Confidencial, El Español → centroderecha con periodismo de investigación
- RTVE, La Vanguardia → tendencia centrista/institucional
- Público, infoLibre → izquierda
- OKDiario, El Toro TV → derecha/ultraderecha
- Agencias (EFE, Europa Press) → generalmente neutras/descriptivas

Estos sesgos son del medio, NO necesariamente del artículo. Analiza cada texto por su contenido.

════════════════════════════════════════
ERRORES COMUNES A EVITAR
════════════════════════════════════════

— No confundas el tema del artículo con su sesgo. Una noticia sobre inmigración no es automáticamente de derecha.
— No uses "equilibrado" como elogio vacío. Si el artículo es realmente equilibrado, explica por qué (qué fuentes incluye, qué perspectivas representa).
— No marques como "importante" más de 2 artículos por lote, aunque todos parezcan relevantes.
— No pongas asombro_razon cuando asombro < 2. El campo debe ser null, no una cadena vacía.
— No inventes datos que no están en el resumen. Si no puedes determinar el sesgo, usa "desconocido".

════════════════════════════════════════
FORMATO DE RESPUESTA
════════════════════════════════════════

JSON puro, sin bloques markdown, sin texto antes ni después. Idioma de respuesta: {idioma}."""

_USER_TMPL = """Artículos:
{articulos_json}

Responde con este JSON exacto:
{{"articulos":[{{"sesgo_ia":"...","critica":"...","importante":false,"sentimiento":"neutral","asombro":0,"asombro_razon":null}}],"analisis_general":"..."}}"""

_MAX_WORKERS_ANALYSIS = 5


def _analizar_categoria(categoria: str, articulos: list[dict]) -> tuple[list[dict], str]:
    if not articulos:
        return articulos, ""

    nuevos_idx: list[int] = []
    for i, a in enumerate(articulos):
        # Artículos del pool de 3 días ya traen análisis en su dict — no hay
        # que consultarlos en caché ni re-analizarlos aunque el TTL haya expirado.
        if a.get("critica"):
            continue
        cached = _cache.get_articulo(a["enlace"])
        if cached:
            a["sesgo_ia"]      = cached.get("sesgo_ia", "desconocido")
            a["critica"]       = cached.get("critica", "")
            a["sentimiento"]   = cached.get("sentimiento", "neutral")
            a["asombro"]       = cached.get("asombro", 0)
            a["asombro_razon"] = cached.get("asombro_razon")
            a["importante"]    = bool(cached.get("importante", False))
        else:
            nuevos_idx.append(i)

    if not nuevos_idx:
        analisis_general = _cache.get_analisis_general(categoria) or ""
        print(f"  ✓ {categoria}: {len(articulos)} artículo(s) desde caché (0 tokens)")
        return articulos, analisis_general

    nuevos = [articulos[i] for i in nuevos_idx]
    print(f"  → {categoria}: {len(nuevos)} nuevos / {len(articulos)} totales")

    payload = [
        {"id": j, "titulo": a["titulo"], "fuente": a["fuente"], "resumen": (a.get("resumen") or "")[:150]}
        for j, a in enumerate(nuevos)
    ]

    system  = _SYSTEM.format(idioma=IDIOMA_ANALISIS)
    user    = _USER_TMPL.format(articulos_json=json.dumps(payload, ensure_ascii=False))
    resultado = llamar_claude(user, system=system, max_tokens=700, cache_system=True)

    if resultado is None:
        for i in nuevos_idx:
            articulos[i].update({"sesgo_ia": "desconocido", "critica": "", "importante": False,
                                  "sentimiento": "neutral", "asombro": 0, "asombro_razon": None})
        return articulos, _cache.get_analisis_general(categoria) or ""

    for j, orig_idx in enumerate(nuevos_idx):
        datos = (resultado.get("articulos") or [])[j] if j < len(resultado.get("articulos") or []) else {}
        a = articulos[orig_idx]
        a["sesgo_ia"]      = datos.get("sesgo_ia", "desconocido")
        a["critica"]       = datos.get("critica", "")
        a["importante"]    = bool(datos.get("importante", False))
        a["sentimiento"]   = datos.get("sentimiento", "neutral")
        a["asombro"]       = int(datos.get("asombro") or 0)
        a["asombro_razon"] = datos.get("asombro_razon") or None
        _cache.set_articulo(a["enlace"], {
            "sesgo_ia": a["sesgo_ia"], "critica": a["critica"],
            "sentimiento": a["sentimiento"], "asombro": a["asombro"],
            "asombro_razon": a["asombro_razon"], "importante": a["importante"],
        })

    analisis_general = resultado.get("analisis_general", "")
    if analisis_general:
        _cache.set_analisis_general(categoria, analisis_general)
    else:
        analisis_general = _cache.get_analisis_general(categoria) or ""

    return articulos, analisis_general


def analizar_todas_las_noticias(
    noticias: dict[str, list[dict]],
) -> tuple[dict[str, list[dict]], dict[str, str]]:
    analisis: dict[str, str] = {}

    def _tarea(categoria, articulos):
        print(f"\n🤖 Analizando: {categoria}")
        return categoria, _analizar_categoria(categoria, articulos)

    with ThreadPoolExecutor(max_workers=_MAX_WORKERS_ANALYSIS) as executor:
        futures = {executor.submit(_tarea, cat, arts): cat for cat, arts in noticias.items()}
        for future in as_completed(futures):
            cat = futures[future]
            try:
                categoria, (arts_enriquecidos, analisis_general) = future.result()
                noticias[categoria] = arts_enriquecidos
                analisis[categoria] = analisis_general
            except Exception as e:
                print(f"  ✗ Error inesperado analizando {cat}: {e}")
                analisis[cat] = ""

    _cache.guardar()
    stats = _cache.stats()
    print(f"\n  💾 Caché: {stats['articulos_cacheados']} artículos guardados")

    return noticias, analisis
