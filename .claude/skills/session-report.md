# Session Report — resumen de sesión para handoff

Genera un resumen de lo hecho en la sesión, listo para compartir o archivar.

## Cuándo usarlo
Al terminar una sesión. Complementa a `/cierre` — este es el resumen legible, cierre guarda la memoria técnica.

## Qué hacer

1. `git log --oneline master..HEAD` — commits de esta sesión
2. `git diff --stat master..HEAD` — archivos tocados
3. Redactar resumen con el formato de abajo

## Formato de salida

```
## Sesión [FECHA] — [rama]

### Resumen
[2-3 frases describiendo el hilo principal de trabajo]

### Completado
- [tarea] → [archivo(s) afectados]

### Decisiones
- [decisión tomada y por qué]

### Pendiente
- [lo que quedó sin hacer]

### Coste API
[estimado si hubo llamadas Claude]
```

## Notas
- Orientado a ser leído por humano, no por Claude
- Máximo 25 líneas
