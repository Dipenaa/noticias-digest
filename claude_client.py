"""
claude_client.py — Cliente Anthropic compartido con retry y prompt caching.

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
) -> dict | None:
    """
    Llama a Claude y devuelve el JSON parseado, o None si falla.

    Si cache_system=True, marca el system prompt como cacheable (ephemeral).
    Ahorra tokens en llamadas consecutivas con el mismo system prompt.
    """
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
            print(f"  ✗ JSON inválido: {e}")
            return None

        except Exception as e:
            print(f"  ✗ Error inesperado: {e}")
            return None

    return None
