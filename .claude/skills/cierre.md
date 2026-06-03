# Cierre — guardar estado de sesión

Guarda un resumen estructurado de la sesión en `context/ultima-sesion.md` para que la próxima sesión pueda retomar sin perder contexto.

## Cuándo usarlo
Al terminar cualquier sesión de trabajo. Equivale a hacer un "handoff" a tu yo futuro.

## Qué hacer

1. Revisar `git log --oneline master..HEAD` para ver qué se hizo en esta sesión
2. Revisar el historial de conversación para identificar decisiones tomadas
3. Escribir `context/ultima-sesion.md` con el formato de abajo
4. Hacer commit del archivo: `git add context/ultima-sesion.md && git commit -m "context: cierre de sesión [fecha]"`

## Formato de `context/ultima-sesion.md`

```markdown
# Última sesión — [FECHA]

## Qué se hizo
- [bullet por tarea completada, con archivo afectado si aplica]

## Decisiones tomadas
- [decisiones de diseño, arquitectura o prioridad que no están en el código]

## En curso / sin terminar
- [tareas que quedaron a medias, con contexto suficiente para retomar]

## Próximos pasos sugeridos
- [1-3 cosas concretas para la próxima sesión]

## Coste API estimado
[si hubo llamadas a Claude, el total aproximado]
```

## Notas
- Ser concreto: "edité renderer/shell.py línea 45" es más útil que "trabajé en el renderer"
- Si no hubo trabajo técnico (solo conversación), igualmente guardar las decisiones y pendientes
- Máximo 40 líneas — si es más largo, resumir
