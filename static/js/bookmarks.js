/* ── Lista de lectura (bookmarks) ────────────────────────────────────── */
var _BK_KEY = 'digestBookmarks';

function _cargarBookmarks() {
  try { return JSON.parse(localStorage.getItem(_BK_KEY) || '[]'); } catch(e) { return []; }
}
function _guardarBookmarks(lista) {
  try { localStorage.setItem(_BK_KEY, JSON.stringify(lista)); } catch(e) {}
}
function _actualizarContadorBK() {
  var n   = _cargarBookmarks().length;
  var cnt = document.getElementById('bookmark-count');
  if (!cnt) return;
  if (n > 0) { cnt.textContent = n; cnt.style.display = ''; }
  else        cnt.style.display = 'none';
}

function toggleBookmark(ev, btn) {
  ev.stopPropagation();
  var d      = btn.dataset;
  var enlace = d.enlace;
  var lista  = _cargarBookmarks();
  var idx    = lista.findIndex(function(x) { return x.enlace === enlace; });
  if (idx >= 0) {
    lista.splice(idx, 1);
    btn.classList.remove('guardado');
    btn.title = 'Guardar para leer';
  } else {
    lista.push({ enlace: enlace, titulo: d.titulo, fuente: d.fuente, fecha: d.fecha });
    btn.classList.add('guardado');
    btn.title = 'Quitar de la lista';
  }
  _guardarBookmarks(lista);
  _actualizarContadorBK();
  if (_tabActual === 'para-leer') _renderizarParaLeer();
}

function _crearTarjetaGuardada(item) {
  var card = document.createElement('div');
  card.className = 'tarjeta';
  card.style.cursor = 'default';

  var meta = document.createElement('div');
  meta.className = 'tarjeta-meta';

  var fuente = document.createElement('div');
  fuente.className = 'fuente-bloque';

  var fuenteNombre = document.createElement('span');
  fuenteNombre.className = 'fuente-nombre';
  fuenteNombre.textContent = item.fuente || '';

  var fecha = document.createElement('span');
  fecha.className = 'fecha';
  fecha.textContent = item.fecha || '';

  fuente.appendChild(fuenteNombre);
  fuente.appendChild(fecha);

  var btn = document.createElement('button');
  btn.className = 'bookmark-btn guardado';
  btn.title = 'Quitar de la lista';
  btn.textContent = '★';
  btn.addEventListener('click', function() {
    _eliminarBookmark(item.enlace, btn);
  });

  meta.appendChild(fuente);
  meta.appendChild(btn);

  var titulo = document.createElement('div');
  titulo.className = 'titulo';

  var enlaceEl = document.createElement('a');
  enlaceEl.href = item.enlace || '#';
  enlaceEl.target = '_blank';
  enlaceEl.rel = 'noopener noreferrer';
  enlaceEl.textContent = item.titulo || '';

  titulo.appendChild(enlaceEl);
  card.appendChild(meta);
  card.appendChild(titulo);
  return card;
}

function _renderizarParaLeer() {
  var lista = _cargarBookmarks();
  var cont  = document.getElementById('para-leer-contenido');
  var desc  = document.getElementById('para-leer-desc');
  if (!cont) return;

  while (cont.firstChild) cont.removeChild(cont.firstChild);

  if (lista.length === 0) {
    var empty = document.createElement('div');
    empty.className = 'para-leer-empty';
    empty.textContent = 'Todavía no has guardado ningún artículo. Haz clic en ★ en cualquier tarjeta para añadirlo aquí.';
    cont.appendChild(empty);
    if (desc) desc.textContent = 'Artículos guardados con ★ — se conservan entre sesiones';
    return;
  }

  if (desc) desc.textContent = lista.length + ' artículo(s) guardado(s)';
  var grid = document.createElement('div');
  grid.className = 'grid';
  lista.forEach(function(item) { grid.appendChild(_crearTarjetaGuardada(item)); });
  cont.appendChild(grid);
}

function _eliminarBookmark(enlace, btn) {
  var lista = _cargarBookmarks().filter(function(x) { return x.enlace !== enlace; });
  _guardarBookmarks(lista);
  _actualizarContadorBK();
  _renderizarParaLeer();
  document.querySelectorAll('.bookmark-btn[data-enlace="' + enlace + '"]').forEach(function(b) {
    b.classList.remove('guardado');
    b.title = 'Guardar para leer';
  });
}

function _sincronizarBotonesBK() {
  var guardados = new Set(_cargarBookmarks().map(function(x) { return x.enlace; }));
  document.querySelectorAll('.bookmark-btn').forEach(function(btn) {
    if (guardados.has(btn.dataset.enlace)) {
      btn.classList.add('guardado');
      btn.title = 'Quitar de la lista';
    } else {
      btn.classList.remove('guardado');
      btn.title = 'Guardar para leer';
    }
  });
}
