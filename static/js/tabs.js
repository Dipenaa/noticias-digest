/* ── Navegación por pestañas ──────────────────────────────────────────── */
var _tabActual   = 'destacadas';
var _statsReady  = false;
var _buscarTimer = null;

function switchTab(name) {
  _tabActual = name;
  document.querySelectorAll('.tab-content').forEach(function(el) {
    el.style.display = 'none';
  });
  document.querySelectorAll('.tab-btn').forEach(function(el) {
    el.classList.remove('active');
  });
  var tabEl = document.getElementById('tab-' + name);
  if (tabEl) {
    tabEl.style.display = 'block';
    tabEl.classList.remove('tab-anim');
    void tabEl.offsetWidth;
    tabEl.classList.add('tab-anim');
    setTimeout(function() { _animarTarjetas(tabEl); }, 30);
  }
  var btnEl = document.querySelector('[data-tab="' + name + '"]');
  if (btnEl) btnEl.classList.add('active');

  var nav = document.getElementById('cat-nav');
  if (nav) nav.style.display = name === 'todas' ? 'flex' : 'none';

  var noSearch = name === 'estadisticas' || name === 'para-leer' || name === 'actualidad';
  var barra    = document.querySelector('.search-bar');
  if (barra) barra.style.display = noSearch ? 'none' : 'flex';
  var sortBar  = document.getElementById('sort-bar');
  var noSort   = noSearch || name === 'sintesis' || name === 'asombro';
  if (sortBar) sortBar.style.display = noSort ? 'none' : 'flex';

  try {
    if (name === 'estadisticas') {
      if (!_statsReady) { renderEstadisticas(); _statsReady = true; }
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

/* ── Staggered animation al cambiar pestaña ──────────────────────────── */
function _animarTarjetas(tabEl) {
  if (!tabEl) return;
  var cards = tabEl.querySelectorAll(
    '.tarjeta, .tarjeta-destacada, .sintesis-card, .asombro-card, .proceso-card, .proceso-card-hero'
  );
  cards.forEach(function(c, i) {
    c.classList.remove('card-animate');
    c.style.setProperty('--card-delay', Math.min(i * 42, 600) + 'ms');
    void c.offsetWidth;
    c.classList.add('card-animate');
  });
}
