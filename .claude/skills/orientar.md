# Orientar — bootstrap de sesión

Recupera contexto al inicio de sesión y presenta un resumen accionable.

## Cuándo usarlo
Al empezar cualquier sesión, especialmente en entornos remotos donde la memoria no persiste.

## Qué hacer

1. Leer `context/ultima-sesion.md` si existe — es la memoria de la sesión anterior
2. Ejecutar `git log --oneline -8` para ver cambios recientes
3. Revisar `git status` para detectar trabajo en curso
4. Leer las primeras líneas de `CLAUDE.md` (sección "Estado del proyecto")

## Formato de salida

```
## Orientación — [proyecto] / [fecha]

### Última sesión
[resumen de context/ultima-sesion.md, o "(sin contexto guardado)" si no existe]

### Cambios recientes
[3-5 commits más relevantes]

### Estado actual
[rama, archivos modificados si los hay]

### Pendientes conocidos
[de CLAUDE.md sección Pendiente]

---
¿En qué trabajamos hoy?
```

## Notas
- Si `context/ultima-sesion.md` no existe, hacer bootstrap desde git log y CLAUDE.md
- Mantener el resumen en menos de 30 líneas — es orientación, no análisis
