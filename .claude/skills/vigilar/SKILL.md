---
name: vigilar
description: Gestiona condiciones de vigilancia en el digest de noticias. Úsalo para añadir o eliminar alertas que aparecerán en el digest cuando se cumpla una condición. Ejemplo: /vigilar "Gaza vuelve a escalar" o /vigilar --listar
---

Sistema de vigilancia del digest. Cada condición que definas se comprueba automáticamente en cada generación del digest. Si se cumple, aparece un banner de alerta naranja en la parte superior del digest.

## Comandos

### Añadir una condición
Describe en lenguaje natural qué quieres vigilar:

```
/vigilar Israel lanza operación terrestre en Líbano
/vigilar La Fed sube los tipos de interés
/vigilar China anuncia operaciones militares en el Estrecho de Taiwán
/vigilar La IA Act europea entra en vigor
```

El sistema comprobará esta condición contra los artículos del día. Si hay evidencia clara (confianza ≥ 70%), aparece la alerta.

### Listar condiciones activas
```
/vigilar --listar
```

### Eliminar una condición
```
/vigilar --eliminar [id]
```

## Cómo funciona

1. Las condiciones se guardan en `~/.noticias-watch.json`
2. Cada vez que se genera el digest, Haiku comprueba cada condición contra los artículos del día
3. Si la confianza supera el 70%, aparece un banner naranja en el digest con la explicación
4. El resultado se cachea 6h (no re-evalúa en regeneraciones del mismo día)

## Instrucciones para Claude

Cuando el usuario invoque `/vigilar`:

1. **Sin argumentos o con texto descriptivo**: es una condición nueva
   - Extrae la condición del mensaje del usuario
   - Llama a `watch.guardar_condicion(condicion)` en el proyecto noticias
   - Confirma: "✓ Condición guardada: [condicion]. Se comprobará en la próxima generación del digest."

2. **Con `--listar`**: muestra las condiciones actuales
   - Lee `~/.noticias-watch.json`
   - Lista cada condición con su id y fecha de creación

3. **Con `--eliminar [id]`**: elimina la condición
   - Llama a `watch.eliminar_condicion(id)`
   - Confirma eliminación

## Coste

~0.05 céntimos por condición por generación · Modelo: claude-haiku-4-5 · Caché 6h
