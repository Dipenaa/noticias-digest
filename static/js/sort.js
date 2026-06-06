/* ── Ordenación de artículos ─────────────────────────────────────────── */
var _SESGO_IZQ_ORD = {
  'izquierda': 0, 'centro-izquierda': 1, 'centro': 2,
  'centro-derecha': 3, 'derecha': 4, 'desconocido': 5
};
var _SESGO_DER_ORD = {
  'derecha': 0, 'centro-derecha': 1, 'centro': 2,
  'centro-izquierda': 3, 'izquierda': 4, 'desconocido': 5
};

function _parseFecha(s) {
  if (!s || s === 'Fecha desconocida') return 0;
  var p = s.split(' '), f = (p[0]||'').split('/'), h = (p[1]||'00:00').split(':');
  return new Date(f[2], f[1]-1, f[0], h[0], h[1]).getTime();
}

function sortCards(criterio, btn) {
  document.querySelectorAll('.sort-btn').forEach(function(b) { b.classList.remove('active'); });
  if (btn) btn.classList.add('active');

  var tab = document.querySelector('.tab-content[style*="block"]');
  if (!tab) return;

  tab.querySelectorAll('.grid, .grid-destacadas').forEach(function(grid) {
    var cards = Array.from(grid.querySelectorAll(':scope > .tarjeta, :scope > .tarjeta-destacada, :scope > .asombro-card'));
    if (cards.length < 2) return;

    // Schwartzian transform: pre-calcular valores para optimizar y asegurar rapidez
    var mapped = cards.map(function(c) {
      var ds = c.dataset || {};
      
      // Fecha
      var fechaVal = _parseFecha(ds.fecha);
      
      // Relevancia
      var importanteVal = ds.importante === 'true' ? 10 : 0;
      var asombroVal = parseInt(ds.asombro || 0);
      var novedadVal = parseInt(ds.novedad || 2);
      var relevanciaVal = importanteVal + (asombroVal * 3) + (novedadVal === 3 ? 2 : 0);
      
      // Sesgo Izquierda
      var sIA = (ds.sesgoIa || 'desconocido').toLowerCase();
      var sesgoIzqVal = _SESGO_IZQ_ORD[sIA] !== undefined ? _SESGO_IZQ_ORD[sIA] : 5;
      
      // Sesgo Derecha
      var sesgoDerVal = _SESGO_DER_ORD[sIA] !== undefined ? _SESGO_DER_ORD[sIA] : 5;

      return {
        el: c,
        fecha: fechaVal,
        relevancia: relevanciaVal,
        novedad: novedadVal,
        sesgoIzq: sesgoIzqVal,
        sesgoDer: sesgoDerVal,
        order: parseInt(ds.order || 0)
      };
    });

    mapped.sort(function(a, b) {
      switch (criterio) {
        case 'fecha-desc':
          return b.fecha - a.fecha;
        case 'fecha-asc':
          return a.fecha - b.fecha;
        case 'novedad':
          if (b.novedad !== a.novedad) {
            return b.novedad - a.novedad;
          }
          return b.fecha - a.fecha;
        case 'sesgo-izq':
          if (a.sesgoIzq !== b.sesgoIzq) {
            return a.sesgoIzq - b.sesgoIzq;
          }
          return b.fecha - a.fecha;
        case 'sesgo-der':
          if (a.sesgoDer !== b.sesgoDer) {
            return a.sesgoDer - b.sesgoDer;
          }
          return b.fecha - a.fecha;
        default:
          return a.order - b.order;
      }
    });

    mapped.forEach(function(item) { grid.appendChild(item.el); });
  });
}
