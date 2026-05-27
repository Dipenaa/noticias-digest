"""
watch.py — Sistema de vigilancia de condiciones definidas por el usuario.

El usuario define condiciones en ~/.noticias-watch.json (o NOTICIAS_WATCH en env).
Cada generación del digest comprueba si alguna se cumple.
Si se cumple, el digest muestra un banner de alerta destacado.

Formato del fichero de condiciones:
[
  {"id": "gaza-escala", "condicion": "Gaza escala a conflicto convencional amplio"},
  {"id": "ia-act", "condicion": "La UE publica el texto final de la AI Act"}
]

Coste: una llamada Haiku batch para todas las condiciones pendientes. Caché por condición 6h.
"""

import json
import os
from pathlib import Path
from datetime import datetime

from config import CLAUDE_MODEL_ANALISIS
from article_cache import shared as _cache
from claude_client import llamar_claude

_WATCH_FILE = Path(os.getenv("NOTICIAS_WATCH_FILE",
                             str(Path.home() / ".noticias-watch.json")))
_TTL = 6 * 3600

_SYSTEM = """Eres un analista de noticias. Determinas si condiciones específicas
se han cumplido hoy basándote en los artículos disponibles.
Solo marca cumplida=true si hay evidencia clara y directa en los artículos."""

_PROMPT_BATCH = """Comprueba si estas condiciones se han cumplido HOY según los artículos.

CONDICIONES:
{condiciones_json}

ARTÍCULOS (fuente | título | resumen):
{articulos}

Responde ÚNICAMENTE con JSON:
{{
  "resultados": [
    {{
      "id": "condicion-id",
      "cumplida": false,
      "confianza": 0.0,
      "explicacion": "Por qué sí o no"
    }}
  ]
}}

Devuelve un resultado por cada condición del array, en el mismo orden. confianza: 0.0-1.0."""


def cargar_condiciones() -> list[dict]:
    """Lee las condiciones del fichero de vigilancia del usuario."""
    if not _WATCH_FILE.exists():
        return []
    try:
        return json.loads(_WATCH_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def guardar_condicion(condicion: str, cond_id: str | None = None) -> dict:
    """Añade una nueva condición al fichero. Devuelve la condición creada."""
    condiciones = cargar_condiciones()
    if cond_id is None:
        cond_id = condicion[:30].lower().replace(" ", "-").replace("'", "")
    nueva = {"id": cond_id, "condicion": condicion, "creada": datetime.now().isoformat()}
    condiciones.append(nueva)
    _WATCH_FILE.write_text(json.dumps(condiciones, ensure_ascii=False, indent=2),
                           encoding="utf-8")
    return nueva


def eliminar_condicion(cond_id: str) -> bool:
    """Elimina una condición por su id. Devuelve True si existía."""
    condiciones = cargar_condiciones()
    nuevas = [c for c in condiciones if c.get("id") != cond_id]
    if len(nuevas) == len(condiciones):
        return False
    _WATCH_FILE.write_text(json.dumps(nuevas, ensure_ascii=False, indent=2), encoding="utf-8")
    return True


def verificar_condiciones(noticias: dict, alternativas: dict | None = None) -> list[dict]:
    """
    Comprueba todas las condiciones activas en UNA sola llamada (batch).
    Las condiciones ya cacheadas no van a la API.
    Devuelve lista de alertas disparadas.
    """
    condiciones = cargar_condiciones()
    if not condiciones:
        return []

    todos_arts = []
    for arts in (noticias or {}).values():
        todos_arts.extend(arts)
    for arts in (alternativas or {}).values():
        todos_arts.extend(arts)

    if not todos_arts:
        return []

    hash_arts = _hash_arts(todos_arts)
    articulos_str = "\n".join(
        f"{a.get('fuente','')} | {a.get('titulo','')} | {(a.get('resumen') or '')[:70]}"
        for a in todos_arts[:40]
    )

    alertas: list[dict] = []
    pendientes: list[dict] = []

    # Separar condiciones cacheadas de las pendientes
    for cond in condiciones:
        cond_id  = cond.get("id", "")
        condicion = cond.get("condicion", "")
        if not condicion:
            continue
        clave = f"watch:{cond_id}:{hash_arts}"
        cached = _cache._redis_get(clave)
        if cached:
            try:
                res = json.loads(cached)
                if res.get("cumplida") and res.get("confianza", 0) >= 0.7:
                    alertas.append({**cond, **res})
                continue
            except Exception:
                pass
        pendientes.append(cond)

    if not pendientes:
        return alertas

    # Una sola llamada para todas las condiciones pendientes
    condiciones_json = json.dumps(
        [{"id": c["id"], "condicion": c["condicion"]} for c in pendientes],
        ensure_ascii=False,
    )
    prompt = _PROMPT_BATCH.format(condiciones_json=condiciones_json, articulos=articulos_str)
    resultado = llamar_claude(
        prompt,
        system=_SYSTEM,
        model=CLAUDE_MODEL_ANALISIS,
        max_tokens=400 + 150 * len(pendientes),
        temperature=0.1,
        cache_system=True,
    )

    if resultado is None:
        return alertas

    resultados_map = {r["id"]: r for r in resultado.get("resultados", []) if isinstance(r, dict)}

    for cond in pendientes:
        cond_id  = cond.get("id", "")
        clave    = f"watch:{cond_id}:{hash_arts}"
        res      = resultados_map.get(cond_id, {})
        if not res:
            continue
        _cache._redis_set(clave, json.dumps(res, ensure_ascii=False), ex=_TTL)
        if res.get("cumplida") and res.get("confianza", 0) >= 0.7:
            alertas.append({
                "id":          cond_id,
                "condicion":   cond.get("condicion", ""),
                "confianza":   res.get("confianza", 0),
                "explicacion": res.get("explicacion", ""),
            })
            print(f"  ⚠ Vigilar: condición disparada — {cond.get('condicion','')[:50]}")

    return alertas


def _hash_arts(arts: list[dict]) -> str:
    import hashlib
    titulos = "".join(a.get("titulo", "") for a in arts[:20])
    return hashlib.md5(titulos.encode()).hexdigest()[:8]
