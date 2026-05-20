---
description: Sistema de diseño del digest de noticias. Cargado automáticamente en cada sesión.
---

# Sistema de diseño — Digest de Noticias

## Arquitectura de archivos CSS
- **`styles.py`** — TODO el CSS en la constante `_CSS`. Este es el único archivo a editar para diseño.
- **`renderer.py`** — Importa `_CSS` desde `styles.py`. Contiene lógica Python y plantilla HTML.
- **`preview.py`** — Servidor local en `localhost:5001`. Botón 🔄 para regenerar sin tokens.

## Workflow de iteración de diseño (sin gastar tokens)
1. Editar `styles.py`
2. El usuario pulsa **🔄 Regenerar** en `localhost:5001`
3. El usuario describe lo que ve → yo ajusto
4. Solo tomar screenshot con Playwright cuando sea necesario para diagnóstico

Si necesito screenshot manual:
```python
from playwright.sync_api import sync_playwright
# Regenerar primero: urllib.request.urlopen('http://localhost:5001/regen')
# Luego screenshot desde http://localhost:5001 (no desde file://)
```

## Tema actual: Bosque Otoñal (estilo Axios)

### Paleta CSS (variables en `:root` de `styles.py`)
```css
--bg:          #f4f1eb;   /* blanco cálido casi imperceptible */
--surface:     #ffffff;   /* blanco puro para cards */
--surface-2:   #f0ece4;   /* hover muy sutil */
--border:      #d0c9bf;   /* borde visible cálido */
--border-sub:  #e6e0d8;   /* borde sutil */
--txt-1:       #1a1208;   /* casi negro cálido */
--txt-2:       #4a3828;   /* marrón medio */
--txt-3:       #8a7868;   /* marrón muted */
--accent:      #2d5a2d;   /* verde bosque — principal */
--accent-blue: #5a4030;   /* marrón tierra */
--accent-green:#557820;   /* olivo */
--accent-gold: #a06010;   /* ámbar oscuro */
--font-serif:  'Playfair Display', Georgia, serif;
```

### Filosofía de diseño (Axios-style)
- Fondo casi blanco, cards blancas puras
- Sin texturas ni decoraciones excesivas
- Mucho espacio en blanco — el espacio ES el diseño
- Tipografía serif (Playfair Display) solo para titulares
- Verde bosque como único acento de color
- Sombras suaves con color de acento (no grises planos)

## Layout — Sidebar de navegación
El `.tab-bar` es un sidebar fijo a la izquierda (210px). Todo el contenido tiene `margin-left: 210px`.

### Sticky top values (con sidebar, sin tab-bar horizontal):
- `header`: `top: 0`
- `.search-bar`: `top: 64px`
- `.sort-bar`: `top: 64px`
- `#cat-nav`: `top: 105px`

### Mobile: sidebar se convierte en barra horizontal inferior (fixed bottom).

## Colores hardcodeados en `styles.py` (actualizar al cambiar paleta)
Estos NO usan variables CSS — hay que cambiarlos manualmente:

| Selector | Propiedades |
|---|---|
| `.analisis-general` | `background: #edf5ed; border: 1px solid #9cc89c; color: #1a3a1a` |
| `.critica` | `background: #edf5ed; border: 1px solid #9cc89c; color: #1a3a1a` |
| `.drawer-critica` | `background: #edf5ed; border: 1px solid #9cc89c; color: #1a3a1a` |
| `.header-logo .icono` | `background: linear-gradient(135deg, #2d5a2d, #557820)` |
| `.seccion-acento` | `background: linear-gradient(180deg, #557820, #2d5a2d)` |
| `.tarjeta:hover` | `box-shadow: rgba(45,90,45,...)` |
| `.tarjeta-destacada:hover` | `box-shadow: rgba(45,90,45,...)` |
| `.sintesis-card:hover` | `box-shadow: rgba(45,90,45,...)` |
| `.sintesis-fuentes-count` | `background: #e8f0e8; border: 1px solid #9cc89c` |
| `.drawer-btn-primary:hover` | `background: #1b3d1b` |
| `.drawer-btn-translate` | `background: #e8f5e8; color: #2d5a2d; border: 1px solid #9cc89c` |
| `.badge-sent-optimista` | `background: #e8f5e8; color: #2d5a2d` |
| `.badge-verified` | `background: #e8f0e0; color: #2d5a2d; border: 1px solid #8ab48a` |
| `.tab-bar::before` | branding del sidebar |
| `nav` | `background: rgba(244,241,235,0.97)` |
| `#ia-banner` | `background: #f0f8f0; border: 1px solid #9cc89c; color: #1a3a1a` |
| `#ia-banner .ia-regen` | `background: #2d5a2d` |
| `stat-kpi-valor` | gradient `var(--accent) → var(--accent-green)` |

## Secciones con acento propio (NO cambiar salvo petición explícita)
- `#tab-libertaria` → acento rojo `#dc2626`
- `.asombro-*` → acento violeta `#7c3aed`

## Validación antes de commit
```powershell
python -c "import renderer; print('OK')"
python -c "
import renderer
html = renderer.renderizar_html({}, {}, {}, {}, [])
print(len(html), 'chars, CSS OK:', '--bg' in html)
"
```

## Commit de diseño
```powershell
git add styles.py
git commit -m "Rediseno tema <nombre>: <descripcion breve>

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
git push origin master
```

## Referencias de diseño consultadas
- **Axios** — minimalismo extremo, mucho espacio, sans-serif limpia, muy pocos elementos
- **The Atlantic** — serif editorial, rojo único acento, blanco y negro
- **Rest of World** — tres typefaces con roles distintos, alto contraste
- **Morning Brew** — bloques visuales separados, muy escaneable
- **The Pudding** — data visual, ilustrativo, vibrante

## Principios de diseño probados en este proyecto
1. **Serif solo en titulares** — el mayor salto de calidad visual por el menor esfuerzo
2. **Sombras con color de acento** (no grises) — más profesional, más cohesivo
3. **Sidebar izquierdo** — más moderno que tab bar horizontal para apps de contenido
4. **Cards blancas sobre fondo cálido** — la separación figura/fondo ayuda a leer
5. **Menos elementos, más espacio** — cada elemento eliminado mejora el conjunto
