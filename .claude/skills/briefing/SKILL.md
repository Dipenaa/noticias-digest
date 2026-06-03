---
name: briefing
description: Genera un memo de inteligencia de ~300 palabras sobre la situación global actual del digest de noticias. Úsalo cuando quieras un resumen ejecutivo del día en formato PDB (President's Daily Brief).
---

Genera un memo de situación en estilo **PDB — President's Daily Brief** sobre el estado del mundo según el digest de hoy.

## Estructura del memo

**SITUACIÓN GLOBAL**
2-3 frases sobre el panorama macro. No obviedades — qué está caracterizando este momento específico.

**QUÉ CAMBIÓ HOY**
• Desarrollo 1 — concreto, con actor o dato específico
• Desarrollo 2
• Desarrollo 3

**SEÑALES DE ALERTA**
• Proceso o evento que requiere atención especial y por qué
• Segundo si hay otro genuinamente urgente

**QUÉ VIGILAR (próximos 7 días)**
• Indicador concreto: ¿qué evento o dato confirmaría o descartaría una hipótesis?
• Segundo indicador

## Instrucciones de uso

1. Abre el digest en producción: https://noticias-digest.onrender.com
2. Ve a la pestaña **Actualidad**
3. Pulsa el botón **📄 Briefing**
4. El memo aparece en el panel en 15-20 segundos (solo la primera vez del día; el resto sale de caché)

## O desde Claude Code

Si quieres el briefing directamente aquí sin abrir el navegador, llama a la API:

```bash
curl -u :tu-contraseña https://noticias-digest.onrender.com/briefing
```

## Directrices de calidad

- Sin frases genéricas como "el mundo enfrenta desafíos"
- Nombra actores, países, cifras cuando los tengas
- Máximo 340 palabras totales
- Cada bullet debe ser accionable o verificable

## Coste

~0.5-1 céntimo/generación · Modelo: claude-sonnet-4-6 · Caché Redis 12h
