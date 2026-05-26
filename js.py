"""
js.py — JavaScript del digest de noticias.
Importado por renderer.py como constante _JS.

Único punto de interpolación: __SESGO_COLORES__ se reemplaza en render time
con el JSON de colores de sesgo generado desde config.py.
"""

_JS = """
var _tabActual    = 'destacadas';
var _filtroSesgo  = null;
var _statsReady   = false;
var _buscarTimer  = null;
var SESGO_COLORES = __SESGO_COLORES__;

/* ── Navegación por pestañas ─────────────────────────────────────────── */
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

  // La barra de búsqueda y el filtro solo tienen sentido fuera de Estadísticas
  var noSearch = name === 'estadisticas' || name === 'para-leer' || name === 'actualidad';
  var barra = document.querySelector('.search-bar');
  if (barra) barra.style.display = noSearch ? 'none' : 'flex';
  var sortBar = document.getElementById('sort-bar');
  var noSort = noSearch || name === 'sintesis' || name === 'asombro';
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

/* ── Búsqueda ────────────────────────────────────────────────────────── */
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
      // Usar el sesgo de la fuente (siempre disponible) para filtrar
      var sF = (t.dataset.sesgoFuente || '').toLowerCase();
      okF = (sF === _filtroSesgo);
    }
    var ok   = okQ && okF;
    t.hidden = !ok;
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

/* ── Filtro de sesgo (leyenda clicable) ──────────────────────────────── */
function filtrarPorSesgo(sesgo, el) {
  if (_filtroSesgo === sesgo) {
    limpiarFiltro();
    return;
  }
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

/* ── Estadísticas ────────────────────────────────────────────────────── */
function renderEstadisticas() {
  var tarjetas   = document.querySelectorAll('#tab-todas .tarjeta');
  var sesgosF    = {};  // por sesgo_fuente (siempre disponible)
  var sesgosIA   = {};  // por sesgo_ia (solo con análisis IA)
  var fuentes    = {};
  var categorias = {};

  tarjetas.forEach(function(t) {
    // Leer directamente de los data attributes — fiable independientemente del DOM
    var sF  = (t.dataset.sesgoFuente || 'desconocido').toLowerCase();
    var sIA = (t.dataset.sesgoIa    || 'desconocido').toLowerCase();
    sesgosF[sF]  = (sesgosF[sF]  || 0) + 1;
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

  var total    = tarjetas.length;
  var nFuentes = Object.keys(fuentes).length;

  // Diversidad: basada en sesgo_fuente (siempre tiene datos reales)
  var sesgosRef = ['izquierda','centro-izquierda','centro','centro-derecha','derecha'];
  var nDiv = sesgosRef.filter(function(s) {
    return (sesgosF[s] || 0) / Math.max(total, 1) >= 0.05;
  }).length;
  var divPct = sesgosRef.length ? Math.round((nDiv / sesgosRef.length) * 100) + '%' : '—';

  // Sesgos detectados por IA (excluye desconocido)
  var sesgosActIA = Object.keys(sesgosIA).filter(function(s) {
    return s !== 'desconocido' && sesgosIA[s] > 0;
  }).length;

  document.getElementById('kpi-total').textContent      = total;
  document.getElementById('kpi-fuentes').textContent    = nFuentes;
  document.getElementById('kpi-diversidad').textContent = divPct;
  document.getElementById('kpi-sesgos').textContent     = sesgosActIA || '—';

  var sesgoOrden = ['izquierda','centro-izquierda','centro','centro-derecha','derecha','desconocido'];

  // Gráfico: sesgo de la fuente (siempre disponible)
  var maxSF = Math.max.apply(null, sesgoOrden.map(function(s) { return sesgosF[s]||0; })) || 1;
  document.getElementById('stat-sesgo-chart').innerHTML = sesgoOrden.map(function(s) {
    var n   = sesgosF[s] || 0;
    var pct = Math.round((n / maxSF) * 100);
    var col = SESGO_COLORES[s] || '#9ca3af';
    return '<div class="stat-bar-row">' +
      '<span class="stat-bar-label">' + s + '</span>' +
      '<div class="stat-bar-bg"><div class="stat-bar-fill" style="width:' + pct + '%;background:' + col + '"></div></div>' +
      '<span class="stat-bar-count">' + n + '</span>' +
      '</div>';
  }).join('');

  // Gráfico: sesgo IA (puede estar todo en "desconocido" sin cuota)
  var maxSIA = Math.max.apply(null, sesgoOrden.map(function(s) { return sesgosIA[s]||0; })) || 1;
  var iaHtml = sesgoOrden.map(function(s) {
    var n   = sesgosIA[s] || 0;
    var pct = Math.round((n / maxSIA) * 100);
    var col = SESGO_COLORES[s] || '#9ca3af';
    return '<div class="stat-bar-row">' +
      '<span class="stat-bar-label">' + s + '</span>' +
      '<div class="stat-bar-bg"><div class="stat-bar-fill" style="width:' + pct + '%;background:' + col + '"></div></div>' +
      '<span class="stat-bar-count">' + n + '</span>' +
      '</div>';
  }).join('');
  var iaEl = document.getElementById('stat-sesgo-ia-chart');
  if (iaEl) iaEl.innerHTML = sesgosActIA === 0
    ? '<span style="color:var(--txt-3);font-size:.78rem">Sin datos IA — ejecuta con GEMINI_API_KEY para ver análisis</span>'
    : '<span style="color:var(--txt-3);font-size:.78rem">Sin datos IA — regenera con ANTHROPIC_API_KEY configurada</span>';

  // Top fuentes
  var topF = Object.entries(fuentes).sort(function(a,b){ return b[1]-a[1]; }).slice(0,12);
  var maxF = topF.length ? topF[0][1] : 1;
  document.getElementById('stat-fuentes-chart').innerHTML = topF.map(function(p) {
    var pct = Math.round((p[1]/maxF)*100);
    return '<div class="stat-bar-row">' +
      '<span class="stat-bar-label">' + p[0] + '</span>' +
      '<div class="stat-bar-bg"><div class="stat-bar-fill" style="width:' + pct + '%;background:var(--accent)"></div></div>' +
      '<span class="stat-bar-count">' + p[1] + '</span>' +
      '</div>';
  }).join('');

  // Categorías
  var catEntries = Object.entries(categorias);
  var maxC = Math.max.apply(null, catEntries.map(function(e){ return e[1]; })) || 1;
  document.getElementById('stat-cat-chart').innerHTML = catEntries.map(function(p) {
    var pct = Math.round((p[1]/maxC)*100);
    return '<div class="stat-bar-row">' +
      '<span class="stat-bar-label">' + p[0] + '</span>' +
      '<div class="stat-bar-bg"><div class="stat-bar-fill" style="width:' + pct + '%;background:var(--accent-green)"></div></div>' +
      '<span class="stat-bar-count">' + p[1] + '</span>' +
      '</div>';
  }).join('');
}

/* ── Lista de lectura ────────────────────────────────────────────────── */
var _BK_KEY = 'digestBookmarks';

function _cargarBookmarks() {
  try { return JSON.parse(localStorage.getItem(_BK_KEY) || '[]'); } catch(e) { return []; }
}
function _guardarBookmarks(lista) {
  try { localStorage.setItem(_BK_KEY, JSON.stringify(lista)); } catch(e) {}
}
function _actualizarContadorBK() {
  var n    = _cargarBookmarks().length;
  var cnt  = document.getElementById('bookmark-count');
  if (!cnt) return;
  if (n > 0) { cnt.textContent = n; cnt.style.display = ''; }
  else        cnt.style.display = 'none';
}

function toggleBookmark(ev, btn) {
  ev.stopPropagation();
  var d       = btn.dataset;
  var enlace  = d.enlace;
  var lista   = _cargarBookmarks();
  var idx     = lista.findIndex(function(x) { return x.enlace === enlace; });
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

function _esc(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function _safeUrl(u) { return /^https?:\/\//i.test(u) ? u : '#'; }

function _renderizarParaLeer() {
  var lista = _cargarBookmarks();
  var cont  = document.getElementById('para-leer-contenido');
  var desc  = document.getElementById('para-leer-desc');
  if (!cont) return;
  if (lista.length === 0) {
    cont.innerHTML = '<div class="para-leer-empty">Todavía no has guardado ningún artículo.<br>Haz clic en ★ en cualquier tarjeta para añadirlo aquí.</div>';
    if (desc) desc.textContent = 'Artículos guardados con ★ — se conservan entre sesiones';
    return;
  }
  if (desc) desc.textContent = lista.length + ' artículo(s) guardado(s)';
  cont.innerHTML = '<div class="grid">' + lista.map(function(item) {
    var tit = _esc(item.titulo || '');
    var src = _esc(item.fuente || '');
    var fch = _esc(item.fecha  || '');
    var url = _safeUrl(item.enlace || '');
    var urlEsc = _esc(url);
    return '<div class="tarjeta" style="cursor:default">' +
      '<div class="tarjeta-meta"><div class="fuente-bloque">' +
      '<span class="fuente-nombre">' + src + '</span>' +
      '<span class="fecha">' + fch + '</span>' +
      '</div>' +
      '<button class="bookmark-btn guardado" title="Quitar de la lista" data-enlace-rm="' + urlEsc + '" onclick="_eliminarBookmark(this.dataset.enlaceRm,this)">&#9733;</button>' +
      '</div>' +
      '<div class="titulo"><a href="' + urlEsc + '" target="_blank" rel="noopener noreferrer">' + tit + '</a></div>' +
      '</div>';
  }).join('') + '</div>';
}

function _eliminarBookmark(enlace, btn) {
  var lista = _cargarBookmarks().filter(function(x) { return x.enlace !== enlace; });
  _guardarBookmarks(lista);
  _actualizarContadorBK();
  _renderizarParaLeer();
  // Quitar clase guardado del botón correspondiente en otras pestañas
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

/* ── Resaltado de palabras clave ─────────────────────────────────────── */
var _kwActuales = [];

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

/* ── Vista inmersiva ─────────────────────────────────────────────────── */
function abrirArticulo(el) {
  var d         = el.dataset;
  var titulo    = d.titulo    || '';
  var fuente    = d.fuente    || '';
  var fecha     = d.fecha     || '';
  var enlace    = /^https?:\/\//i.test(d.enlace || '') ? d.enlace : '#';
  var resumen   = d.resumen   || '';
  var critica   = d.critica   || '';
  var sesgoF    = d.sesgoFuente || 'desconocido';
  var sesgoIA   = d.sesgoIa    || 'desconocido';

  // Categoría: leer del ancestro .seccion si existe
  var secEl = el.closest('.seccion');
  var cat   = secEl ? (secEl.querySelector('.seccion-titulo') || {}).textContent || '' : (d.categoria || '');

  // Tiempo de lectura estimado
  var palabras = (titulo + ' ' + resumen).split(/\\s+/).filter(Boolean).length;
  var minutos  = Math.max(1, Math.round(palabras / 200));

  document.getElementById('d-categoria').textContent = cat;
  document.getElementById('d-fuente').textContent    = fuente;
  document.getElementById('d-fecha').textContent     = fecha;
  document.getElementById('d-reading').textContent   = minutos + ' min lectura';
  document.getElementById('d-titulo').textContent    = titulo;
  document.getElementById('d-resumen').textContent   = resumen;

  var sfEl = document.getElementById('d-sesgo-f');
  sfEl.textContent = sesgoF.toUpperCase();
  sfEl.style.background = SESGO_COLORES[sesgoF] || '#9ca3af';

  var siaEl = document.getElementById('d-sesgo-ia');
  siaEl.textContent = sesgoIA.toUpperCase();
  siaEl.style.background = SESGO_COLORES[sesgoIA] || '#9ca3af';

  var sent     = (d.sentimiento || '').toLowerCase();
  var sentClss = {'alarmista':'badge-sent-alarmista','neutral':'badge-sent-neutral','optimista':'badge-sent-optimista'};
  var sentIcon = {'alarmista':'⚠','optimista':'✦'};
  var sentEl   = document.getElementById('d-sent');
  if (sentEl) {
    sentEl.innerHTML = (sent && sent !== 'neutral')
      ? '<span class="badge-sent ' + (sentClss[sent]||'') + '">' + (sentIcon[sent]||'') + ' ' + sent.toUpperCase() + '</span>'
      : '';
  }

  var criticaEl = document.getElementById('d-critica');
  if (critica) {
    criticaEl.textContent  = '\U0001F4A1 ' + critica;
    criticaEl.style.display = '';
  } else {
    criticaEl.style.display = 'none';
  }

  document.getElementById('d-btn-leer').href = enlace;
  document.getElementById('d-btn-traducir').href = 'https://translate.google.com/translate?sl=auto&tl=es&u=' + encodeURIComponent(enlace);

  document.getElementById('drawer-overlay').classList.add('open');
  document.getElementById('drawer').classList.add('open');
  document.body.style.overflow = 'hidden';
  document.body.classList.add('drawer-open');
}

function cerrarDrawer() {
  document.getElementById('drawer-overlay').classList.remove('open');
  document.getElementById('drawer').classList.remove('open');
  document.body.style.overflow = '';
  document.body.classList.remove('drawer-open');
}

function compartirArticulo() {
  var titulo  = document.getElementById('d-titulo').textContent;
  var enlace  = document.getElementById('d-btn-leer').href;
  var btn     = document.getElementById('d-btn-compartir');
  if (navigator.share) {
    navigator.share({ title: titulo, url: enlace }).catch(function() {});
  } else {
    navigator.clipboard.writeText(enlace).then(function() {
      btn.textContent = '✓ Copiado';
      setTimeout(function() { btn.textContent = 'Copiar enlace'; }, 2000);
    }).catch(function() {
      prompt('Copia este enlace:', enlace);
    });
  }
}

document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') cerrarDrawer();
});


/* ── Saludo según hora ───────────────────────────────────────────────── */
(function() {
  var h = new Date().getHours();
  var g = h < 6 ? 'Buenas noches' : h < 14 ? 'Buenos días' : h < 21 ? 'Buenas tardes' : 'Buenas noches';
  var el = document.getElementById('header-greeting');
  if (el) el.textContent = g;
})();

/* ── Modo oscuro ─────────────────────────────────────────────────────── */
function toggleDark() {
  var dark = document.body.classList.toggle('dark');
  try { localStorage.setItem('digestDark', dark ? '1' : '0'); } catch(e) {}
  var btn = document.getElementById('dark-toggle');
  if (btn) btn.innerHTML = dark ? '&#9728; Modo día' : '&#9790; Modo oscuro';
}

(function() {
  try {
    if (localStorage.getItem('digestDark') === '1') {
      document.body.classList.add('dark');
      var btn = document.getElementById('dark-toggle');
      if (btn) btn.innerHTML = '&#9728; Modo día';
    }
  } catch(e) {}
})();

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

/* ── Inicio ──────────────────────────────────────────────────────────── */
(function() {
  var last = 'destacadas';
  try {
    var saved = localStorage.getItem('digestTab') || 'destacadas';
    last = (saved === 'todas') ? 'destacadas' : saved;
  } catch(e) {}

  try {
    var kw = localStorage.getItem('digestKeywords');
    if (kw) {
      var kwInput = document.getElementById('kw-input');
      if (kwInput) { kwInput.value = kw; aplicarKeywords(kw); }
    }
  } catch(e) {}

  try { _actualizarContadorBK(); } catch(e) {}

  try {
    var sinIA = document.querySelectorAll('[data-sesgo-ia="desconocido"]').length;
    if (sinIA > 0) {
      var bannerCount = document.getElementById('ia-banner-count');
      var bannerEl    = document.getElementById('ia-banner');
      if (bannerCount) bannerCount.textContent = sinIA;
      if (bannerEl)    bannerEl.style.display = 'flex';
      if (window.location.protocol === 'file:') {
        var regenBtn = document.getElementById('ia-regen-btn');
        if (regenBtn) {
          regenBtn.textContent = 'Iniciar servidor Flask';
          regenBtn.onclick = function() {
            alert('Inicia el servidor Flask (app.py) o el .bat del escritorio para regenerar el análisis IA.');
          };
        }
      }
    }
  } catch(e) {}

  switchTab(last);
})();



// ── Ordenación de artículos ───────────────────────────────────────────────
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



/* ── Actualidad Absoluta ─────────────────────────────────────────────── */
var _historialDias = 10;
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
    _renderTrend(card);
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

function _renderSparkline(el) {
  if (!el) return;
  var card = el.closest('[data-historial]');
  if (!card) return;
  var estado = card.dataset.estado || 'estable';
  var color  = PROCESO_COLORES[estado] || '#2d5a2d';
  var historial;
  try { historial = JSON.parse(card.dataset.historial || '[]'); } catch(e) { historial = []; }
  var slice = historial.slice(-_historialDias);
  var max = 0;
  slice.forEach(function(d) { if ((d.cobertura||0) > max) max = d.cobertura||0; });
  if (max === 0) max = 1;
  el.innerHTML = slice.map(function(d) {
    var pct = d.cobertura > 0 ? Math.max(8, Math.round((d.cobertura / max) * 100)) : 4;
    var parts = (d.fecha || '').split('-');
    var label = parts.length === 3 ? parts[2] + '/' + parts[1] : d.fecha;
    var title = label + ': ' + (d.cobertura || 0) + ' art.';
    var opacity = d.cobertura > 0 ? '0.85' : '0.18';
    var bg = 'linear-gradient(to top,' + color + '55,' + color + ')';
    return '<div class="spark-bar" style="height:' + pct + '%;opacity:' + opacity + ';background:' + bg + '" title="' + title + '"></div>';
  }).join('');
}

function _renderTrend(card) {
  if (!card) return;
  var wrap = card.querySelector('.proceso-trend-wrap');
  if (!wrap) return;
  var estado = card.dataset.estado || 'estable';
  var color  = PROCESO_COLORES[estado] || '#6b7280';
  var historial;
  try { historial = JSON.parse(card.dataset.historial || '[]'); } catch(e) { historial = []; }
  var slice = historial.slice(-_historialDias);
  if (slice.length < 4) { wrap.innerHTML = ''; return; }
  var half   = Math.floor(slice.length / 2);
  var before = slice.slice(0, half).reduce(function(s,d){ return s+(d.cobertura||0); },0) / half;
  var after  = slice.slice(half).reduce(function(s,d){ return s+(d.cobertura||0); },0) / (slice.length-half);
  var pct = before > 0 ? Math.round(((after-before)/before)*100) : (after>0?100:0);
  if (Math.abs(pct) < 8) {
    wrap.innerHTML = '<span style="color:#9ca3af">&#8594; Cobertura estable</span>';
    return;
  }
  var arrow = pct > 0 ? '&#8593;' : '&#8595;';
  var sign  = pct > 0 ? '+' : '';
  wrap.innerHTML = '<span style="color:' + color + '">' + arrow + ' ' + sign + pct + '% cobertura esta semana</span>';
}

(function() {
  document.querySelectorAll('.proceso-card, .proceso-card-hero').forEach(function(card) {
    _renderSparkline(card.querySelector('.proceso-sparkline'));
    _renderTrend(card);
  });
})();

function generarBriefing() {
  var panel = document.getElementById('briefing-panel');
  var texto = document.getElementById('briefing-texto');
  panel.style.display = 'block';
  texto.innerHTML = '<span style="color:var(--txt-3);font-size:.85rem">Generando memo&#8230; puede tardar 15-20 s</span>';
  fetch('/briefing', {method:'POST'})
    .then(function(r) { return r.json(); })
    .then(function(d) {
      if (!d.ok) { texto.textContent = d.texto || 'Error'; return; }
      // Renderizar markdown mínimo de forma segura sin innerHTML con strings externos
      texto.textContent = '';
      d.texto.split('\\n').forEach(function(line) {
        var p = document.createElement('p');
        // Negrita **texto**
        var parts = line.split(/\*\*(.+?)\*\*/g);
        parts.forEach(function(part, i) {
          if (i % 2 === 1) {
            var b = document.createElement('strong');
            b.textContent = part;
            p.appendChild(b);
          } else if (part) {
            p.appendChild(document.createTextNode(part));
          }
        });
        texto.appendChild(p);
      });
    })
    .catch(function() {
      texto.textContent = 'Error al conectar con el servidor.';
    });
}



if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');
}
"""
