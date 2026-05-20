---
name: redisenar
description: Rediseña el tema visual del digest. Úsalo cuando el usuario pida cambiar colores, estilo, textura o aspecto general. Incluye workflow completo con preview local.
---

# Skill: /redisenar

## Contexto
- CSS en `styles.py` → constante `_CSS`. Este es el ÚNICO archivo a editar para diseño.
- `renderer.py` importa `_CSS` desde `styles.py`.
- Preview local en `localhost:5001` con botón 🔄 (servidor `preview.py`).
- Ver `diseño.md` en rules/ para el sistema de diseño completo y colores hardcodeados.

## Proceso obligatorio

### 1. Leer el estado actual
```
Leer styles.py completo antes de editar — nunca editar a ciegas.
```

### 2. Si el usuario pide referencias o inspiración
Buscar en web: `"best designed news websites 2025"`, `"news app UI design"`.
Presentar 4-6 opciones con descripción del estilo visual, NO solo el nombre.
Esperar confirmación antes de implementar.

### 3. Actualizar variables `:root` primero
Casi todos los colores usan estas variables. Una buena paleta en `:root` propaga el cambio al 80% del UI.

### 4. Actualizar colores hardcodeados
Ver la tabla completa en `.claude/rules/diseño.md`. Los más comunes:
- `.analisis-general`, `.critica`, `.drawer-critica` → bg, border, color
- `.header-logo .icono`, `.seccion-acento` → gradiente
- Hover shadows → cambiar `rgba(R,G,B,...)` con los nuevos valores RGB del acento
- `.tab-bar::before` → si cambia el nombre/branding
- `#ia-banner` → bg, border, color, botón

### 5. NO tocar (salvo petición explícita)
- `#tab-libertaria` → acento rojo `#dc2626`
- `.asombro-*` → acento violeta `#7c3aed`
- `#tab-libertaria .tab-btn.active` → `border-left-color: #dc2626`
- `.tab-btn[data-tab="asombro"].active` → `border-left-color: #7c3aed`

### 6. Validar
```powershell
python -c "import renderer; print('OK')"
```

### 7. Ver el resultado (sin gastar tokens)
Decirle al usuario: "Pulsa 🔄 en localhost:5001 para ver el cambio."
Solo tomar screenshot si el usuario lo pide o hay un problema que diagnosticar.

Si necesito screenshot:
```python
import urllib.request
urllib.request.urlopen('http://localhost:5001/regen')  # regenerar primero
# Luego Playwright desde http://localhost:5001
```

### 8. Commit
```powershell
git add styles.py
git commit -m "Rediseno tema <nombre>: <descripcion>

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
git push origin master
```

## Contraste mínimo
- Texto principal sobre fondo: ratio ≥ 4.5:1
- Texto muted (`--txt-3`): ratio ≥ 3:1 sobre `--bg`
- Nunca color claro sobre fondo blanco/crema

## Variaciones posibles desde el tema actual
- **Noche**: `--bg: #0f0f0f`, surface oscuro, acento verde o dorado
- **Periódico clásico**: blanco puro, negro, gris, cambiar `--font-serif` a fuente mono
- **Primavera**: `--accent` a rosa/lavanda, bg a blanco puro
- **Invierno**: azules grisáceos, `--accent` a azul pizarra
- **Contraste alto**: bg blanco puro `#ffffff`, txt-1 negro puro `#000000`
