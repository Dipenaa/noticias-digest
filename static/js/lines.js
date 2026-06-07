/* ── Líneas de periódico — barrido continuo + borde de tabs ─────── */

var ns = 'http://www.w3.org/2000/svg';

function rndInt(a, b) { return Math.floor(a + Math.random() * (b - a + 1)); }

function randomizeTitulos(container) {
  (container || document).querySelectorAll('.grid').forEach(function(grid) {
    var titulo   = grid.querySelector('.grid-titulo-celda');
    if (!titulo) return;
    var tarjetas = Array.from(grid.querySelectorAll(':scope > .tarjeta'));
    if (tarjetas.length < 2) return;
    var newPos = 1 + Math.floor(Math.random() * Math.min(tarjetas.length - 1, 4));
    grid.removeChild(titulo);
    var ref = tarjetas[newPos];
    if (ref && ref.parentNode === grid) grid.insertBefore(titulo, ref);
    else grid.appendChild(titulo);
    titulo.setAttribute('data-titulo-pos', newPos);
  });
}

function drawGridLines(container) {
  var isLight = document.body.classList.contains('light');
  var rgb     = isLight ? '30,22,12'  : '255,248,235';
  var maxOp   = isLight ? 0.90        : 0.85;

  /* Todos los grids de todas las pestañas */
  var sel = '.grid, .grid-destacadas, .sintesis-grid, .asombro-grid, .proceso-grid';

  (container || document).querySelectorAll(sel).forEach(function(grid, gi) {
    var old = grid.querySelector('.grid-lines-svg');
    if (old) old.remove();

    var cells = Array.from(grid.querySelectorAll(
      '.tarjeta, .tarjeta-destacada, .grid-titulo-celda, ' +
      '.sintesis-card, .asombro-card, .proceso-strip'
    ));
    if (cells.length < 2) return;

    grid.style.position = 'relative';
    var gRect = grid.getBoundingClientRect();
    var W = grid.offsetWidth, H = grid.offsetHeight;
    if (!W || !H) return;

    /*
     * Detectar TODAS las líneas de borde de cada celda:
     *   - lx > MIN  → borde izquierdo (evita falsos interiores en celdas hero)
     *   - ty > MIN, no título → borde superior (se omite en título para no duplicar)
     *   - by        → borde inferior (nuevo: todos los bordes de cada fila)
     * El borde derecho del último column se añade como x=W al final.
     * Deduplicación por posición exacta (bordes compartidos = una sola línea).
     */
    var seenX = {}, seenY = {}, lineDefs = [];
    var MIN = 8;

    cells.forEach(function(cell) {
      var cr       = cell.getBoundingClientRect();
      var lx       = Math.round(cr.left   - gRect.left);
      var ty       = Math.round(cr.top    - gRect.top);
      var by       = Math.round(cr.bottom - gRect.top);
      var isTitle  = cell.classList.contains('grid-titulo-celda');

      if (lx > MIN && !seenX[lx]) { seenX[lx] = 1; lineDefs.push({ dir: 'v', x: lx }); }
      /* La línea ARRIBA del título la aporta el borde inferior de la fila anterior */
      if (ty > MIN && !isTitle && !seenY[ty]) { seenY[ty] = 1; lineDefs.push({ dir: 'h', y: ty }); }
      /* Borde inferior de cada celda → cards sin vecino abajo también tienen línea */
      if (!seenY[by]) { seenY[by] = 1; lineDefs.push({ dir: 'h', y: by }); }
    });

    /* Borde derecho del grid — cards sin vecino a la derecha también tienen línea */
    if (!seenX[W]) { seenX[W] = 1; lineDefs.push({ dir: 'v', x: W }); }

    if (!lineDefs.length) return;

    /* ── SVG ── */
    var PAD = 200;
    var svgW = W + PAD * 2, svgH = H + PAD * 2;
    var svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('class', 'grid-lines-svg');
    svg.setAttribute('viewBox', (-PAD) + ' ' + (-PAD) + ' ' + svgW + ' ' + svgH);
    svg.setAttribute('width',  svgW);
    svg.setAttribute('height', svgH);
    svg.style.cssText = [
      'position:absolute', 'top:-' + PAD + 'px', 'left:-' + PAD + 'px',
      'pointer-events:none', 'overflow:visible', 'z-index:2'
    ].join(';');
    var defs = document.createElementNS(ns, 'defs');
    svg.appendChild(defs);

    function makeGrad(id, x1, y1, x2, y2) {
      var g = document.createElementNS(ns, 'linearGradient');
      g.setAttribute('id', id);
      g.setAttribute('gradientUnits', 'userSpaceOnUse');
      g.setAttribute('x1', x1); g.setAttribute('y1', y1);
      g.setAttribute('x2', x2); g.setAttribute('y2', y2);
      [[0,0],[0.07,maxOp],[0.93,maxOp],[1,0]].forEach(function(p) {
        var s = document.createElementNS(ns, 'stop');
        s.setAttribute('offset', (p[0]*100) + '%');
        s.setAttribute('stop-color', 'rgb(' + rgb + ')');
        s.setAttribute('stop-opacity', p[1]);
        g.appendChild(s);
      });
      return g;
    }

    /* ── Coordenadas con extensión orgánica (fijadas al crear, no cambian) ── */
    function coordsV(x) {
      var y1 = -rndInt(20, 130);
      var y2 = H + rndInt(20, 130);
      if (Math.random() < 0.35)
        y2 = Math.round(y1 + (y2 - y1) * (0.35 + Math.random() * 0.5));
      return { x1: x, y1: y1, x2: x, y2: y2, len: Math.abs(y2 - y1) };
    }

    function coordsH(y) {
      /* 25% de las horizontales cruzan toda la pantalla */
      var fullPage = Math.random() < 0.25;
      var x1 = fullPage ? Math.round(-gRect.left - 60) : -rndInt(20, 100);
      var x2 = fullPage ? Math.round(window.innerWidth - gRect.left + 60)
                        : W + rndInt(20, 100);
      return { x1: x1, y1: y, x2: x2, y2: y, len: x2 - x1 };
    }

    /* ── Crear elementos ── */
    var lineEls = [];
    lineDefs.forEach(function(ld, i) {
      var gid   = 'lg' + gi + '_' + i;
      var coords = ld.dir === 'v' ? coordsV(ld.x) : coordsH(ld.y);
      var len   = coords.len;

      defs.appendChild(makeGrad(gid, coords.x1, coords.y1, coords.x2, coords.y2));

      var el = document.createElementNS(ns, 'line');
      el.setAttribute('x1', coords.x1); el.setAttribute('y1', coords.y1);
      el.setAttribute('x2', coords.x2); el.setAttribute('y2', coords.y2);
      el.setAttribute('stroke', 'url(#' + gid + ')');
      el.setAttribute('stroke-width', '2');
      el.setAttribute('stroke-linecap', 'round');
      el.setAttribute('stroke-dasharray', len);
      el.setAttribute('stroke-dashoffset', len); /* empieza invisible */
      svg.appendChild(el);

      lineEls.push({ el: el, len: len, i: i });
    });

    grid.appendChild(svg);

    /* ── Animación inicial: cada línea se dibuja ── */
    requestAnimationFrame(function() {
      requestAnimationFrame(function() {
        lineEls.forEach(function(item) {
          var dur   = rndInt(600, 1100);
          var delay = item.i * rndInt(40, 80);
          item.el.style.transition =
            'stroke-dashoffset ' + dur + 'ms ease-out ' + delay + 'ms';
          item.el.setAttribute('stroke-dashoffset', '0');
        });
      });
    });

    /*
     * TODAS las líneas animan, pero escalonadas para que nunca estén
     * todas fuera a la vez. Cada línea descansa ~22-34s (visible) y
     * luego barre en 5-8s. El stagger distribuye los inicios a lo largo
     * del periodo de descanso, así en cualquier momento solo ~2-4 líneas
     * están barriendo mientras el resto permanece visible.
     */
    var N = lineEls.length || 1;
    lineEls.forEach(function(item) {
      var len     = item.len;
      var drawDur = 600 + item.i * 60;

      /* Stagger: cada línea empieza su primer barrido en un momento
         diferente, distribuido uniformemente más un pequeño jitter */
      var pausaBase = rndInt(22000, 34000);
      var stagger   = Math.round((item.i / N) * pausaBase) + rndInt(0, 1500);

      function barrido() {
        var pausa    = rndInt(22000, 34000);
        var durSwipe = rndInt(5000, 8000);
        var reverse  = Math.random() > 0.5;

        setTimeout(function() {
          item.el.style.transition = 'none';
          item.el.setAttribute('stroke-dashoffset', reverse ? -len : len);
          requestAnimationFrame(function() {
            requestAnimationFrame(function() {
              item.el.style.transition =
                'stroke-dashoffset ' + durSwipe + 'ms ease-in-out';
              item.el.setAttribute('stroke-dashoffset', reverse ? len : -len);
              setTimeout(barrido, durSwipe + 150);
            });
          });
        }, pausa);
      }

      setTimeout(function() {
        var durSwipe = rndInt(5000, 8000);
        item.el.style.transition =
          'stroke-dashoffset ' + durSwipe + 'ms ease-in-out';
        item.el.setAttribute('stroke-dashoffset', -len);
        setTimeout(barrido, durSwipe + 150);
      }, drawDur + stagger);
    });
  });
}

/* ── Líneas reactivas al hover de tarjetas ───────────────────────
 * Al pasar el cursor sobre una tarjeta, las líneas SVG que tocan
 * sus bordes se activan una a una (generativo, escalonado).
 * Al salir, vuelven a su estado normal.
 */
var _GRID_SEL = '.grid, .grid-destacadas, .sintesis-grid, .asombro-grid, .proceso-grid';
var _CARD_SEL = '.tarjeta, .tarjeta-destacada, .sintesis-card, .asombro-card, .proceso-strip';

function highlightCardLines(card) {
  var grid = card.closest(_GRID_SEL);
  if (!grid) return;
  var svg = grid.querySelector('.grid-lines-svg');
  if (!svg) return;

  var gRect = grid.getBoundingClientRect();
  var cRect = card.getBoundingClientRect();
  var thr   = 5; /* tolerancia en px para detectar qué líneas tocan la celda */

  var cLeft   = Math.round(cRect.left   - gRect.left);
  var cRight  = Math.round(cRect.right  - gRect.left);
  var cTop    = Math.round(cRect.top    - gRect.top);
  var cBottom = Math.round(cRect.bottom - gRect.top);

  var matched = [];
  svg.querySelectorAll('line').forEach(function(el) {
    var x1 = parseFloat(el.getAttribute('x1'));
    var y1 = parseFloat(el.getAttribute('y1'));
    var x2 = parseFloat(el.getAttribute('x2'));
    var y2 = parseFloat(el.getAttribute('y2'));
    var isV = Math.abs(x1 - x2) < 1;

    if (isV) {
      if (Math.abs(x1 - cLeft) < thr || Math.abs(x1 - cRight) < thr) matched.push(el);
    } else {
      if (Math.abs(y1 - cTop) < thr || Math.abs(y1 - cBottom) < thr) matched.push(el);
    }
  });

  /* Token para cancelar timeouts si el cursor sale antes de que terminen */
  var token = {};
  card._hlToken   = token;
  card._hlMatched = matched;

  matched.forEach(function(el, idx) {
    var delay = idx * rndInt(120, 220) + rndInt(0, 100);
    setTimeout(function() {
      if (card._hlToken !== token) return;
      /* Forzar re-draw desde invisible para que siempre sea visible */
      var len = parseFloat(el.getAttribute('stroke-dasharray'));
      el.style.transition = 'none';
      el.setAttribute('stroke-dashoffset', len);
      requestAnimationFrame(function() {
        requestAnimationFrame(function() {
          if (card._hlToken !== token) return;
          el.style.transition = 'stroke-dashoffset 1.2s ease-out';
          el.setAttribute('stroke-dashoffset', '0');
        });
      });
    }, delay);
  });
}

function restoreCardLines(card) {
  card._hlToken   = null;
  card._hlMatched = null;
}

/* ── Borde animado en tabs ────────────────────────────────────────
 * Al activar un tab, dos mitades de borde salen del centro inferior
 * y se encuentran en el centro superior, rodeando el botón.
 */
function initTabLines() {
  /* Esperar un frame para que el DOM haya pintado los badges */
  requestAnimationFrame(function() {
    document.querySelectorAll('.tab-btn').forEach(function(btn) {
      if (btn._tabSvgPaths) return;

      /* getBoundingClientRect captura el tamaño visual real incluyendo badges */
      var rect = btn.getBoundingClientRect();
      var W = Math.ceil(rect.width);
      var H = Math.ceil(rect.height);
      if (!W || !H) return;

      var pad = 1; /* inset para que el stroke no quede cortado en el borde */
      var x0 = pad, y0 = pad, x1 = W - pad, y1 = H - pad;
      var cx  = W / 2;
      var half = (x1 - cx) + (y1 - y0) + (x1 - x0) / 2;

      var svg = document.createElementNS(ns, 'svg');
      svg.setAttribute('class', 'tab-line-svg');
      svg.setAttribute('width',  W);
      svg.setAttribute('height', H);
      svg.style.overflow = 'visible';

      var pR = document.createElementNS(ns, 'path');
      pR.setAttribute('d', 'M'+cx+','+y1+' L'+x1+','+y1+' L'+x1+','+y0+' L'+cx+','+y0);

      var pL = document.createElementNS(ns, 'path');
      pL.setAttribute('d', 'M'+cx+','+y1+' L'+x0+','+y1+' L'+x0+','+y0+' L'+cx+','+y0);

      [pR, pL].forEach(function(p) {
        p.style.stroke = 'var(--txt-1)'; /* negro en modo día, crema en oscuro */
        p.setAttribute('stroke-width', '2');
        p.setAttribute('fill', 'none');
        p.setAttribute('stroke-linecap', 'square');
        p.setAttribute('stroke-dasharray', half);
        p.setAttribute('stroke-dashoffset', half);
        svg.appendChild(p);
      });

      btn.appendChild(svg);
      btn._tabSvgPaths = [pR, pL];
      btn._tabSvgLen   = half;
    });
  });
}

function animateTabLine(name) {
  /* Ocultar todas */
  document.querySelectorAll('.tab-btn').forEach(function(btn) {
    if (!btn._tabSvgPaths) return;
    btn._tabSvgPaths.forEach(function(p) {
      p.style.transition = 'none';
      p.setAttribute('stroke-dashoffset', btn._tabSvgLen);
    });
  });

  /* Animar el activo */
  var activeBtn = document.querySelector('.tab-btn[data-tab="' + name + '"]');
  if (!activeBtn || !activeBtn._tabSvgPaths) return;

  requestAnimationFrame(function() {
    requestAnimationFrame(function() {
      activeBtn._tabSvgPaths.forEach(function(p) {
        p.style.transition = 'stroke-dashoffset 0.85s cubic-bezier(0.22, 1, 0.36, 1)';
        p.setAttribute('stroke-dashoffset', '0');
      });
    });
  });
}
