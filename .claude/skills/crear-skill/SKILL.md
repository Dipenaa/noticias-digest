---
name: crear-skill
description: Crea o mejora una skill de Claude Code para este proyecto. Úsalo cuando el usuario quiera automatizar una tarea repetitiva o guardar conocimiento especializado.
disable-model-invocation: false
---

# Skill: /crear-skill

## Qué es una skill
Un archivo `SKILL.md` que Claude lee cuando la tarea coincide con su descripción, o que el usuario invoca con `/nombre-skill`. Actúa como un manual de instrucciones especializado que Claude sigue al pie de la letra.

## Cuándo crear una skill (vs otras opciones)

| Situación | Solución |
|---|---|
| Tarea repetitiva con pasos fijos | **Skill** |
| Conocimiento que Claude necesita siempre | **Rule** (`.claude/rules/`) |
| Info sobre el usuario o proyecto | **Memory** (`~/.claude/projects/.../memory/`) |
| Tarea puntual, no repetitiva | Nada, solo hacerla |

## Estructura de una skill perfecta

```markdown
---
name: nombre-en-kebab-case
description: Una frase que describe QUÉ hace y CUÁNDO usarla. Claude lee esto para decidir si invocar la skill automáticamente.
disable-model-invocation: false   # true = solo el usuario puede invocarla con /nombre
---

# Skill: /nombre

## Contexto
[Qué sabe Claude sobre este proyecto que necesita para ejecutar la skill]
[Rutas de archivos concretas, no genéricas]
[Estado actual del sistema]

## Proceso (pasos numerados y en orden)

### 1. [Primer paso]
[Instrucciones específicas, no genéricas]
[Comandos exactos si aplica]

### 2. [Segundo paso]
...

## Validación
[Cómo verificar que la skill funcionó correctamente]

## Ejemplos
[Casos de uso concretos]
```

## Principios de una skill de calidad

### La descripción es crítica
Claude usa la descripción para decidir cuándo invocar la skill automáticamente. Debe responder:
- ¿Qué hace exactamente?
- ¿Cuándo debe usarse? (trigger conditions)
- ¿Qué NO hace? (límites)

❌ Mala: `"Ayuda con el diseño"`
✅ Buena: `"Rediseña el tema visual del digest. Úsalo cuando el usuario pida cambiar colores, estilo o aspecto general de la web."`

### Rutas absolutas o relativas al proyecto
No escribir "el archivo CSS" — escribir `styles.py` o `C:\ruta\completa\styles.py`.

### Incluir comandos exactos
No "valida el código" — incluir el comando exacto:
```powershell
python -c "import renderer; print('OK')"
```

### Proceso en pasos numerados
Las skills se siguen como un checklist. Pasos ambiguos = resultados inconsistentes.

### Separar conocimiento de proceso
- **Contexto** (arriba): qué necesita saber Claude
- **Proceso** (en medio): qué debe hacer, en orden
- **Validación** (abajo): cómo saber que funcionó

### `disable-model-invocation: true` para skills destructivas
Si la skill hace push a producción, borra archivos, o tiene efectos irreversibles, añadir esta opción para que solo el usuario pueda invocarla con `/nombre`.

## Dónde guardar la skill
```
.claude/skills/<nombre-skill>/SKILL.md
```

## Actualizar CLAUDE.md si la skill es importante
Si la skill es de uso frecuente, mencioarla en CLAUDE.md para que el usuario sepa que existe.

## Proceso para crear una skill nueva

1. **Identificar la tarea** — ¿Qué hace el usuario repetidamente que podría automatizarse?
2. **Definir el trigger** — ¿Cuándo debe invocarse? (automáticamente vs `/comando`)
3. **Documentar el proceso actual** — Cómo se hace hoy, paso a paso
4. **Abstraer el conocimiento** — Qué necesita saber Claude para hacerlo bien
5. **Escribir el SKILL.md** — Siguiendo la estructura de arriba
6. **Probar** — Invocar con `/nombre-skill` y verificar que el resultado es correcto
7. **Iterar** — Añadir casos edge que no estaban cubiertos

## Errores comunes

- **Demasiado genérica** — Una skill que hace "todo" no hace nada bien. Mejor varias skills específicas.
- **Sin contexto del proyecto** — Claude no sabe qué archivos tocar si no se los dices.
- **Proceso ambiguo** — "Mejora el código" no es un paso. "Ejecuta `python -c 'import renderer'`" sí lo es.
- **Sin validación** — Sin un paso de verificación, no sabes si la skill funcionó.
- **Conocimiento volátil** — No guardar en la skill información que cambia frecuentemente (colores actuales, URLs). Eso va en rules/.
