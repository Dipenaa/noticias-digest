---
name: redisenar
description: >
  AUTO-TRIGGER en cualquier tarea visual sobre la web: bordes, tarjetas, colores, padding,
  layout, CSS, modo claro/oscuro, "se ve mal", "queda raro", "está pegado", "cambia el fondo",
  fix de contraste, nuevo estilo, rediseño parcial o completo. Carga este skill ANTES de tocar
  ningún fichero CSS — define el workflow eficiente (usuario como ojos, sin screenshots).
---

# Skill: /redisenar

## Arquitectura CSS (desde mayo 2026)

El CSS está dividido en 4 ficheros en `static/css/`:

| Fichero | Qué contiene |
|---|---|
| `reset.css` | Variables `:root`, reset, body, modo día (`body.light`), scrollbar |
| `layout.css` | Header, sidebar, nav, search-bar, sort-bar, main, footer, responsive |
| `components.css` | Tarjetas, drawer, badges, botones, splash, silencio, síntesis |
| `animations.css` | Keyframes, hovers, glow, transiciones |

`shell.py` los carga vía `<link rel="stylesheet">` — Flask los sirve desde `/static/css/`.

## Paleta actual (EnPapel)

```css
--bg: #0d0b08          /* fondo oscuro */
--accent: #c8a470      /* dorado arena */
--accent-warm: #c87840 /* terracota */
--txt-1: #f0e8d8       /* crema claro */
--txt-2: #b8a48a       /* crema medio */
--txt-3: #7a6650       /* crema oscuro */
--font-serif: 'Playfair Display', Georgia, serif
```

Modo día en `body.light {}` dentro de `reset.css` — redefine todas las variables y añade overrides para colores hardcodeados.

## Reglas críticas de diseño

- **Sticky elements**: siempre con `background` opaco o semiopaco + `backdrop-filter: blur()`. Nunca `background: transparent` en elementos `position: sticky` — el contenido se cuela por debajo al hacer scroll.
- **Un color de acento**: nunca mezclar morado, verde y dorado. Un acento por diseño.
- **Contraste mínimo**: texto principal ≥ 4.5:1, texto muted ≥ 3:1 sobre `--bg`.
- **Modo día**: si cambias un color hardcodeado (rgba directo, no variable), añade su override en `body.light {}` en `reset.css`.

## Proceso

### 1. Identificar el fichero correcto
Determina cuál de los 4 ficheros contiene el selector a editar. Leerlo completo antes de editar.

### 2. Editar
Cambios quirúrgicos. Si el cambio afecta variables, editar `:root` en `reset.css` primero — se propaga a todo.

### 3. Preview — el usuario es los ojos

El workflow correcto para iterar diseño:

```
Editar CSS → "Refresca localhost:5001 y dime qué ves"
  → Usuario describe problema → ajustar CSS
  → Bug oscuro (no sabe por qué no funciona) → browser_evaluate getComputedStyle
  → Confirmar clase en DOM → python -c + grep, sin browser
```

**NO usar screenshots ni Playwright navigate para ver el resultado visual.**
El usuario tiene el browser abierto — es más barato que cualquier screenshot.

Cuándo sí usar herramientas de browser:
- `browser_evaluate` con `getComputedStyle` → diagnosticar por qué un CSS no aplica
- `browser_evaluate` para leer el DOM cuando el usuario no puede describir la estructura

**Ojo:** `/regen` recarga módulos Python (renderer), pero NO recarga `preview.py`. Si cambias variables en ese fichero, reiniciar el servidor:
```powershell
Get-NetTCPConnection -LocalPort 5001 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
Start-Process python -ArgumentList "preview.py" -WorkingDirectory "c:\Proyectos\noticias" -WindowStyle Hidden
```

### 4. Commit
```powershell
git add static/css/
git commit -m "fix/feat: <descripcion visual breve>"
git push origin master
```

## No tocar salvo petición explícita
- Acento rojo `#dc2626` de Izquierda Crítica (libertaria)
- Acento violeta `#7c3aed` de Asombro
- Tipografía Playfair Display — definida en shell.py como Google Font
