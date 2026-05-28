"""
macro_tracker.py — Identifica los 3-5 procesos mundiales más importantes del día.

Estrategia:
- Sonnet para identificar procesos: ~2-3 céntimos/día (1 llamada caché 24h)
- Haiku fue sustituido porque devolvía [] con JSON complejo; Sonnet es más fiable
- Caché Redis 24h: solo ejecuta una vez aunque el digest se regenere varias veces
- Guarda snapshot diario en Redis (TTL 15 días) para el historial de cobertura
"""

import json
import re
from datetime import datetime, timedelta

from config import CLAUDE_MODEL, CLAUDE_MODEL_ANALISIS
from article_cache import shared as _cache
from claude_client import llamar_claude

_TTL_PROCESOS  = 24 * 3600       # 24h — no recalcular si se regenera hoy
_TTL_HISTORIAL = 15 * 24 * 3600  # 15 días de historial

_KEY_HOY       = "macro:hoy:{fecha}"  # date-aware para evitar cache stale entre días
_KEY_SNAP      = "macro:snap:{fecha}"  # {proceso_id: n_articulos}

_ESTADOS = {"escalada", "estable", "resolucion", "silencio"}
_HORIZONTES = {"dias", "semanas", "meses", "anos"}

# Solo categorías con noticias de actualidad política/social. Comparación exacta.
# Historia/Ciencia/Tecnología se excluyen — Claude no identifica procesos actuales en esas categorías.
_CATEGORIAS_PROCESO = {"España", "Internacional", "Economía"}

# Límite de artículos enviados a Claude — evita prompts enormes cuando el pool acumula 3 días
_MAX_ARTICULOS_MACRO = 50

_SYSTEM = """Eres un analista geopolítico senior especializado en España y asuntos internacionales.
Tu tarea es identificar los grandes procesos en curso: conflictos, crisis, negociaciones, tensiones
políticas o sociales que llevan días o semanas activos y tienen impacto real en las personas.
Siempre respondes con JSON válido, sin explicaciones adicionales."""

_PROMPT = """Analiza estos titulares de noticias e identifica los 2-5 PROCESOS más importantes
en curso ahora mismo — conflictos, crisis políticas, negociaciones o tensiones que persisten
en el tiempo (no eventos únicos de hoy).

Los artículos están ordenados del más reciente al más antiguo. Usa la fecha para distinguir
si algo es un proceso activo (aparece en varios días) o un evento puntual.

Artículos (id | fecha | fuente | título | resumen):
{articulos}

EJEMPLO de respuesta correcta:
{{
  "procesos": [
    {{
      "id": "guerra-ucrania",
      "nombre": "Guerra en Ucrania",
      "descripcion": "Invasión rusa en curso desde 2022 con escaladas periódicas.",
      "estado": "escalada",
      "importancia": 9,
      "horizonte": "anos",
      "resumen_hoy": "Rusia lanza nueva oleada de drones sobre Kiev. Zelenski pide más defensa aérea a la OTAN. EE.UU. debate nuevo paquete de ayuda.",
      "ids_articulos": [1, 4, 9]
    }}
  ]
}}

Devuelve JSON válido con esta estructura exacta. Si no hay procesos claros, devuelve {{"procesos": []}}.
Ordena por importancia (mayor primero)."""


def _compactar_articulos(noticias: dict) -> tuple[list[dict], list[dict]]:
    """Aplana, ordena por fecha desc y compacta artículos de categorías relevantes."""
    pares = []  # (articulo_original, categoria)
    for cat, arts in noticias.items():
        if _CATEGORIAS_PROCESO and cat not in _CATEGORIAS_PROCESO:
            continue
        for a in arts:
            pares.append(a)

    # Fallback: si el filtro vacía todo, usar todos los artículos
    if not pares:
        for arts in noticias.values():
            pares.extend(arts)

    # Ordenar del más reciente al más antiguo antes de capturar
    pares.sort(key=lambda a: a.get("fecha", ""), reverse=True)

    # Aplicar límite sobre los más recientes
    pares = pares[:_MAX_ARTICULOS_MACRO]

    todos = pares
    compactos = [
        {
            "id":      i,
            "fecha":   a.get("fecha", "")[:10],
            "fuente":  a.get("fuente", ""),
            "titulo":  a.get("titulo", ""),
            "resumen": (a.get("resumen") or "")[:120],
        }
        for i, a in enumerate(pares)
    ]
    return compactos, todos


def _llamar_sonnet(articulos_compactos: list[dict]) -> list[dict] | None:
    lineas = [
        f"{a['id']} | {a['fecha']} | {a['fuente']} | {a['titulo']} | {a['resumen']}"
        for a in articulos_compactos
    ]
    prompt = _PROMPT.format(articulos="\n".join(lineas))
    print(f"  → Macro: enviando {len(articulos_compactos)} artículos a Sonnet...")
    texto = llamar_claude(
        prompt,
        system=_SYSTEM,
        model=CLAUDE_MODEL,
        max_tokens=1500,
        temperature=0.2,
        raw_text=True,
    )
    if texto is None:
        print("  ✗ Macro: llamar_claude devolvió None (API error o rate limit)")
        return None

    print(f"  → Macro: respuesta Sonnet ({len(texto)} chars): {texto[:400]}")

    # Parse JSON; fall back to regex extraction if Sonnet added surrounding text
    resultado = None
    try:
        resultado = json.loads(texto)
    except json.JSONDecodeError:
        m = re.search(r'\{[\s\S]*\}', texto)
        if m:
            try:
                resultado = json.loads(m.group())
            except json.JSONDecodeError:
                pass
    if resultado is None:
        print(f"  ✗ Macro: JSON no parseable. Respuesta: {texto[:200]}")
        return None

    procesos = resultado.get("procesos", [])
    print(f"  → Macro: Claude identificó {len(procesos)} proceso(s) en {len(articulos_compactos)} artículos")
    return procesos


def _enriquecer_con_articulos(procesos: list[dict], todos_articulos: list[dict]) -> list[dict]:
    """Añade los objetos artículo completos a cada proceso."""
    for p in procesos:
        ids = p.get("ids_articulos", [])
        p["articulos"] = [
            {
                "titulo": todos_articulos[i].get("titulo", ""),
                "fuente": todos_articulos[i].get("fuente", ""),
                "enlace": todos_articulos[i].get("enlace", "#"),
                "fecha":  todos_articulos[i].get("fecha", datetime.now().strftime("%Y-%m-%d")),
            }
            for i in ids if 0 <= i < len(todos_articulos)
        ]
        # Normalizar campos
        if p.get("estado") not in _ESTADOS:
            p["estado"] = "estable"
        if p.get("horizonte") not in _HORIZONTES:
            p["horizonte"] = "meses"
        p["importancia"] = max(1, min(10, int(p.get("importancia") or 5)))
    return procesos


def _guardar_snapshot(procesos: list[dict]) -> None:
    """Guarda cuántos artículos tuvo cada proceso hoy."""
    fecha = datetime.now().strftime("%Y-%m-%d")
    snap = {p["id"]: len(p.get("articulos", [])) for p in procesos}
    key = _KEY_SNAP.format(fecha=fecha)
    _cache._redis_set(key, json.dumps(snap), ex=_TTL_HISTORIAL)


def _cargar_historial(proceso_id: str, dias: int = 15) -> list[dict]:
    """Devuelve lista de {fecha, cobertura} para los últimos N días."""
    historial = []
    hoy = datetime.now()
    for i in range(dias - 1, -1, -1):
        fecha = (hoy - timedelta(days=i)).strftime("%Y-%m-%d")
        key = _KEY_SNAP.format(fecha=fecha)
        raw = _cache._redis_get(key)
        cobertura = 0
        if raw:
            try:
                snap = json.loads(raw)
                cobertura = snap.get(proceso_id, 0)
            except Exception:
                pass
        historial.append({"fecha": fecha, "cobertura": cobertura})
    return historial


_KEY_CONEXIONES = "macro:conexiones:{fecha}"

_SYSTEM_CONEXIONES = """Eres un analista geopolítico. Identificas relaciones causales y temáticas
entre grandes procesos mundiales activos. Una conexión es una relación real, no trivial."""

_PROMPT_CONEXIONES = """Dados estos procesos mundiales activos:
{procesos}

Identifica 2-4 CONEXIONES importantes entre ellos — relaciones causales, sinergias o tensiones.

Responde ÚNICAMENTE con JSON válido:
{{
  "conexiones": [
    {{
      "proceso_a": "id-del-proceso",
      "proceso_b": "id-del-otro-proceso",
      "relacion": "Una frase que explique cómo A afecta a B o están relacionados causalmente."
    }}
  ]
}}

Solo conexiones reales y significativas. Máximo 4."""


def _identificar_conexiones(procesos: list[dict]) -> list[dict]:
    if len(procesos) < 2:
        return []

    _hoy_con = datetime.now().strftime("%Y-%m-%d")
    cached = _cache._redis_get(_KEY_CONEXIONES.format(fecha=_hoy_con))
    if cached:
        try:
            return json.loads(cached)
        except Exception:
            pass

    lineas = "\n".join(
        f"- {p['id']}: {p.get('nombre','?')} — {p.get('descripcion','')}"
        for p in procesos
    )
    prompt = _PROMPT_CONEXIONES.format(procesos=lineas)
    resultado = llamar_claude(
        prompt,
        system=_SYSTEM_CONEXIONES,
        model=CLAUDE_MODEL_ANALISIS,
        max_tokens=600,
        temperature=0.3,
    )
    if resultado is None:
        return []

    conexiones = resultado.get("conexiones", [])
    _cache._redis_set(_KEY_CONEXIONES.format(fecha=_hoy_con), json.dumps(conexiones, ensure_ascii=False), ex=_TTL_PROCESOS)
    print(f"  ✓ Macro: {len(conexiones)} conexión(es) entre procesos")
    return conexiones


# ---------------------------------------------------------------------------
# Punto de entrada público
# ---------------------------------------------------------------------------

def obtener_procesos(noticias: dict) -> list[dict]:
    """
    Identifica los procesos del día y los reconcilia con el registro persistente.

    Flujo:
      1. Si ya hay caché de hoy → devuelve directamente (0 tokens).
      2. Claude identifica procesos en los artículos de hoy.
      3. macro_registry reconcilia con el registro canónico (1 llamada extra Haiku).
      4. Se actualiza el registro permanente y la caché de hoy.
      5. Se enriquece con días activo y tendencia antes de devolver.
    """
    import macro_registry as _reg

    # ── Caché de hoy ──────────────────────────────────────────────────────────
    _hoy = datetime.now().strftime("%Y-%m-%d")
    cached_raw = _cache._redis_get(_KEY_HOY.format(fecha=_hoy))
    if cached_raw:
        try:
            procesos = json.loads(cached_raw)
            print(f"  ✓ Macro: {len(procesos)} proceso(s) desde caché (0 tokens)")
            registro = _reg.cargar_registro()
            return _reg.enriquecer(procesos, registro)
        except Exception:
            pass

    # ── Detectar procesos con Claude ──────────────────────────────────────────
    compactos, todos = _compactar_articulos(noticias)
    if not compactos:
        return []

    print(f"  → Macro: identificando procesos en {len(compactos)} artículos...")
    procesos = _llamar_sonnet(compactos)
    if not procesos:
        return []

    procesos = _enriquecer_con_articulos(procesos, todos)

    # ── Reconciliar con registro canónico ────────────────────────────────────
    registro = _reg.cargar_registro()
    if registro:
        print(f"  → Macro: reconciliando con {len(registro)} proceso(s) conocido(s)...")
        procesos = _reg.reconciliar(procesos, registro)

    # ── Actualizar registro permanente ────────────────────────────────────────
    registro = _reg.actualizar_registro(registro, procesos)
    _reg.guardar_registro(registro)

    # ── Caché de hoy (24h) ───────────────────────────────────────────────────
    _cache._redis_set(_KEY_HOY.format(fecha=_hoy), json.dumps(procesos, ensure_ascii=False), ex=_TTL_PROCESOS)
    _guardar_snapshot(procesos)

    # ── Enriquecer con tendencia y días activo ────────────────────────────────
    procesos = _reg.enriquecer(procesos, registro)

    print(f"  ✓ Macro: {len(procesos)} proceso(s) identificado(s) · registro: {len(registro)} total")
    return procesos


def obtener_macro_data(noticias: dict) -> dict:
    """
    Devuelve procesos + conexiones entre ellos.
    Punto de entrada recomendado para el servidor.
    """
    procesos = obtener_procesos(noticias)
    conexiones = _identificar_conexiones(procesos)
    return {"procesos": procesos, "conexiones": conexiones}
