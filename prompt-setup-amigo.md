# Prompt de setup — pégalo en tu primera sesión de Claude Code

---

Hola. Eres Claude Code y acabas de abrirte en mi dispositivo. Quiero que configures mi entorno de trabajo exactamente como te voy a describir. Hazlo todo sin preguntarme nada, en orden, y al final dime qué has creado.

## Lo que tienes que hacer

### 1. Crear el stop hook de git

Crea el archivo `~/.claude/stop-hook-git-check.sh` con este contenido exacto:

```bash
#!/bin/bash

input=$(cat)

stop_hook_active=$(echo "$input" | jq -r '.stop_hook_active')
if [[ "$stop_hook_active" = "true" ]]; then
  exit 0
fi

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  exit 0
fi

if [[ -z "$(git remote)" ]]; then
  exit 0
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Hay cambios sin commitear. Por favor haz commit y push antes de terminar." >&2
  exit 2
fi

untracked_files=$(git ls-files --others --exclude-standard)
if [[ -n "$untracked_files" ]]; then
  echo "Hay archivos sin trackear. Por favor haz commit y push antes de terminar." >&2
  exit 2
fi

current_branch=$(git branch --show-current)
if [[ -n "$current_branch" ]]; then
  if git rev-parse "origin/$current_branch" >/dev/null 2>&1; then
    unpushed=$(git rev-list "origin/$current_branch..HEAD" --count 2>/dev/null) || unpushed=0
    if [[ "$unpushed" -gt 0 ]]; then
      echo "Tienes $unpushed commit(s) sin pushear en '$current_branch'. Haz push antes de terminar." >&2
      exit 2
    fi
  else
    unpushed=$(git rev-list "origin/HEAD..HEAD" --count 2>/dev/null) || unpushed=0
    if [[ "$unpushed" -gt 0 ]]; then
      echo "La rama '$current_branch' tiene $unpushed commit(s) sin pushear. Haz push." >&2
      exit 2
    fi
  fi
fi

exit 0
```

Luego dale permisos de ejecución: `chmod +x ~/.claude/stop-hook-git-check.sh`

---

### 2. Configurar settings.json

Crea o actualiza `~/.claude/settings.json` con este contenido:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/stop-hook-git-check.sh"
          }
        ]
      }
    ]
  },
  "permissions": {
    "allow": ["Skill"]
  }
}
```

---

### 3. Crear el skill /crear-skill (dentro del proyecto actual)

Crea el archivo `.claude/skills/crear-skill/SKILL.md` con este contenido:

```markdown
---
name: crear-skill
description: Crea o mejora una skill de Claude Code para este proyecto. Úsalo cuando el usuario quiera automatizar una tarea repetitiva o guardar conocimiento especializado.
---

# Skill: /crear-skill

## Qué es una skill
Un archivo SKILL.md que Claude lee cuando la tarea coincide con su descripción, o que el usuario invoca con /nombre. Actúa como un manual de instrucciones que Claude sigue al pie de la letra.

## Cuándo crear una skill

| Situación | Solución |
|---|---|
| Tarea repetitiva con pasos fijos | Skill |
| Conocimiento que Claude necesita siempre | Rule (.claude/rules/) |
| Info sobre el usuario o proyecto | Memory |
| Tarea puntual, no repetitiva | Nada, solo hacerla |

## Estructura de una skill perfecta

```
---
name: nombre-en-kebab-case
description: Qué hace y cuándo usarla. Claude usa esto para decidir si invocarla automáticamente.
disable-model-invocation: false
---

# Skill: /nombre

## Contexto
[Qué necesita saber Claude sobre el proyecto para ejecutar esta skill]
[Rutas exactas de archivos, no genéricas]

## Proceso
### 1. Primer paso
[Instrucciones específicas con comandos exactos]

### 2. Segundo paso
...

## Validación
[Cómo saber que funcionó]
```

## Principios

- La descripción es crítica — Claude decide cuándo activarse automáticamente leyéndola
- Incluir rutas concretas, no "el archivo CSS" sino `src/styles/main.css`
- Pasos numerados y en orden — ambigüedad = resultados inconsistentes
- `disable-model-invocation: true` para skills que hacen push o borran cosas

## Dónde guardar
`.claude/skills/<nombre>/SKILL.md` — en el repo, se versiona con el código

## Proceso para crear una skill nueva
1. Identificar qué tarea repetitiva quiere automatizar el usuario
2. Documentar cómo se hace hoy, paso a paso
3. Abstraer el conocimiento: qué necesita Claude para hacerlo bien
4. Escribir el SKILL.md siguiendo la estructura de arriba
5. Probar invocando con /nombre-skill
6. Iterar añadiendo casos edge
```

---

### 4. Crear el skill /mejorar-codigo (dentro del proyecto actual)

Crea el archivo `.claude/skills/mejorar-codigo/SKILL.md` con este contenido:

```markdown
---
name: mejorar-codigo
description: Revisa el código del proyecto buscando bugs, deuda técnica, problemas de rendimiento y seguridad. Úsalo cuando el usuario pida revisar, auditar o mejorar la calidad del código.
---

# Skill: /mejorar-codigo

## Proceso

### 1. Análisis inicial
Leer los archivos principales del proyecto. Identificar el lenguaje, framework y arquitectura.

### 2. Buscar en orden de prioridad

**Crítico (arreglar siempre):**
- Race conditions y problemas de thread safety
- Imports duplicados o dentro de funciones (moverlos al top)
- Variables globales modificadas desde múltiples hilos sin lock
- SQL injection, XSS, credenciales hardcodeadas

**Importante:**
- Dependencias circulares entre módulos (A importa B, B importa A)
- Constantes definidas en el módulo equivocado
- Funciones que hacen demasiadas cosas (> 50 líneas, extraer)
- Manejo de errores que falla silenciosamente

**Mejora:**
- Imports inline dentro de funciones que podrían estar arriba
- Código duplicado entre funciones similares
- Comentarios que explican el QUÉ en vez del POR QUÉ

### 3. Implementar los fixes
Arreglar en orden crítico → importante → mejora.
No introducir abstracciones innecesarias.
No añadir features nuevas.

### 4. Validar
Ejecutar los tests si existen. Importar los módulos modificados para verificar que no hay errores de sintaxis.

### 5. Reportar
Decir qué se arregló y por qué, en términos concretos.
```

---

### 5. Crear la rule de buenas prácticas

Crea el archivo `.claude/rules/buenas-practicas.md` con este contenido:

```markdown
---
description: Principios de desarrollo que Claude debe seguir siempre en este proyecto.
---

# Buenas prácticas del proyecto

## Código
- Imports siempre al top del archivo, nunca dentro de funciones
- Sin comentarios que expliquen el QUÉ — el código ya lo dice. Solo comentar el POR QUÉ cuando no es obvio
- Sin features extra que no se pidieron
- Sin manejo de errores para casos que no pueden pasar

## Git
- Commits descriptivos: qué cambió y por qué, no solo qué
- Push siempre a la rama correcta — nunca a main/master sin confirmar
- No usar --no-verify ni --force salvo petición explícita

## Comunicación
- Respuestas cortas y directas
- Si algo es ambiguo, preguntar antes de implementar
- Al terminar: una frase de qué cambió y qué viene después
```

---

## Al terminar

Dime exactamente qué archivos creaste, con sus rutas completas. Si alguno ya existía, dime qué tenía antes y qué tiene ahora.
