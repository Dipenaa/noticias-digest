"""
claude_client.py — Cliente Anthropic compartido con retry, prompt caching y logging de coste.

Un único cliente para todo el proyecto (analyzer + synthesizer).
El prompt caching reduce hasta un 80% el coste de los tokens de instrucciones
en llamadas consecutivas al mismo modelo dentro de una misma generación.
"""

import json
import time
import anthropic

from config import ANTHROPIC_API_KEY

_REINTENTOS_MAX  = 4
_ESPERA_BASE_429 = 30
_ESPERA_BASE_5XX = 5

_client: anthropic.Anthropic | None = None

# Acumulador de coste para la generación en curso (en dólares).
# Se reinicia al llamar reset_coste().
_coste_total: float = 0.0
_llamadas:    int   = 0

# Precios por millón de tokens (MTok) — mayo 2026
_PRECIOS: dict[str, dict[str, float]] = {
    "claude-haiku-4-5-20251001": {
        "input":          0.80,   # $/MTok
        "output":         4.00,
        "cache_write":    1.00,   # escritura de caché (1.25× input)
        "cache_read":     0.08,   # lectura de caché (0.1× input)
    },
    "claude-sonnet-4-6": {
        "input":          3.00,
        "output":        15.00,
        "cache_write":    3.75,
        "cache_read":     0.30,
    },
}
_PRECIOS_DEFAULT = {"input": 3.00, "output": 15.00, "cache_write": 3.75, "cache_read": 0.30}


def _calcular_coste(model: str, usage) -> float:
    p = _PRECIOS.get(model, _PRECIOS_DEFAULT)
    inp   = getattr(usage, "input_tokens",                0) or 0
    out   = getattr(usage, "output_tokens",               0) or 0
    cw    = getattr(usage, "cache_creation_input_tokens", 0) or 0
    cr    = getattr(usage, "cache_read_input_tokens",     0) or 0
    # Los tokens de caché se cobran diferente; los input_tokens ya NO incluyen los de caché
    return (inp * p["input"] + out * p["output"] +
            cw  * p["cache_write"] + cr * p["cache_read"]) / 1_000_000


def reset_coste() -> None:
    global _coste_total, _llamadas
    _coste_total = 0.0
    _llamadas    = 0


def resumen_coste() -> str:
    return f"${_coste_total:.4f} en {_llamadas} llamada(s)"


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


def llamar_claude(
    user_content: str,
    system: str | None = None,
    model: str | None = None,
    max_tokens: int = 1024,
    temperature: float = 0.2,
    cache_system: bool = False,
    raw_text: bool = False,
) -> dict | str | None:
    """
    Llama a Claude y devuelve el JSON parseado, o None si falla.

    Si cache_system=True, marca el system prompt como cacheable (ephemeral).
    Ahorra tokens en llamadas consecutivas con el mismo system prompt.
    """
    global _coste_total, _llamadas
    from config import CLAUDE_MODEL_ANALISIS
    model = model or CLAUDE_MODEL_ANALISIS
    client = get_client()

    # Construir el system prompt (con o sin cache_control)
    system_param = None
    if system:
        if cache_system:
            system_param = [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}]
        else:
            system_param = system

    for intento in range(1, _REINTENTOS_MAX + 1):
        try:
            kwargs = dict(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": user_content}],
            )
            if system_param is not None:
                kwargs["system"] = system_param

            message = client.messages.create(**kwargs)
            texto = message.content[0].text.strip()

            # Logging de uso y coste
            u = message.usage
            coste = _calcular_coste(model, u)
            _coste_total += coste
            _llamadas    += 1
            inp = getattr(u, "input_tokens",                0) or 0
            out = getattr(u, "output_tokens",               0) or 0
            cw  = getattr(u, "cache_creation_input_tokens", 0) or 0
            cr  = getattr(u, "cache_read_input_tokens",     0) or 0
            cache_info = ""
            if cw: cache_info += f" cache_write={cw}"
            if cr: cache_info += f" cache_read={cr}"
            print(f"    💰 {model.split('-')[1][:6]} in={inp} out={out}{cache_info} → ${coste:.4f} (total ${_coste_total:.4f})")

            if raw_text:
                return texto

            if texto.startswith("```"):
                texto = "\n".join(texto.splitlines()[1:-1]).strip()

            return json.loads(texto)

        except anthropic.RateLimitError:
            if intento == _REINTENTOS_MAX:
                print(f"  ✗ Rate limit — reintentos agotados")
                return None
            espera = _ESPERA_BASE_429 * (2 ** (intento - 1))
            print(f"  ⏳ Rate limit — esperando {espera}s (intento {intento}/{_REINTENTOS_MAX})...")
            time.sleep(espera)

        except anthropic.APIStatusError as e:
            if e.status_code >= 500:
                if intento == _REINTENTOS_MAX:
                    print(f"  ✗ Error {e.status_code} — reintentos agotados")
                    return None
                espera = _ESPERA_BASE_5XX * (2 ** (intento - 1))
                print(f"  ⏳ Error {e.status_code} — esperando {espera}s...")
                time.sleep(espera)
            else:
                print(f"  ✗ Error API {e.status_code}: {str(e)[:200]}")
                return None

        except json.JSONDecodeError as e:
            if raw_text:
                return texto  # type: ignore[possibly-undefined]
            print(f"  ✗ JSON inválido: {e}")
            return None

        except Exception as e:
            print(f"  ✗ Error inesperado: {e}")
            return None

    return None
