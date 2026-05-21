"""
noise_filter.py — Detecta ruido informativo: artículos que repiten lo mismo sin añadir valor.

Estrategia:
- Una sola llamada Haiku con todos los artículos compactos (títulos + resúmenes)
- Cada artículo recibe novedad 1-3: 3=nueva perspectiva, 2=añade algo, 1=repetición
- Caché Redis 6h para no repetir si se regenera el mismo día
- Los artículos con novedad=1 se marcan es_ruido=True en el dict de noticias
"""

import json
import hashlib
from config import CLAUDE_MODEL_ANALISIS
from article_cache import shared as _cache
from claude_client import llamar_claude

_TTL = 6 * 3600

_SYSTEM = """Eres un editor de noticias. Detectas cuando distintos medios cubren exactamente el mismo
hecho sin añadir información nueva. No te importa el sesgo político — solo si el artículo aporta
datos, perspectivas o detalles que los demás no tienen."""

_PROMPT = """Analiza estos artículos de noticias. Para cada uno, determina cuánta información NUEVA
aporta en comparación con los demás sobre el mismo tema.

Artículos (id | fuente | título | resumen):
{articulos}

Responde ÚNICAMENTE con JSON válido:
{{
  "ruido": [
    {{
      "id": 0,
      "novedad": 3,
      "razon": "Exclusiva con datos de desempleo no publicados en otros medios"
    }}
  ]
}}

novedad: 3=perspectiva o datos nuevos; 2=añade algo menor; 1=repetición casi exacta del mismo hecho
Incluye TODOS los artículos en la respuesta."""


def _clave_cache(noticias: dict) -> str:
    titulos = sorted(
        a.get("titulo", "")
        for arts in noticias.values() for a in arts
    )
    digest = hashlib.md5("|".join(titulos).encode()).hexdigest()
    return f"ruido:v1:{digest}"


def detectar_ruido(noticias: dict) -> dict:
    """
    Añade los campos 'novedad' (1-3) y 'es_ruido' (bool) a cada artículo.
    Devuelve el mismo dict modificado in-place.
    Si no hay Redis o falla, devuelve noticias sin cambios.
    """
    clave = _clave_cache(noticias)
    cached = _cache._redis_get(clave)
    if cached:
        try:
            scores = {item["id"]: item for item in json.loads(cached)}
            _aplicar_scores(noticias, scores)
            n_ruido = sum(1 for arts in noticias.values() for a in arts if a.get("es_ruido"))
            print(f"  ✓ Ruido/señal: desde caché ({n_ruido} artículos marcados como ruido)")
            return noticias
        except Exception:
            pass

    # Construir lista compacta global (todos los artículos)
    compactos = []
    for arts in noticias.values():
        for a in arts:
            idx = len(compactos)
            a["_ruido_idx"] = idx
            compactos.append(
                f"{idx} | {a.get('fuente','')} | {a.get('titulo','')} | {(a.get('resumen') or '')[:110]}"
            )

    if len(compactos) < 2:
        return noticias

    print(f"  → Ruido/señal: analizando {len(compactos)} artículos...")
    prompt = _PROMPT.format(articulos="\n".join(compactos))
    resultado = llamar_claude(
        prompt,
        system=_SYSTEM,
        model=CLAUDE_MODEL_ANALISIS,
        max_tokens=2000,
        temperature=0.1,
    )

    if resultado is None:
        return noticias

    items = resultado.get("ruido", [])
    scores = {item["id"]: item for item in items if isinstance(item.get("id"), int)}
    _aplicar_scores(noticias, scores)

    # Guardar en caché (solo los scores, no los artículos completos)
    _cache._redis_set(clave, json.dumps(items, ensure_ascii=False), ex=_TTL)

    n_ruido = sum(1 for arts in noticias.values() for a in arts if a.get("es_ruido"))
    n_señal = sum(1 for arts in noticias.values() for a in arts if a.get("novedad", 2) == 3)
    print(f"  ✓ Ruido/señal: {n_señal} señales, {n_ruido} repeticiones")
    return noticias


def _aplicar_scores(noticias: dict, scores: dict) -> None:
    for arts in noticias.values():
        for a in arts:
            idx = a.get("_ruido_idx")
            if idx is not None and idx in scores:
                item = scores[idx]
                a["novedad"]  = max(1, min(3, int(item.get("novedad") or 2)))
                a["es_ruido"] = a["novedad"] <= 1
                a["novedad_razon"] = item.get("razon", "")
            else:
                a["novedad"]  = 2
                a["es_ruido"] = False
