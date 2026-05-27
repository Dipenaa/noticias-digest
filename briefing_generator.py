"""
briefing_generator.py — Genera un memo de inteligencia de ~300 palabras.

Estilo President's Daily Brief: denso, accionable, sin relleno.
Usa Sonnet (no Haiku) porque la síntesis de calidad lo requiere.
Caché Redis 12h — se genera una vez al día bajo demanda.
"""

import json
from datetime import datetime
from config import CLAUDE_MODEL
from article_cache import shared as _cache
from claude_client import llamar_claude

_TTL = 12 * 3600
_KEY = "briefing:hoy"

_SYSTEM = """Eres un analista de inteligencia senior. Produces memos de situación concisos,
densos y accionables. Estilo President's Daily Brief: sin retórica, sin relleno,
máxima información por palabra. Escribes en español."""

_PROMPT = """Con los datos de hoy, produce un MEMO DE SITUACIÓN de 280-340 palabras.

PROCESOS MUNDIALES ACTIVOS:
{procesos_str}

TITULARES RELEVANTES DE HOY:
{titulares_str}

Estructura EXACTA (usa estos encabezados en negrita):

**SITUACIÓN GLOBAL**
[2-3 frases. Qué está pasando en el mundo hoy en términos macro. Sin obviedades.]

**QUÉ CAMBIÓ HOY**
• [Desarrollo 1 — concreto, con dato o actor específico]
• [Desarrollo 2]
• [Desarrollo 3]

**SEÑALES DE ALERTA**
• [Proceso o evento que requiere atención especial y por qué]
• [Segundo si hay otro genuinamente urgente]

**QUÉ VIGILAR (próximos 7 días)**
• [Indicador concreto o evento que confirmaría o descartaría una hipótesis]
• [Segundo indicador]

Sé específico. Nombra actores, países, cifras cuando los tengas. Sin frases genéricas."""


def generar_briefing(procesos: list[dict], noticias: dict, alternativas: dict | None = None) -> str:
    """
    Genera el memo. Devuelve el texto en markdown.
    Primero comprueba caché Redis.
    """
    cached = _cache._redis_get(_KEY)
    if cached:
        try:
            data = json.loads(cached)
            print(f"  ✓ Briefing: desde caché (0 tokens)")
            return data.get("texto", "")
        except Exception:
            pass

    print(f"  → Briefing: generando memo con {CLAUDE_MODEL}...")

    procesos_str = "\n".join(
        f"• {p.get('nombre','?')} [{p.get('estado','?').upper()}, imp {p.get('importancia','?')}/10]: "
        f"{p.get('resumen_hoy', p.get('descripcion',''))}"
        for p in (procesos or [])
    ) or "Sin procesos identificados hoy."

    # Selección de los titulares más relevantes (máx 30, priorizando novedad=3)
    todos_arts = []
    for cat, arts in {**(noticias or {}), **(alternativas or {})}.items():
        for a in arts:
            todos_arts.append((a.get("novedad", 2), a.get("importante", False), a))

    todos_arts.sort(key=lambda x: (x[0] == 3, x[1]), reverse=True)
    seleccionados = [t[2] for t in todos_arts[:20]]

    titulares_str = "\n".join(
        f"- [{a.get('fuente','')}] {a.get('titulo','')}"
        for a in seleccionados
    ) or "Sin artículos disponibles."

    prompt = _PROMPT.format(procesos_str=procesos_str, titulares_str=titulares_str)
    texto = llamar_claude(
        prompt,
        system=_SYSTEM,
        model=CLAUDE_MODEL,
        max_tokens=550,
        temperature=0.4,
        raw_text=True,
        cache_system=True,
    )

    if not texto:
        return "Error generando el briefing. Inténtalo de nuevo."

    _cache._redis_set(_KEY, json.dumps({"texto": texto, "fecha": datetime.now().isoformat()},
                                       ensure_ascii=False), ex=_TTL)
    print(f"  ✓ Briefing: {len(texto)} chars generados")
    return texto
