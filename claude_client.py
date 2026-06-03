"""
claude_client.py — Cliente Anthropic / Gemini unificado con retry, prompt caching y logging de coste.

Determina el uso de Gemini o Claude basándose en las variables de entorno configuradas.
Si GEMINI_API_KEY está configurada, realiza llamadas directas a la API REST de Gemini (2.0-flash),
evitando cargos en la API de Anthropic. Mantiene compatibilidad total con el resto de módulos.
"""

import json
import time
import requests
import anthropic

from config import ANTHROPIC_API_KEY, GEMINI_API_KEY

_REINTENTOS_MAX  = 4
_ESPERA_BASE_429 = 15
_ESPERA_BASE_5XX = 5

_client: anthropic.Anthropic | None = None

# Acumulador de coste para la generación en curso (en dólares).
# Se reinicia al llamar reset_coste().
_coste_total: float = 0.0
_llamadas:    int   = 0

# Precios por millón de tokens (MTok) — mayo/junio 2026
_PRECIOS: dict[str, dict[str, float]] = {
    "claude-haiku-4-5-20251001": {
        "input":          0.80,   # $/MTok
        "output":         4.00,
        "cache_write":    1.00,
        "cache_read":     0.08,
    },
    "claude-sonnet-4-6": {
        "input":          3.00,
        "output":        15.00,
        "cache_write":    3.75,
        "cache_read":     0.30,
    },
    "gemini-2.0-flash": {
        "input":          0.075,  # $/MTok (Tarifa de pago por uso de Gemini Flash)
        "output":         0.300,
        "cache_write":    0.0,
        "cache_read":     0.0,
    }
}
_PRECIOS_DEFAULT = {"input": 3.00, "output": 15.00, "cache_write": 3.75, "cache_read": 0.30}


def _calcular_coste(model: str, usage) -> float:
    p = _PRECIOS.get(model, _PRECIOS_DEFAULT)
    inp   = getattr(usage, "input_tokens",                0) or 0
    out   = getattr(usage, "output_tokens",               0) or 0
    cw    = getattr(usage, "cache_creation_input_tokens", 0) or 0
    cr    = getattr(usage, "cache_read_input_tokens",     0) or 0
    return (inp * p["input"] + out * p["output"] +
            cw  * p["cache_write"] + cr * p["cache_read"]) / 1_000_000


def reset_coste() -> None:
    global _coste_total, _llamadas
    _coste_total = 0.0
    _llamadas    = 0


def resumen_coste() -> str:
    return f"${_coste_total:.6f} en {_llamadas} llamada(s)"


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


def _llamar_anthropic(
    user_content: str,
    system: str | None,
    model: str,
    max_tokens: int,
    temperature: float,
    cache_system: bool,
    raw_text: bool,
) -> dict | str | None:
    """Rama interna: llama directamente a la API de Anthropic/Claude."""
    global _coste_total, _llamadas
    client = get_client()
    if not client:
        print("  ✗ No hay ANTHROPIC_API_KEY configurada")
        return None

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
            if not message.content:
                print("  ✗ Respuesta vacía de Claude")
                return None
            texto = message.content[0].text.strip()

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
            print(f"    💰 {model.split('-')[1][:6]} in={inp} out={out}{cache_info} -> ${coste:.4f} (total ${_coste_total:.4f})")

            if raw_text:
                return texto
            if texto.startswith("```"):
                texto = "\n".join(texto.splitlines()[1:-1]).strip()
            return json.loads(texto)

        except anthropic.RateLimitError:
            if intento == _REINTENTOS_MAX:
                print("  ✗ Claude Rate limit — reintentos agotados")
                return None
            espera = _ESPERA_BASE_429 * (2 ** (intento - 1))
            print(f"  Esperando {espera}s por rate limit de Claude...")
            time.sleep(espera)

        except anthropic.APIStatusError as e:
            if e.status_code >= 500:
                if intento == _REINTENTOS_MAX:
                    print(f"  ✗ Claude Error {e.status_code} — reintentos agotados")
                    return None
                espera = _ESPERA_BASE_5XX * (2 ** (intento - 1))
                print(f"  Esperando {espera}s por error {e.status_code} de Claude...")
                time.sleep(espera)
            else:
                print(f"  ✗ Claude API {e.status_code}: {str(e)[:200]}")
                return None

        except json.JSONDecodeError as e:
            if raw_text:
                return texto
            print(f"  ✗ JSON invalido de Claude: {e}")
            return None

        except Exception as e:
            print(f"  ✗ Error inesperado en Claude: {e}")
            return None

    return None


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
    Llama a Gemini si hay clave disponible; si falla fatalmente, cae a Claude.
    Devuelve el JSON parseado (o str si raw_text=True).
    """
    global _coste_total, _llamadas
    from config import CLAUDE_MODEL_ANALISIS, ANTHROPIC_API_KEY, GEMINI_API_KEY

    usar_gemini = bool(GEMINI_API_KEY and GEMINI_API_KEY != "TU_API_KEY_AQUI")
    model = model or CLAUDE_MODEL_ANALISIS

    # Modelo Claude de fallback: si el caller pasó un modelo Gemini, usamos CLAUDE_MODEL_ANALISIS
    from config import CLAUDE_MODEL_ANALISIS as _CLAUDE_ANALISIS
    claude_model = _CLAUDE_ANALISIS if "gemini" in model.lower() else model

    if usar_gemini:
        # Mapear modelos heredados de Claude a Gemini
        if "claude" in model.lower():
            model = "gemini-2.0-flash"

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}

        # Estructurar payload REST para Gemini
        payload = {
            "contents": [{"parts": [{"text": user_content}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}

        # Forzar JSON nativo de Gemini si se espera estructurado
        if not raw_text:
            payload["generationConfig"]["responseMimeType"] = "application/json"

        gemini_ok = False
        for intento in range(1, _REINTENTOS_MAX + 1):
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=60)

                # Error fatal de autenticación/autorización — no reintentar, ir a Claude
                if resp.status_code in (401, 403):
                    print(f"  ✗ Gemini auth error {resp.status_code} — cambiando a Claude")
                    break

                if resp.status_code == 429:
                    if intento == _REINTENTOS_MAX:
                        print("  ✗ Gemini Rate limit agotado — cambiando a Claude")
                        break
                    espera = _ESPERA_BASE_429 * (2 ** (intento - 1))
                    print(f"  Gemini Rate limit — esperando {espera}s (intento {intento}/{_REINTENTOS_MAX})...")
                    time.sleep(espera)
                    continue

                if resp.status_code >= 500:
                    if intento == _REINTENTOS_MAX:
                        print(f"  ✗ Gemini Error {resp.status_code} agotado — cambiando a Claude")
                        break
                    espera = _ESPERA_BASE_5XX * (2 ** (intento - 1))
                    print(f"  Gemini Error {resp.status_code} — esperando {espera}s...")
                    time.sleep(espera)
                    continue

                resp.raise_for_status()
                resp_json = resp.json()

                try:
                    texto = resp_json["candidates"][0]["content"]["parts"][0]["text"].strip()
                except (KeyError, IndexError):
                    print("  ✗ Estructura de respuesta de Gemini inesperada — cambiando a Claude")
                    break

                usage = resp_json.get("usageMetadata", {})
                inp = usage.get("promptTokenCount", 0)
                out = usage.get("candidatesTokenCount", 0)
                p_gemini = _PRECIOS.get(model, _PRECIOS["gemini-2.0-flash"])
                coste = (inp * p_gemini["input"] + out * p_gemini["output"]) / 1_000_000
                _coste_total += coste
                _llamadas += 1
                print(f"    [Gemini] {model} in={inp} out={out} -> ${coste:.6f} (total ${_coste_total:.6f})")

                if raw_text:
                    return texto
                if texto.startswith("```"):
                    lineas = texto.splitlines()
                    texto = "\n".join(lineas[1:-1]).strip()
                gemini_ok = True
                return json.loads(texto)

            except requests.exceptions.RequestException as e:
                print(f"  ✗ Error de red en Gemini: {e}")
                if intento == _REINTENTOS_MAX:
                    print("  -> Cambiando a Claude como fallback")
                    break
                time.sleep(2)
                continue
            except json.JSONDecodeError as e:
                if raw_text:
                    return texto
                print(f"  ✗ JSON de Gemini invalido: {e} — cambiando a Claude")
                break
            except Exception as e:
                print(f"  ✗ Error inesperado en Gemini: {e} — cambiando a Claude")
                break

        if gemini_ok:
            return None  # ya retornó arriba

        # --- Fallback a Claude ---
        if not ANTHROPIC_API_KEY:
            print("  ✗ Sin fallback: ANTHROPIC_API_KEY no configurada")
            return None
        print(f"  -> Fallback a Claude ({claude_model})")
        return _llamar_anthropic(user_content, system, claude_model, max_tokens, temperature, cache_system, raw_text)

    else:
        # Sin Gemini — usar Claude directamente
        return _llamar_anthropic(user_content, system, model, max_tokens, temperature, cache_system, raw_text)
