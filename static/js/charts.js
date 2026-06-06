/* ── Visualización de Datos e Indicadores SVG (charts.js) ── */

// Lista de términos que activan la detección de alarmismo
var TERMINOS_ALARMISTAS = [
  'crisis', 'colapso', 'tensión', 'caos', 'guerra', 'amenaza', 'peligro', 'desastre', 
  'alarma', 'pánico', 'caída', 'desplome', 'conflicto', 'escalada', 'ruptura', 
  'catástrofe', 'alerta', 'urgente', 'choque', 'recorte', 'tensión', 'impacto'
];

document.addEventListener('DOMContentLoaded', function() {
  // Inicialización de componentes gráficos
  setTimeout(function() {
    inicializarBarometroTension();
    inicializarTimelineHistogram();
    // La Cartografía se renderiza bajo demanda al cargar estadísticas
  }, 100);
});

/* ── 1. Barómetro de Tensión Semántica ── */
function inicializarBarometroTension() {
  var wrap = document.getElementById('tension-wrap');
  var aguja = document.getElementById('barometro-aguja');
  var valLbl = document.getElementById('barometro-val-lbl');
  
  if (!wrap || !aguja) return;
  
  var pct = parseInt(wrap.getAttribute('data-pct-tension') || 0);
  var txt = wrap.getAttribute('data-txt-tension') || 'Normal';
  var color = wrap.getAttribute('data-color-tension') || 'var(--txt-3)';
  
  // Rotar aguja de -75 a +75 grados según el porcentaje
  var angle = -75 + (pct * 1.5);
  aguja.style.transform = "rotate(" + angle + "deg)";
  aguja.style.transformOrigin = "50px 45px";
  aguja.style.transition = "transform 1.2s cubic-bezier(0.2, 0.9, 0.3, 1)";
  
  // Colorear el pivote del barómetro
  var cir = aguja.nextElementSibling;
  if (cir) cir.setAttribute('fill', color);
  
  // Rellenar modal con datos
  var modalPct = document.getElementById('barometro-modal-pct');
  var modalStatus = document.getElementById('barometro-modal-status');
  if (modalPct) modalPct.textContent = pct + "%";
  if (modalStatus) {
    modalStatus.textContent = txt.toUpperCase();
    modalStatus.style.color = color;
  }
  
  // Analizar palabras alarmistas del DOM
  contarPalabrasAlarmistas();
}

function contarPalabrasAlarmistas() {
  var conteos = {};
  TERMINOS_ALARMISTAS.forEach(function(w) { conteos[w] = 0; });
  
  var tarjetas = document.querySelectorAll('.tarjeta, .tarjeta-destacada');
  tarjetas.forEach(function(t) {
    var txt = (t.dataset.search || "").toLowerCase();
    TERMINOS_ALARMISTAS.forEach(function(w) {
      // Búsqueda simple de subcadena
      var idx = txt.indexOf(w);
      while (idx !== -1) {
        conteos[w]++;
        idx = txt.indexOf(w, idx + 1);
      }
    });
  });
  
  // Ordenar vocabulario por frecuencia
  var vocabList = Object.entries(conteos)
    .filter(function(x) { return x[1] > 0; })
    .sort(function(a, b) { return b[1] - a[1]; })
    .slice(0, 10); // Top 10 palabras
    
  var listEl = document.getElementById('barometro-vocab-list');
  if (!listEl) return;
  
  if (vocabList.length === 0) {
    listEl.innerHTML = '<span style="color:var(--txt-3);font-size:.78rem">No se detectó lenguaje de alta tensión semántica hoy.</span>';
    return;
  }
  
  var maxVal = vocabList[0][1];
  listEl.innerHTML = vocabList.map(function(item) {
    var word = item[0];
    var count = item[1];
    var pct = Math.round((count / maxVal) * 100);
    return '<div class="vocab-row">' +
      '<span class="vocab-word">' + word + '</span>' +
      '<div class="vocab-bar-bg"><div class="vocab-bar-fill" style="width:' + pct + '%;background:var(--accent-warm)"></div></div>' +
      '<span class="vocab-count">' + count + '</span>' +
      '</div>';
  }).join('');
}

function abrirBarometroModal(ev) {
  if (ev) ev.stopPropagation();
  var modal = document.getElementById('barometro-modal');
  if (modal) {
    modal.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
}

function cerrarBarometroModal() {
  var modal = document.getElementById('barometro-modal');
  if (modal) {
    modal.classList.remove('open');
    document.body.style.overflow = '';
  }
}


/* ── 2. Timeline Histogram (Filtro por Antigüedad) ── */
var _diasFiltroActivo = null;

function inicializarTimelineHistogram() {
  var histContainer = document.getElementById('timeline-histogram');
  var ticksContainer = document.getElementById('timeline-ticks');
  if (!histContainer) return;
  
  var tarjetas = document.querySelectorAll('#tab-todas .tarjeta');
  var conteos = {};
  
  // Agrupar por diferencia de días respecto a hoy
  tarjetas.forEach(function(t) {
    var diff = _obtenerDiferenciaDias(t.dataset.fecha);
    if (diff !== 999) {
      conteos[diff] = (conteos[diff] || 0) + 1;
    }
  });
  
  var diasLabels = {
    0: 'Hoy',
    1: 'Ayer',
    2: 'Hace 3d',
    3: 'Hace 4d',
    4: 'Hace 5d',
    5: 'Hace 6d',
    6: 'Hace 7d',
    7: 'Hace 8d',
    8: 'Hace 9d',
    9: 'Hace 10d'
  };
  
  // Encontrar el volumen máximo para escalar las barras
  var maxVol = 0;
  for (var d = 0; d <= 9; d++) {
    var vol = conteos[d] || 0;
    if (vol > maxVol) maxVol = vol;
  }
  if (maxVol === 0) maxVol = 1;
  
  // Dibujar barras del histograma
  var barsHtml = "";
  var ticksHtml = "";
  
  for (var d = 0; d <= 9; d++) {
    var vol = conteos[d] || 0;
    var pct = Math.round((vol / maxVol) * 80); // Escalar al 80% de la altura
    var label = diasLabels[d] || ('Hace ' + (d + 1) + 'd');
    
    // Solo mostramos días que tienen algún artículo para mantener la limpieza
    var activeClass = _diasFiltroActivo === d ? 'active' : '';
    
    barsHtml += '<div class="timeline-bar-column ' + activeClass + '" data-dias="' + d + '" onclick="filtrarDias(' + d + ', this)" title="' + label + ': ' + vol + ' noticias">' +
      '<div class="timeline-bar-fill" style="height:' + pct + '%"></div>' +
      '</div>';
      
    ticksHtml += '<span class="timeline-tick" onclick="filtrarDias(' + d + ', this)">' + (d === 0 ? 'Hoy' : d === 1 ? 'Ayer' : d + 'd') + '</span>';
  }
  
  histContainer.innerHTML = barsHtml;
  if (ticksContainer) ticksContainer.innerHTML = ticksHtml;
}

// Filtra las noticias en el DOM según el día
function filtrarDias(dias, element) {
  _diasFiltroActivo = dias;
  
  // Actualizar botones rápidos
  document.querySelectorAll('.timeline-btn').forEach(function(btn) {
    var bD = btn.getAttribute('data-dias');
    if (bD === 'todos' && dias === null) {
      btn.classList.add('active');
    } else if (bD !== 'todos' && parseInt(bD) === dias) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });
  
  // Actualizar barras del histograma
  document.querySelectorAll('.timeline-bar-column').forEach(function(col) {
    var colD = parseInt(col.getAttribute('data-dias'));
    if (colD === dias) {
      col.classList.add('active');
    } else {
      col.classList.remove('active');
    }
  });
  
  // Lanzar la búsqueda con los nuevos parámetros
  var buscador = document.getElementById('buscador');
  buscar(buscador ? buscador.value : '');
}


/* ── 3. Cartografía del Espectro de Noticias 2D ── */
function renderizarCartografia2D() {
  var chartWrap = document.getElementById('stat-scatter-chart');
  if (!chartWrap) return;
  
  // Obtener todas las tarjetas de la pestaña "Todas"
  var tarjetas = document.querySelectorAll('#tab-todas .tarjeta');
  if (tarjetas.length === 0) {
    chartWrap.innerHTML = '<span style="color:var(--txt-3);font-size:.78rem">Sin noticias para cartografiar hoy.</span>';
    return;
  }
  
  // Mapeo numérico de sesgos en el Eje X (10% a 90%)
  var sesgoXMappings = {
    'izquierda': 12,
    'centro-izquierda': 31,
    'centro': 50,
    'centro-derecha': 69,
    'derecha': 88,
    'desconocido': 50
  };
  
  var nodosHtml = [];
  
  tarjetas.forEach(function(t, idx) {
    var sesgoF = (t.dataset.sesgoFuente || 'desconocido').toLowerCase();
    var titulo = t.dataset.titulo || '';
    var fuente = t.dataset.fuente || '';
    var asombro = parseInt(t.dataset.asombro || 0);
    var novedad = parseInt(t.dataset.novedad || 2);
    
    // Indicador de señal IA (Y): combinamos novedad y asombro
    // Escala Y de 0 a 3 mapeada del 82% al 18% (coordenadas SVG invertidas)
    var signalVal = asombro + (novedad === 3 ? 1.5 : 0); // 0 a 4.5
    var pctY = 82 - (Math.min(signalVal, 4.5) / 4.5) * 64; // Mapeado limpio en la rejilla
    
    var pctX = sesgoXMappings[sesgoF] || 50;
    
    // Jittering sutil (desviación aleatoria de +-3%) para evitar solapamientos exactos
    var jitterX = (Math.random() - 0.5) * 5.5;
    var jitterY = (Math.random() - 0.5) * 3.5;
    var finalX = pctX + jitterX;
    var finalY = pctY + jitterY;
    
    var col = window.DIGEST_CONFIG.sesgoColores[sesgoF] || '#9ca3af';
    
    // Construir punto SVG (círculo con mirilla tipográfica premium)
    nodosHtml.push(
      '<g class="scatter-node" onclick="abrirArticuloDesdeGrafico(' + idx + ')" ' +
      'onmouseover="mostrarScatterTooltip(event, \'' + window.btoa(unescape(encodeURIComponent(titulo))) + '\', \'' + fuente + '\', ' + novedad + ', ' + asombro + ')" ' +
      'onmouseout="ocultarScatterTooltip()">' +
      '<circle cx="' + finalX + '%" cy="' + finalY + '%" r="5" fill="none" stroke="' + col + '" stroke-width="1.5"/>' +
      '<circle cx="' + finalX + '%" cy="' + finalY + '%" r="1.5" fill="' + col + '"/>' +
      '</g>'
    );
  });
  
  // Dibujar la rejilla académica
  chartWrap.innerHTML = 
    '<svg class="scatter-svg" viewBox="0 0 500 280" style="width:100%;height:auto;overflow:visible">' +
    '  <!-- Rejilla horizontal -->' +
    '  <line x1="8%" y1="18%" x2="92%" y2="18%" stroke="rgba(240,230,208,0.05)" stroke-width="1" stroke-dasharray="2,2"/>' +
    '  <line x1="8%" y1="50%" x2="92%" y2="50%" stroke="rgba(240,230,208,0.05)" stroke-width="1" stroke-dasharray="2,2"/>' +
    '  <line x1="8%" y1="82%" x2="92%" y2="82%" stroke="rgba(240,230,208,0.05)" stroke-width="1"/>' +
    '  <!-- Eje vertical (Centro) -->' +
    '  <line x1="50%" y1="12%" x2="50%" y2="84%" stroke="rgba(240,230,208,0.04)" stroke-width="1"/>' +
    '  <!-- Nodos de noticias -->' +
    '  ' + nodosHtml.join('\n') +
    '  <!-- Leyenda de Ejes en SVG -->' +
    '  <text x="50%" y="94%" fill="var(--txt-3)" font-size="9" text-anchor="middle" font-family="ui-monospace, monospace">ESPECTRO IDEOLÓGICO DE LA FUENTE</text>' +
    '  <text x="8%" y="93%" fill="var(--txt-3)" font-size="8" text-anchor="start" font-family="ui-monospace, monospace">IZQUIERDA</text>' +
    '  <text x="92%" y="93%" fill="var(--txt-3)" font-size="8" text-anchor="end" font-family="ui-monospace, monospace">DERECHA</text>' +
    '  <text x="2%" y="50%" fill="var(--txt-3)" font-size="9" text-anchor="middle" transform="rotate(-90 2 50)" font-family="ui-monospace, monospace">CALIDAD / SEÑAL IA</text>' +
    '  <text x="6%" y="21%" fill="var(--txt-3)" font-size="8" font-family="ui-monospace, monospace">Alta Señal (Asombro/Señal)</text>' +
    '  <text x="6%" y="81%" fill="var(--txt-3)" font-size="8" font-family="ui-monospace, monospace">Rutina (Ruido/Reiteración)</text>' +
    '</svg>' +
    '<div id="scatter-tooltip" class="scatter-tooltip"></div>';
}

function abrirArticuloDesdeGrafico(idx) {
  var tarjetas = document.querySelectorAll('#tab-todas .tarjeta');
  if (idx >= 0 && idx < tarjetas.length) {
    abrirArticulo(tarjetas[idx]);
  }
}

function mostrarScatterTooltip(ev, tituloB64, fuente, novedad, asombro) {
  var tooltip = document.getElementById('scatter-tooltip');
  if (!tooltip) return;
  
  var titulo = decodeURIComponent(escape(window.atob(tituloB64)));
  var lang = localStorage.getItem('digestLang') || 'es';
  var novTxt = novedad === 3 ? (lang === 'en' ? 'Informativa (Signal)' : 'Informativa (Señal)') : (lang === 'en' ? 'Standard' : 'Estándar');
  var asombroTxt = '✦'.repeat(asombro) + '✧'.repeat(3 - asombro);
  
  tooltip.innerHTML = '<div class="st-fuente">' + fuente.toUpperCase() + '</div>' +
    '<div class="st-titulo">' + titulo + '</div>' +
    '<div class="st-meta">' +
    '  <span>' + (lang === 'en' ? 'Novelty: ' : 'Novedad: ') + novTxt + '</span> · ' +
    '  <span>' + (lang === 'en' ? 'Signal: ' : 'Interés: ') + asombroTxt + '</span>' +
    '</div>';
    
  tooltip.style.display = 'block';
  
  // Posicionar tooltip cerca del puntero del ratón
  var x = ev.clientX + 15;
  var y = ev.clientY + 15;
  
  // Ajustar si se sale de la pantalla
  var w = window.innerWidth;
  if (x + 220 > w) x = ev.clientX - 235;
  
  tooltip.style.left = x + 'px';
  tooltip.style.top = y + 'px';
}

function ocultarScatterTooltip() {
  var tooltip = document.getElementById('scatter-tooltip');
  if (tooltip) tooltip.style.display = 'none';
}
