/* ── Ordenación de artículos ─────────────────────────────────────────── */
var _SESGO_ORD = {
  'izquierda': 0, 'centro-izquierda': 1, 'centro': 2,
  'centro-derecha': 3, 'derecha': 4, 'desconocido': 5
};
var _SENT_ORD = {'alarmista': 0, 'neutral': 1, 'optimista': 2};

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
    var cards = Array.from(grid.querySelectorAll(':scope > .tarjeta, :scope > .tarjeta-destacada'));
    if (cards.length < 2) return;

    // Schwartzian transform: pre-calcular valores para optimizar la ordenación
    var mapped = cards.map(function(c) {
      var ds = c.dataset || {};
      var fechaVal = 0;
      if (criterio === 'fecha-desc' || criterio === 'fecha-asc') {
        fechaVal = _parseFecha(ds.fecha);
      }
      
      var importanteVal = 0;
      if (criterio === 'importante') {
        importanteVal = ds.importante === 'true' ? 1 : 0;
      }
      
      var sesgoVal = 5;
      if (criterio === 'sesgo-izq' || criterio === 'sesgo-der') {
        var sIA = ds.sesgoIa;
        sesgoVal = _SESGO_ORD[sIA] !== undefined ? _SESGO_ORD[sIA] : 5;
      }
      
      var sentimientoVal = 1;
      if (criterio === 'alarmista') {
        var sent = ds.sentimiento;
        sentimientoVal = _SENT_ORD[sent] !== undefined ? _SENT_ORD[sent] : 1;
      }
      
      var orderVal = 0;
      if (criterio === 'defecto') {
        orderVal = parseInt(ds.order || 0);
      }

      return {
        el: c,
        fecha: fechaVal,
        importante: importanteVal,
        sesgo: sesgoVal,
        sentimiento: sentimientoVal,
        order: orderVal
      };
    });

    mapped.sort(function(a, b) {
      switch (criterio) {
        case 'fecha-desc':
          return b.fecha - a.fecha;
        case 'fecha-asc':
          return a.fecha - b.fecha;
        case 'importante':
          return b.importante - a.importante;
        case 'sesgo-izq':
          return a.sesgo - b.sesgo;
        case 'sesgo-der':
          return b.sesgo - a.sesgo;
        case 'alarmista':
          return a.sentimiento - b.sentimiento;
        default:
          return a.order - b.order;
      }
    });

    mapped.forEach(function(item) { grid.appendChild(item.el); });
  });
}
