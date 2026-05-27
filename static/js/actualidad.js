/* ── Actualidad Absoluta — procesos globales y briefing ──────────────── */
var _historialDias       = 15;
var _procesoEstadoFiltro = 'todos';

var PROCESO_COLORES = {
  'escalada':   '#dc2626',
  'estable':    '#2563eb',
  'resolucion': '#16a34a',
  'silencio':   '#9ca3af'
};

function setHistorialDias(n) {
  _historialDias = n;
  document.querySelectorAll('.historial-filter-btn[data-dias]').forEach(function(b) {
    b.classList.toggle('active', parseInt(b.dataset.dias) === n);
  });
  document.querySelectorAll('.proceso-card, .proceso-card-hero').forEach(function(card) {
    _renderSparkline(card.querySelector('.proceso-sparkline'));
  });
}

function filtrarProcesos(estado, btn) {
  _procesoEstadoFiltro = estado;
  document.querySelectorAll('.historial-filter-btn[data-estado]').forEach(function(b) {
    b.classList.remove('active');
  });
  if (btn) btn.classList.add('active');
  document.querySelectorAll('.proceso-card, .proceso-card-hero').forEach(function(card) {
    var ok = estado === 'todos' || card.dataset.estado === estado;
    card.style.display = ok ? '' : 'none';
  });
}

function _renderSparkline(canvas) {
  if (!canvas || !canvas.getContext) return;
  var card = canvas.closest('[data-historial]');
  if (!card) return;
  var estado = card.dataset.estado || 'estable';
  var color  = PROCESO_COLORES[estado] || '#2563eb';
  var historial;
  try { historial = JSON.parse(card.dataset.historial || '[]'); } catch(e) { historial = []; }
  var slice = historial.slice(-_historialDias);
  var max   = 0;
  slice.forEach(function(d) { if ((d.cobertura||0) > max) max = d.cobertura||0; });
  if (max === 0) max = 1;

  var W = canvas.offsetWidth || canvas.parentElement.clientWidth || 280;
  var H = parseInt(canvas.getAttribute('height')) || 44;
  canvas.width  = W;
  canvas.height = H;

  var ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, W, H);
  if (!slice.length) return;

  var n      = slice.length;
  var gap    = 2;
  var barW   = Math.max(2, Math.floor((W - gap * (n - 1)) / n));

  slice.forEach(function(d, i) {
    var pct  = d.cobertura > 0 ? Math.max(0.08, d.cobertura / max) : 0.04;
    var barH = Math.max(2, Math.round(pct * H));
    var x    = i * (barW + gap);
    var y    = H - barH;
    var r    = Math.min(2, barW / 2);

    ctx.globalAlpha = d.cobertura > 0 ? 0.85 : 0.2;
    ctx.fillStyle   = color;
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + barW - r, y);
    ctx.quadraticCurveTo(x + barW, y, x + barW, y + r);
    ctx.lineTo(x + barW, H);
    ctx.lineTo(x, H);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
    ctx.fill();
  });
  ctx.globalAlpha = 1;
}

(function() {
  document.querySelectorAll('.proceso-card, .proceso-card-hero').forEach(function(card) {
    _renderSparkline(card.querySelector('.proceso-sparkline'));
  });
})();

function generarBriefing() {
  var panel = document.getElementById('briefing-panel');
  var texto = document.getElementById('briefing-texto');
  panel.style.display = 'block';
  while (texto.firstChild) texto.removeChild(texto.firstChild);
  var loading = document.createElement('span');
  loading.style.cssText = 'color:var(--txt-3);font-size:.85rem';
  loading.textContent   = 'Generando memo… puede tardar 15-20 s';
  texto.appendChild(loading);

  fetch('/briefing', {method:'POST'})
    .then(function(r) { return r.json(); })
    .then(function(d) {
      while (texto.firstChild) texto.removeChild(texto.firstChild);
      if (!d.ok) { texto.textContent = d.texto || 'Error'; return; }
      // Renderizar markdown básico con DOM seguro
      var lines = (d.texto || '').split('\n');
      lines.forEach(function(line) {
        if (!line.trim()) { texto.appendChild(document.createElement('br')); return; }
        var p = document.createElement('p');
        // Negrita **texto**
        line = line.replace(/\*\*(.+?)\*\*/g, function(_, t) {
          return '<BOLD>' + t + '</BOLD>';
        });
        // Bullet •
        line = line.replace(/^• /, '');
        // Reconstruir con nodos
        var parts = line.split(/<BOLD>|<\/BOLD>/);
        parts.forEach(function(part, i) {
          if (i % 2 === 1) {
            var strong = document.createElement('strong');
            strong.textContent = part;
            p.appendChild(strong);
          } else {
            p.appendChild(document.createTextNode(part));
          }
        });
        texto.appendChild(p);
      });
    })
    .catch(function() {
      while (texto.firstChild) texto.removeChild(texto.firstChild);
      texto.textContent = 'No disponible — inicia el servidor Flask para generar el briefing.';
    });
}

function lanzarAnalisisIA() {
  var btn = document.getElementById('ia-regen-btn');
  btn.disabled    = true;
  btn.textContent = 'Analizando…';
  fetch('/analizar', {method:'POST'})
    .then(function(r) {
      if (!r.ok) throw new Error('no-endpoint');
      return r.json();
    })
    .then(function() {
      btn.textContent = 'Esperando resultado…';
      var poll = setInterval(function() {
        fetch('/estado').then(function(r) { return r.json(); }).then(function(s) {
          if (!s.generando) { clearInterval(poll); window.location.reload(); }
        }).catch(function() { clearInterval(poll); window.location.reload(); });
      }, 4000);
    })
    .catch(function() {
      window.location.href = '/regenerar';
    });
}

function generarSintesis() {
  var btn = document.getElementById('btn-sintetizar');
  var est = document.getElementById('sintesis-estado');
  btn.disabled    = true;
  btn.textContent = 'Generando…';
  est.style.display = 'block';
  var tsAntes = null;
  fetch('/estado').then(function(r) { return r.json(); }).then(function(s) {
    tsAntes = s.ultimo_update;
    return fetch('/sintetizar', {method:'POST'});
  }).then(function() {
    var poll = setInterval(function() {
      fetch('/estado').then(function(r) { return r.json(); }).then(function(s) {
        if (s.ultimo_update !== tsAntes) { clearInterval(poll); window.location.reload(); }
      }).catch(function() { clearInterval(poll); window.location.reload(); });
    }, 3000);
  }).catch(function() {
    est.textContent  = 'Error al conectar con el servidor.';
    btn.disabled     = false;
    btn.textContent  = 'Reintentar';
  });
}
