/* ── Navegación por pestañas ──────────────────────────────────────────── */
var _tabActual   = 'destacadas';
var _statsReady  = false;
var _buscarTimer = null;

function switchTab(name) {
  _tabActual = name;
  window.scrollTo({ top: 0, behavior: 'instant' });
  document.querySelectorAll('.tab-content').forEach(function(el) {
    el.style.display = 'none';
  });
  document.querySelectorAll('.tab-btn').forEach(function(el) {
    el.classList.remove('active');
  });
  var tabEl = document.getElementById('tab-' + name);
  if (tabEl) {
    tabEl.style.display = 'block';
  }
  var btnEl = document.querySelector('[data-tab="' + name + '"]');
  if (btnEl) btnEl.classList.add('active');

  var nav = document.getElementById('cat-nav');
  if (nav) nav.style.display = name === 'todas' ? 'flex' : 'none';

  var noSearch = name === 'estadisticas' || name === 'para-leer' || name === 'actualidad';
  var barra    = document.querySelector('.search-bar');
  if (barra) barra.style.display = noSearch ? 'none' : 'flex';
  var filterBar = document.getElementById('filter-bar');
  var noFilter  = noSearch || name === 'sintesis' || name === 'asombro';
  if (filterBar) filterBar.style.display = noFilter ? 'none' : 'flex';

  if (name === 'actualidad') {
    // Re-render canvas sparklines at correct size now that the tab is visible
    setTimeout(function() {
      document.querySelectorAll('.proceso-sparkline').forEach(function(c) {
        if (typeof _renderSparkline === 'function') _renderSparkline(c);
      });
    }, 0);
  }

  if (name === 'asombro') {
    setTimeout(function() {
      if (typeof inicializarAsombro === 'function') inicializarAsombro();
    }, 0);
  }

  try {
    if (name === 'estadisticas') {
      if (!_statsReady) { renderEstadisticas(); _statsReady = true; }
      if (typeof renderizarCartografia2D === 'function') renderizarCartografia2D();
      if (typeof inicializarCalibrador === 'function') inicializarCalibrador();
    } else if (name === 'para-leer') {
      _renderizarParaLeer();
    } else {
      var q = document.getElementById('buscador');
      if (q && q.value) buscar(q.value); else _limpiarContador();
      _sincronizarBotonesBK();
      if (_kwActuales && _kwActuales.length) {
        var kwIn = document.getElementById('kw-input');
        if (kwIn) aplicarKeywords(kwIn.value);
      }
    }
  } catch(e) {}
  try { localStorage.setItem('digestTab', name); } catch(e) {}
}

