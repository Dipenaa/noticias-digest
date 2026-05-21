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

Coste: una llamada Haiku por condición activa. Caché de resultados 6h.
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

_SYSTEM = """Eres un analista de noticias. Determinas si una condición específica
se ha cumplido hoy basándote en los artículos disponibles."""

_PROMPT = """¿Se ha cumplido HOY la siguiente condición basándote en los artículos?

CONDICIÓN A VIGILAR: {condicion}

ARTÍCULOS DE HOY (fuente | título | resumen):
{articulos}

Responde ÚNICAMENTE con JSON:
{{
  "cumplida": true,
  "confianza": 0.85,
  "explicacion": "Breve explicación de por qué sí/no se cumplió"
}}

confianza: 0.0-1.0. Solo marca cumplida=true si hay evidencia clara en los artículos."""


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
    Comprueba cada condición activa contra los artículos de hoy.
    Devuelve lista de alertas disparadas:
    [{"id": ..., "condicion": ..., "confianza": ..., "explicacion": ...}]
    """
    condiciones = cargar_condiciones()
    if not condiciones:
        return []

    # Artículos compactos para el prompt
    todos_arts = []
    for arts in (noticias or {}).values():
        todos_arts.extend(arts)
    for arts in (alternativas or {}).values():
        todos_arts.extend(arts)

    if not todos_arts:
        return []

    articulos_str = "\n".join(
        f"{a.get('fuente','')} | {a.get('titulo','')} | {(a.get('resumen') or '')[:100]}"
        for a in todos_arts[:60]
    )

    alertas = []
    for cond in condiciones:
        cond_id = cond.get("id", "")
        condicion = cond.get("condicion", "")
        if not condicion:
            continue

        clave = f"watch:{cond_id}:{_hash_arts(todos_arts)}"
        cached = _cache._redis_get(clave)
        if cached:
            try:
                resultado = json.loads(cached)
                if resultado.get("cumplida") and resultado.get("confianza", 0) >= 0.7:
                    alertas.append({**cond, **resultado})
                continue
            except Exception:
                pass

        prompt = _PROMPT.format(condicion=condicion, articulos=articulos_str)
        resultado = llamar_claude(
            prompt,
            system=_SYSTEM,
            model=CLAUDE_MODEL_ANALISIS,
            max_tokens=300,
            temperature=0.1,
        )

        if resultado is None:
            continue

        _cache._redis_set(clave, json.dumps(resultado, ensure_ascii=False), ex=_TTL)

        if resultado.get("cumplida") and resultado.get("confianza", 0) >= 0.7:
            alertas.append({
                "id":         cond_id,
                "condicion":  condicion,
                "confianza":  resultado.get("confianza", 0),
                "explicacion": resultado.get("explicacion", ""),
            })
            print(f"  ⚠ Vigilar: condición disparada — {condicion[:50]}")

    return alertas


def _hash_arts(arts: list[dict]) -> str:
    import hashlib
    titulos = "".join(a.get("titulo", "") for a in arts[:20])
    return hashlib.md5(titulos.encode()).hexdigest()[:8]
