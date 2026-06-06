/* ── Búsqueda y filtros reactivos unificados (search.js) ── */
var _filtroSesgo = null;
var _kwActuales  = [];
var _frenteAFrente = false;
var _enfoqueSemantico = 1; // 0 = Objetivo (Zen), 1 = Normal, 2 = Alerta

function _obtenerDiferenciaDias(fechaArticuloStr) {
  var msecArt = _parseFecha(fechaArticuloStr);
  if (!msecArt) return 999;
  
  var artDate = new Date(msecArt);
  artDate.setHours(0, 0, 0, 0);
  
  var hoyDate = new Date();
  hoyDate.setHours(0, 0, 0, 0);
  
  var diffTime = hoyDate.getTime() - artDate.getTime();
  var diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
  return diffDays;
}

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
    
    // 1. Filtro de búsqueda textual
    var okQ   = !q || texto.includes(q) || ds.includes(q);
    
    // 2. Filtro de sesgo (Espectrómetro)
    var okF   = true;
    if (_filtroSesgo && _tabActual === 'todas') {
      var sF = (t.dataset.sesgoFuente || '').toLowerCase();
      okF = (sF === _filtroSesgo);
    }
    
    // 3. Filtro de contraste extremo (Frente a Frente)
    var okFF = true;
    if (_frenteAFrente && _tabActual === 'todas') {
      var sF = (t.dataset.sesgoFuente || '').toLowerCase();
      okFF = (sF === 'izquierda' || sF === 'derecha');
    }
    
    // 4. Filtro por antigüedad (Timeline Histogram)
    var okD = true;
    if (_diasFiltroActivo !== null && (t.classList.contains('tarjeta') || t.classList.contains('tarjeta-destacada'))) {
      var diff = _obtenerDiferenciaDias(t.dataset.fecha);
      okD = (diff <= _diasFiltroActivo);
    }
    
    // 5. Filtro de Enfoque Semántico (Modo Zen / Alerta)
    var okE = true;
    if (t.classList.contains('tarjeta') || t.classList.contains('tarjeta-destacada')) {
      var sent = (t.dataset.sentimiento || '').toLowerCase();
      var nov = parseInt(t.dataset.novedad || 2);
      
      if (_enfoqueSemantico === 0) { // Enfoque Objetivo / Zen
        okE = (sent !== 'alarmista' && nov > 1);
      } else if (_enfoqueSemantico === 2) { // Enfoque Crítico / Alerta
        okE = (sent === 'alarmista');
      }
    }
    
    // Filtro duro (oculta tarjetas de forma total)
    var okDuro = okQ && okD;
    
    // Filtro blando (atenúa tarjetas de forma no destructiva)
    var okBlando = okF && okFF && okE;
    
    if (!okDuro) {
      t.hidden = true;
      t.classList.remove('filtrado-atenuado');
    } else {
      t.hidden = false;
      if (!okBlando) {
        t.classList.add('filtrado-atenuado');
      } else {
        t.classList.remove('filtrado-atenuado');
      }
      
      // Aplicar animación CSS si pasa a ser visible y no atenuada
      if (okBlando && !t.classList.contains('card-animate')) {
        t.classList.add('card-animate');
      }
    }
    
    var okTotal = okDuro && okBlando;
    if (okTotal) visibles++;
  });
  
  var total = tarjetas.length;
  var cnt   = document.getElementById('search-count');
  if (cnt) {
    var filtradoActivo = q || _filtroSesgo || _frenteAFrente || _diasFiltroActivo !== null || _enfoqueSemantico !== 1;
    cnt.textContent = filtradoActivo ? visibles + ' de ' + total + ' resultado(s)' : '';
  }
}

function _limpiarContador() {
  var cnt = document.getElementById('search-count');
  if (cnt) cnt.textContent = '';
}

/* ── Filtro de sesgo desde dropdown ── */
function filtrarSesgoSelect(val) {
  _filtroSesgo = val || null;
  buscar(document.getElementById('buscador') ? document.getElementById('buscador').value : '');
}

/* ── Espectrómetro Editorial (Lógica) ── */
var SESGO_VALORES_NOMBRES = {
  '-1': 'Todos los medios',
  '0': 'Izquierda',
  '1': 'Centro-Izquierda',
  '2': 'Centro',
  '3': 'Centro-Derecha',
  '4': 'Derecha'
};
var SESGO_MAPPING_SLIDER = {
  '-1': null,
  '0': 'izquierda',
  '1': 'centro-izquierda',
  '2': 'centro',
  '3': 'centro-derecha',
  '4': 'derecha'
};

function filtrarPorEspectro(val) {
  var sliderVal = parseInt(val);
  
  // Sincronizar slider en el DOM
  var slider = document.getElementById('espectro-slider');
  if (slider) slider.value = sliderVal;
  
  // Apagar modo Frente a Frente
  _frenteAFrente = false;
  var btnFF = document.getElementById('btn-contraste');
  if (btnFF) btnFF.classList.remove('active');
  
  // Obtener sesgo correspondiente
  _filtroSesgo = SESGO_MAPPING_SLIDER[sliderVal];
  
  // Actualizar textos
  var valLbl = document.getElementById('espectro-valor');
  if (valLbl) {
    valLbl.textContent = SESGO_VALORES_NOMBRES[sliderVal];
    var col = window.DIGEST_CONFIG.sesgoColores[_filtroSesgo] || 'var(--txt-1)';
    valLbl.style.color = col;
  }
  
  // Sincronizar botones de la botonera
  document.querySelectorAll('.espectro-btn').forEach(function(btn) {
    var bS = btn.getAttribute('data-sesgo');
    if (bS === (_filtroSesgo || 'todos')) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });
  
  if (_tabActual !== 'todas') switchTab('todas');
  else buscar(document.getElementById('buscador').value);
}

function filtrarSesgoBoton(sesgo, btn) {
  // Encontrar el índice del slider correspondiente
  var sliderVal = -1;
  for (var key in SESGO_MAPPING_SLIDER) {
    if (SESGO_MAPPING_SLIDER[key] === (sesgo === 'todos' ? null : sesgo)) {
      sliderVal = parseInt(key);
      break;
    }
  }
  
  filtrarPorEspectro(sliderVal);
}

function toggleFrenteAFrente() {
  _frenteAFrente = !_frenteAFrente;
  var btn = document.getElementById('btn-contraste');
  if (btn) {
    if (_frenteAFrente) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  }
  
  if (_frenteAFrente) {
    // Desactivar filtros simples
    _filtroSesgo = null;
    var slider = document.getElementById('espectro-slider');
    if (slider) slider.value = -1;
    var valLbl = document.getElementById('espectro-valor');
    if (valLbl) {
      valLbl.textContent = "Contraste Extremos";
      valLbl.style.color = "var(--accent)";
    }
    document.querySelectorAll('.espectro-btn').forEach(function(b) {
      b.classList.remove('active');
    });
  } else {
    var valLbl = document.getElementById('espectro-valor');
    if (valLbl) {
      valLbl.textContent = "Todos los medios";
      valLbl.style.color = "var(--txt-1)";
    }
  }
  
  if (_tabActual !== 'todas') switchTab('todas');
  else buscar(document.getElementById('buscador').value);
}

/* ── Filtro de Enfoque Semántico ── */
function cambiarEnfoqueSemantico(val) {
  _enfoqueSemantico = parseInt(val);
  var slider = document.getElementById('enfoque-slider');
  if (slider) slider.value = _enfoqueSemantico;
  
  var buscador = document.getElementById('buscador');
  buscar(buscador ? buscador.value : '');
}

function ajustarEnfoqueIndex(val) {
  cambiarEnfoqueSemantico(val);
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
