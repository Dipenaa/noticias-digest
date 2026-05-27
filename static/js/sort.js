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

    cards.sort(function(a, b) {
      switch (criterio) {
        case 'fecha-desc':
          return _parseFecha(b.dataset.fecha) - _parseFecha(a.dataset.fecha);
        case 'fecha-asc':
          return _parseFecha(a.dataset.fecha) - _parseFecha(b.dataset.fecha);
        case 'importante':
          return (b.dataset.importante === 'true' ? 1 : 0) - (a.dataset.importante === 'true' ? 1 : 0);
        case 'sesgo-izq':
          return (_SESGO_ORD[a.dataset.sesgoIa] !== undefined ? _SESGO_ORD[a.dataset.sesgoIa] : 5)
               - (_SESGO_ORD[b.dataset.sesgoIa] !== undefined ? _SESGO_ORD[b.dataset.sesgoIa] : 5);
        case 'sesgo-der':
          return (_SESGO_ORD[b.dataset.sesgoIa] !== undefined ? _SESGO_ORD[b.dataset.sesgoIa] : 5)
               - (_SESGO_ORD[a.dataset.sesgoIa] !== undefined ? _SESGO_ORD[a.dataset.sesgoIa] : 5);
        case 'alarmista':
          return (_SENT_ORD[a.dataset.sentimiento] !== undefined ? _SENT_ORD[a.dataset.sentimiento] : 1)
               - (_SENT_ORD[b.dataset.sentimiento] !== undefined ? _SENT_ORD[b.dataset.sentimiento] : 1);
        default:
          return parseInt(a.dataset.order || 0) - parseInt(b.dataset.order || 0);
      }
    });

    cards.forEach(function(c) { grid.appendChild(c); });
  });
}
