/* ── Estadísticas del digest ─────────────────────────────────────────── */
function _crearBarChart(container, datos, color) {
  if (!container) return;
  while (container.firstChild) container.removeChild(container.firstChild);
  datos.forEach(function(d) {
    var row  = document.createElement('div');
    row.className = 'stat-bar-row';

    var lbl  = document.createElement('span');
    lbl.className   = 'stat-bar-label';
    lbl.textContent = d.label;

    var bg   = document.createElement('div');
    bg.className = 'stat-bar-bg';

    var fill = document.createElement('div');
    fill.className    = 'stat-bar-fill';
    fill.style.width  = d.pct + '%';
    fill.style.background = d.color || color || 'var(--accent)';

    var cnt  = document.createElement('span');
    cnt.className   = 'stat-bar-count';
    cnt.textContent = d.valor;

    bg.appendChild(fill);
    row.appendChild(lbl);
    row.appendChild(bg);
    row.appendChild(cnt);
    container.appendChild(row);
  });
}

function renderEstadisticas() {
  var tarjetas   = document.querySelectorAll('#tab-todas .tarjeta');
  var sesgosF    = {};
  var sesgosIA   = {};
  var fuentes    = {};
  var categorias = {};

  tarjetas.forEach(function(t) {
    var sF  = (t.dataset.sesgoFuente || 'desconocido').toLowerCase();
    var sIA = (t.dataset.sesgoIa    || 'desconocido').toLowerCase();
    sesgosF[sF]   = (sesgosF[sF]   || 0) + 1;
    sesgosIA[sIA] = (sesgosIA[sIA] || 0) + 1;
    var fn = t.querySelector('.fuente-nombre');
    if (fn) { var f = fn.textContent.trim(); fuentes[f] = (fuentes[f] || 0) + 1; }
  });

  document.querySelectorAll('#tab-todas .seccion').forEach(function(s) {
    var titulo = s.querySelector('.seccion-titulo');
    if (titulo) {
      categorias[titulo.textContent.trim()] = s.querySelectorAll('.tarjeta').length;
    }
  });

  var total         = tarjetas.length;
  var nFuentes      = Object.keys(fuentes).length;
  var SESGO_COLORES = window.DIGEST_CONFIG.sesgoColores;
  var sesgoOrden    = ['izquierda','centro-izquierda','centro','centro-derecha','derecha','desconocido'];

  var sesgosRef = ['izquierda','centro-izquierda','centro','centro-derecha','derecha'];
  var nDiv = sesgosRef.filter(function(s) {
    return (sesgosF[s] || 0) / Math.max(total, 1) >= 0.05;
  }).length;
  var divPct = sesgosRef.length ? Math.round((nDiv / sesgosRef.length) * 100) + '%' : '—';

  var sesgosActIA = Object.keys(sesgosIA).filter(function(s) {
    return s !== 'desconocido' && sesgosIA[s] > 0;
  }).length;

  document.getElementById('kpi-total').textContent      = total;
  document.getElementById('kpi-fuentes').textContent    = nFuentes;
  document.getElementById('kpi-diversidad').textContent = divPct;
  document.getElementById('kpi-sesgos').textContent     = sesgosActIA || '—';

  // Sesgo por fuente
  var maxSF  = Math.max.apply(null, sesgoOrden.map(function(s) { return sesgosF[s]||0; })) || 1;
  var datosSF = sesgoOrden.map(function(s) {
    return { label: s, pct: Math.round(((sesgosF[s]||0) / maxSF) * 100), valor: sesgosF[s]||0, color: SESGO_COLORES[s]||'#9ca3af' };
  });
  _crearBarChart(document.getElementById('stat-sesgo-chart'), datosSF);

  // Sesgo por IA
  var iaEl   = document.getElementById('stat-sesgo-ia-chart');
  if (iaEl) {
    if (sesgosActIA === 0) {
      while (iaEl.firstChild) iaEl.removeChild(iaEl.firstChild);
      var msg = document.createElement('span');
      msg.style.cssText = 'color:var(--txt-3);font-size:.78rem';
      msg.textContent   = 'Sin datos IA — ejecuta con ANTHROPIC_API_KEY para ver análisis';
      iaEl.appendChild(msg);
    } else {
      var maxSIA  = Math.max.apply(null, sesgoOrden.map(function(s) { return sesgosIA[s]||0; })) || 1;
      var datosIA = sesgoOrden.map(function(s) {
        return { label: s, pct: Math.round(((sesgosIA[s]||0) / maxSIA) * 100), valor: sesgosIA[s]||0, color: SESGO_COLORES[s]||'#9ca3af' };
      });
      _crearBarChart(iaEl, datosIA);
    }
  }

  // Top fuentes
  var topF   = Object.entries(fuentes).sort(function(a,b) { return b[1]-a[1]; }).slice(0,12);
  var maxF   = topF.length ? topF[0][1] : 1;
  var datosF = topF.map(function(p) {
    return { label: p[0], pct: Math.round((p[1]/maxF)*100), valor: p[1], color: 'var(--accent)' };
  });
  _crearBarChart(document.getElementById('stat-fuentes-chart'), datosF);

  // Por categoría
  var catEntries = Object.entries(categorias);
  var maxC       = Math.max.apply(null, catEntries.map(function(e) { return e[1]; })) || 1;
  var datosC     = catEntries.map(function(p) {
    return { label: p[0], pct: Math.round((p[1]/maxC)*100), valor: p[1], color: 'var(--accent-green)' };
  });
  _crearBarChart(document.getElementById('stat-cat-chart'), datosC);
}
