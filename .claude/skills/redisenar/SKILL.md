---
name: redisenar
description: Rediseña el tema visual del digest de noticias. Úsalo cuando el usuario pida cambiar colores, estilo, textura o aspecto general de la web.
---

# Skill: redisenar

## Contexto del proyecto
El digest es una app Flask en `C:\Users\Usuario\Desktop\noticias\`.
Todo el CSS está embebido en `renderer.py` — en la constante `_CSS` (string Python multilínea).
No hay archivos CSS externos. No hay framework de estilos. Todo es CSS puro.

## Archivo a modificar
`renderer.py` — solo el bloque `_CSS`. No tocar lógica Python ni JS salvo que el usuario lo pida explícitamente.

## Paleta actual (tema Otoño — referencia para variaciones)
```css
--bg:          #f0e6d3;   /* pergamino otoñal */
--surface:     #faf5ec;   /* papel cálido */
--surface-2:   #e8d9c0;   /* hover / elevado */
--border:      #c4a882;   /* ocre tierra */
--border-sub:  #ddd0b8;   /* borde sutil */
--txt-1:       #2a1a0e;   /* nogal oscuro */
--txt-2:       #6b3f20;   /* corteza marrón */
--txt-3:       #9a7355;   /* siena muted */
--accent:      #b5451b;   /* calabaza / siena tostada */
--accent-blue: #7b5e3a;   /* roble cálido */
--accent-green:#8b7a1e;   /* olivo dorado */
--accent-gold: #d4860a;   /* ámbar */
```

## Proceso obligatorio (en este orden)

1. **Leer renderer.py** completo antes de editar — nunca editar a ciegas.

2. **Actualizar las variables `:root`** primero. Casi todos los colores usan estas variables, así que una buena paleta en `:root` propaga el cambio a casi todo.

3. **Buscar y actualizar colores hardcodeados** que NO usan variables. Los más comunes:
   - `.analisis-general` → `background`, `border`, `color`
   - `.critica` → `background`, `border`, `color`
   - `.drawer-critica` → igual
   - `.header-logo .icono` → gradiente de color
   - `.seccion-acento` → gradiente de color
   - `.tarjeta:hover` → `box-shadow` con color RGBA
   - `.tarjeta-destacada:hover` → igual
   - `.sintesis-card:hover` → igual
   - `.sintesis-fuentes-count` → `background`, `border`
   - `.drawer-btn-primary:hover` → color de hover
   - `.drawer-btn-translate` → `background`, `color`, `border`
   - `.badge-sent-optimista` → `background`, `color`
   - `.badge-verified` → `background`, `color`, `border`
   - `.tab-bar` → `background` hardcodeado
   - `nav` → `background: rgba(...)` hardcodeado
   - `header` → comprobar si usa `var(--surface)` o tiene color fijo
   - `stat-kpi-valor` → gradiente de color
   - `#ia-banner` → colores de fondo/texto/botón

4. **Textura de fondo**: si el usuario pide textura natural (papel, grano, lino, madera), añadirla en `body` con SVG inline:
   ```css
   background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='400'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='400' height='400' filter='url(%23n)' opacity='0.045'/%3E%3C/svg%3E");
   ```
   Ajustar `opacity` (0.02–0.06) y `baseFrequency` (0.6 = grano grueso, 0.9 = grano fino).

5. **Secciones especiales** — tienen acento propio, no romperlas:
   - `#tab-libertaria` → acento rojo (`#dc2626`), no cambiar salvo petición explícita
   - `.asombro-*` → acento violeta (`#7c3aed`), no cambiar salvo petición explícita

6. **Validar** siempre antes de commitear:
   ```powershell
   python -c "import renderer; print('OK')"
   python -c "
   import re, renderer
   html = renderer.renderizar_html({}, {}, {}, {}, [])
   blocks = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
   for i, b in enumerate(blocks):
       open(f'_tj{i}.js','w',encoding='utf-8').write(b)
   print(len(blocks), 'bloques JS')
   "
   node --check _tj0.js; node --check _tj1.js; node --check _tj2.js
   Remove-Item _tj*.js
   ```

7. **Commit y push**:
   ```powershell
   git add renderer.py
   git commit -m @'
   Rediseno tema <nombre>: <descripcion breve>

   Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
   '@
   git push origin master
   ```

## Contraste mínimo
- Texto sobre fondo claro: ratio ≥ 4.5:1
- Texto muted (`--txt-3`): ratio ≥ 3:1 sobre `--bg`
- Nunca usar colores muy claros para texto en fondos blancos/crema

## Ejemplos de variaciones posibles
- **Invierno**: azules grisáceos, hielo, nieve, plateados fríos
- **Primavera**: verdes frescos, rosa pálido, lavanda, flores
- **Verano**: blancos brillantes, turquesa, coral, amarillo sol
- **Noche**: oscuro con toques dorados / índigo profundo
- **Periódico clásico**: blanco puro, negro, gris, serifas (cambiar font-family también)
