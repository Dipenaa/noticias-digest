/* ── Búsqueda y filtros ───────────────────────────────────────────────── */
var _filtroSesgo = null;
var _kwActuales  = [];

function buscar(q) {
  q = q.trim().toLowerCase();
  var tarjetas = document.querySelectorAll(
    '#tab-' + _tabActual + ' .tarjeta, ' +
    '#tab-' + _tabActual + ' .tarjeta-destacada, ' +
    '#tab-' + _tabActual + ' .sintesis-card'
  );
  var visibles = 0;
  tarjetas.forEach(function(t) {
    var texto = (t.textContent || t.innerText).toLowerCase();
    var ds    = (t.dataset.search || '').toLowerCase();
    var okQ   = !q || texto.includes(q) || ds.includes(q);
    var okF   = true;
    if (_filtroSesgo && _tabActual === 'todas') {
      var sF = (t.dataset.sesgoFuente || '').toLowerCase();
      okF = (sF === _filtroSesgo);
    }
    var ok    = okQ && okF;
    t.hidden  = !ok;
    if (ok) visibles++;
  });
  var total = tarjetas.length;
  var cnt   = document.getElementById('search-count');
  if (cnt) cnt.textContent = (q || _filtroSesgo) ? visibles + ' de ' + total + ' resultado(s)' : '';
}

function _limpiarContador() {
  var cnt = document.getElementById('search-count');
  if (cnt) cnt.textContent = '';
}

function filtrarPorSesgo(sesgo, el) {
  if (_filtroSesgo === sesgo) { limpiarFiltro(); return; }
  _filtroSesgo = sesgo;
  document.querySelectorAll('.leyenda-items .badge').forEach(function(b) {
    b.classList.remove('filtro-activo');
  });
  el.classList.add('filtro-activo');
  var aviso = document.getElementById('filtro-aviso');
  var btn   = document.getElementById('filtro-clear');
  if (aviso) { aviso.textContent = 'Filtrando: ' + sesgo; aviso.style.display = ''; }
  if (btn)   btn.style.display = '';
  if (_tabActual !== 'todas') switchTab('todas');
  else buscar(document.getElementById('buscador').value);
}

function limpiarFiltro() {
  _filtroSesgo = null;
  document.querySelectorAll('.leyenda-items .badge').forEach(function(b) {
    b.classList.remove('filtro-activo');
  });
  var aviso = document.getElementById('filtro-aviso');
  var btn   = document.getElementById('filtro-clear');
  if (aviso) aviso.style.display = 'none';
  if (btn)   btn.style.display   = 'none';
  buscar(document.getElementById('buscador').value);
}

function aplicarKeywords(raw) {
  _kwActuales = raw.split(',').map(function(s) { return s.trim().toLowerCase(); }).filter(Boolean);
  try { localStorage.setItem('digestKeywords', raw); } catch(e) {}
  document.querySelectorAll('.tarjeta, .tarjeta-destacada').forEach(function(t) {
    if (_kwActuales.length === 0) {
      t.classList.remove('kw-match');
    } else {
      var texto = (t.dataset.search || '').toLowerCase();
      var match = _kwActuales.some(function(kw) { return texto.includes(kw); });
      t.classList.toggle('kw-match', match);
    }
  });
}
