"""
macro_registry.py — Registro persistente de procesos del mundo.

Almacena un archivo canónico de procesos que se acumula indefinidamente,
independiente de la lógica de detección (macro_tracker.py).

Si macro_tracker cambia su algoritmo o Claude genera IDs distintos,
este módulo reconcilia los procesos nuevos con los ya conocidos para
mantener la identidad y el historial intactos.

Estructura de cada entrada:
{
  "id": "guerra-rusia-ucrania",          <- ID canónico, nunca cambia
  "nombre": "Guerra Rusia-Ucrania",      <- nombre canónico, estable
  "descripcion": "Invasión rusa...",
  "fecha_inicio": "2026-01-15",
  "fecha_ultimo": "2026-05-27",
  "n_dias_cubiertos": 87,
  "importancia_max": 9,
  "estado_actual": "escalada",
  "horizonte": "anos",
  "historial": [
    {"fecha": "2026-05-27", "estado": "escalada", "importancia": 9,
     "n_articulos": 12, "resumen": "..."},
    ...                                  <- últimos 180 días (6 meses)
  ]
}
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

from article_cache import shared as _cache

_KEY_REGISTRO   = "macro:registro:v1"
_BACKUP_PATH    = Path("macro_registro.json")
_TTL_1_YEAR     = 365 * 24 * 3600   # 1 año en segundos; se renueva en cada escritura
_MAX_HISTORIAL  = 180                # días de historial por proceso

_SYSTEM_RECONCILIAR = """Eres un analista que decide si procesos nuevos son el mismo conflicto
que procesos ya conocidos, aunque tengan nombre ligeramente distinto.
Son el mismo proceso si describen el mismo conflicto, crisis o tensión en curso.
No son el mismo si son eventos distintos aunque estén relacionados temáticamente."""

_PROMPT_RECONCILIAR = """Procesos CONOCIDOS en el registro:
{conocidos}

Procesos NUEVOS detectados hoy:
{nuevos}

Para cada proceso NUEVO, decide si coincide con alguno conocido o es genuinamente nuevo.

Responde ÚNICAMENTE con JSON válido:
{{"resultados": [{{"id_nuevo": "slug", "coincide_con": "id-conocido-o-null"}}]}}"""


# ---------------------------------------------------------------------------
# Carga y guardado
# ---------------------------------------------------------------------------

def cargar_registro() -> dict[str, dict]:
    """Carga el registro desde Redis; fallback a JSON en disco."""
    raw = _cache._redis_get(_KEY_REGISTRO)
    if raw:
        try:
            return json.loads(raw)
        except Exception:
            pass
    if _BACKUP_PATH.exists():
        try:
            return json.loads(_BACKUP_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def guardar_registro(registro: dict[str, dict]) -> None:
    """Persiste el registro en Redis (TTL 1 año, se renueva) y en disco."""
    datos = json.dumps(registro, ensure_ascii=False, indent=2)
    _cache._redis_set(_KEY_REGISTRO, datos, ex=_TTL_1_YEAR)
    try:
        _BACKUP_PATH.write_text(datos, encoding="utf-8")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Reconciliación
# ---------------------------------------------------------------------------

def reconciliar(procesos_hoy: list[dict], registro: dict[str, dict]) -> list[dict]:
    """
    Asigna IDs canónicos a los procesos de hoy comparando con el registro.

    Si un proceso coincide con uno conocido → usa su ID y nombre canónico.
    Si es nuevo → mantiene el ID generado por Claude y lo marcamos como nuevo.

    Añade el campo '_nuevo_en_registro' (bool) a cada proceso.
    """
    if not registro:
        for p in procesos_hoy:
            p["_nuevo_en_registro"] = True
        return procesos_hoy

    from claude_client import llamar_claude
    from config import CLAUDE_MODEL_ANALISIS

    conocidos_str = "\n".join(
        f"- {pid}: {info.get('nombre', pid)} — {info.get('descripcion', '')[:80]}"
        for pid, info in registro.items()
    )
    nuevos_str = "\n".join(
        f"- {p['id']}: {p.get('nombre', p['id'])} — {p.get('descripcion', '')[:80]}"
        for p in procesos_hoy
    )

    resultado = llamar_claude(
        _PROMPT_RECONCILIAR.format(conocidos=conocidos_str, nuevos=nuevos_str),
        system=_SYSTEM_RECONCILIAR,
        model=CLAUDE_MODEL_ANALISIS,
        max_tokens=300,
        temperature=0.1,
    )

    if resultado is None:
        for p in procesos_hoy:
            p["_nuevo_en_registro"] = True
        return procesos_hoy

    mapa = {
        r["id_nuevo"]: r.get("coincide_con")
        for r in resultado.get("resultados", [])
        if isinstance(r, dict) and r.get("id_nuevo")
    }

    for p in procesos_hoy:
        coincide = mapa.get(p["id"])
        if coincide and coincide in registro:
            info = registro[coincide]
            p["id"]     = coincide
            p["nombre"] = info["nombre"]
            p["_nuevo_en_registro"] = False
        else:
            p["_nuevo_en_registro"] = True

    return procesos_hoy


# ---------------------------------------------------------------------------
# Actualización del registro
# ---------------------------------------------------------------------------

def actualizar_registro(registro: dict[str, dict], procesos_hoy: list[dict]) -> dict[str, dict]:
    """Añade o actualiza las entradas de hoy en el registro."""
    hoy = datetime.now().strftime("%Y-%m-%d")

    for p in procesos_hoy:
        pid = p["id"]
        entrada_hoy = {
            "fecha":       hoy,
            "estado":      p.get("estado", "estable"),
            "importancia": p.get("importancia", 5),
            "n_articulos": len(p.get("articulos") or []),
            "resumen":     (p.get("resumen_hoy") or "")[:200],
        }

        if pid not in registro:
            registro[pid] = {
                "id":               pid,
                "nombre":           p.get("nombre", pid),
                "descripcion":      p.get("descripcion", ""),
                "fecha_inicio":     hoy,
                "fecha_ultimo":     hoy,
                "n_dias_cubiertos": 1,
                "importancia_max":  p.get("importancia", 5),
                "estado_actual":    p.get("estado", "estable"),
                "horizonte":        p.get("horizonte", "meses"),
                "historial":        [entrada_hoy],
            }
        else:
            r = registro[pid]
            # Solo añadir si no hemos guardado ya hoy
            if not r["historial"] or r["historial"][-1]["fecha"] != hoy:
                r["historial"].append(entrada_hoy)
                r["historial"] = r["historial"][-_MAX_HISTORIAL:]
                r["n_dias_cubiertos"] += 1
            r["fecha_ultimo"]   = hoy
            r["importancia_max"] = max(r.get("importancia_max", 0), p.get("importancia", 5))
            r["estado_actual"]  = p.get("estado", "estable")

    return registro


# ---------------------------------------------------------------------------
# Enriquecimiento de procesos con datos del registro
# ---------------------------------------------------------------------------

def enriquecer(procesos: list[dict], registro: dict[str, dict]) -> list[dict]:
    """
    Añade a cada proceso campos derivados del historial:
      - dias_activo    : días que el proceso lleva en el registro
      - fecha_inicio   : cuándo fue detectado por primera vez
      - tendencia_pct  : % de cambio en cobertura vs hace 7 días
      - historial      : lista de 30 días {fecha, cobertura} para la sparkline
    """
    today = datetime.now()
    for p in procesos:
        pid = p.get("id", "")
        r   = registro.get(pid, {})

        p["dias_activo"]  = r.get("n_dias_cubiertos", 1)
        p["fecha_inicio"] = r.get("fecha_inicio", today.strftime("%Y-%m-%d"))

        hist  = r.get("historial", [])
        n_hoy = len(p.get("articulos") or [])
        if len(hist) >= 7:
            n_ref = hist[-7].get("n_articulos", 0)
            p["tendencia_pct"] = int((n_hoy - n_ref) / max(n_ref, 1) * 100)
        else:
            p["tendencia_pct"] = 0

        # 30-day calendar historial for sparkline — fills calendar gaps with 0
        hist_by_date = {h["fecha"]: h.get("n_articulos", 0) for h in hist}
        p["historial"] = [
            {
                "fecha":     (today - timedelta(days=i)).strftime("%Y-%m-%d"),
                "cobertura": hist_by_date.get(
                    (today - timedelta(days=i)).strftime("%Y-%m-%d"), 0
                ),
            }
            for i in range(29, -1, -1)
        ]

    return procesos


# ---------------------------------------------------------------------------
# Consulta pública (para el usuario)
# ---------------------------------------------------------------------------

def get_todos() -> list[dict]:
    """Devuelve todos los procesos del registro, más recientes primero."""
    return sorted(
        cargar_registro().values(),
        key=lambda p: p.get("fecha_ultimo", ""),
        reverse=True,
    )
