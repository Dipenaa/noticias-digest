/* ── Vista inmersiva (drawer de artículo y Contrapeso Editorial) ── */
var _isPlayingVoz = false;
var _utterance = null;
var _synth = window.speechSynthesis;

function abrirArticulo(el) {
  cancelVoz();
  if (typeof detenerAudio === 'function') detenerAudio(); // Detener reproductor global
  
  var d       = el.dataset;
  var titulo  = d.titulo    || '';
  var fuente  = d.fuente    || '';
  var fecha   = d.fecha     || '';
  var enlace  = d.enlace    || '#';
  var resumen = d.resumen   || '';
  var critica = d.critica   || '';
  var sesgoF  = d.sesgoFuente || 'desconocido';
  var sesgoIA = d.sesgoIa   || 'desconocido';

  var secEl = el.closest('.seccion');
  var cat   = secEl ? (secEl.querySelector('.seccion-titulo') || {}).textContent || '' : (d.categoria || '');

  var palabras = (titulo + ' ' + resumen).split(/\s+/).filter(Boolean).length;
  var minutos  = Math.max(1, Math.round(palabras / 200));

  document.getElementById('d-categoria').textContent = cat;
  document.getElementById('d-fuente').textContent    = fuente;
  document.getElementById('d-fecha').textContent     = fecha;
  document.getElementById('d-reading').textContent   = minutos;
  document.getElementById('d-titulo').textContent    = titulo;
  document.getElementById('d-resumen').textContent   = resumen;

  var badgeF = document.getElementById('d-sesgo-f');
  if (badgeF) {
    badgeF.textContent = sesgoF.toUpperCase();
    badgeF.style.background = (window.DIGEST_CONFIG.sesgoColores[sesgoF] || '#9ca3af');
    badgeF.setAttribute('title', sesgoF);
  }

  var badgeIA = document.getElementById('d-sesgo-ia');
  if (badgeIA && window.DIGEST_CONFIG.sesgoColores) {
    badgeIA.textContent = sesgoIA.toUpperCase();
    badgeIA.style.background = (window.DIGEST_CONFIG.sesgoColores[sesgoIA] || '#9ca3af');
    badgeIA.setAttribute('title', sesgoIA);
  }

  var sentEl = document.getElementById('d-sent');
  if (sentEl) {
    var sent = (d.sentimiento || '').toLowerCase();
    var sentIconos = {'alarmista': '⚠ ALARMISTA', 'optimista': '✦ OPTIMISTA', 'neutral': '◉ NEUTRAL'};
    sentEl.textContent = sentIconos[sent] || '';
    sentEl.className = 'badge-sent ' + (sent === 'alarmista' ? 'badge-sent-alarmista' : sent === 'optimista' ? 'badge-sent-optimista' : 'badge-sent-neutral');
  }

  var preguntaEl = document.getElementById('d-pregunta');
  if (preguntaEl) {
    var preg = d.pregunta || '';
    if (preg) { preguntaEl.textContent = '↳ ' + preg; preguntaEl.style.display = ''; }
    else { preguntaEl.style.display = 'none'; }
  }

  var criticaEl = document.getElementById('d-critica');
  if (critica) {
    criticaEl.textContent  = '💡 ' + critica;
    criticaEl.style.display = '';
  } else {
    criticaEl.style.display = 'none';
  }

  // Ficha de Análisis Editorial IA (Excluyendo Escala de Sesgo IA)
  var descripcionesSentimiento = {
    'alarmista': 'Redacción con tintes catastrofistas, exageración de riesgos o lenguaje de urgencia constante.',
    'neutral': 'Tono descriptivo e institucional, centrado en hechos contrastables y sin carga emocional perceptible.',
    'optimista': 'Énfasis constructivo en avances, soluciones viables, logros sociales o económicos.',
    '': 'Tono descriptivo e institucional, centrado en hechos contrastables y sin carga emocional perceptible.'
  };

  var nombresSentimiento = {
    'alarmista': '⚠ Alarmista',
    'neutral': '◉ Neutral',
    'optimista': '✦ Optimista',
    '': '◉ Neutral'
  };

  var descripcionesNovedad = {
    '3': 'Aporta información inédita, datos primarios o revelaciones que añaden valor sustancial al debate.',
    '2': 'Cobertura informativa regular de hechos en desarrollo, sin revelaciones mayores pero relevante.',
    '1': 'Reitera marcos o datos ya publicados previamente. Contribuye al ruido informativo del día.',
    '0': 'Reitera marcos o datos ya publicados previamente. Contribuye al ruido informativo del día.'
  };

  var nombresNovedad = {
    '3': '◆ Señal (Información Nueva)',
    '2': '● Estándar (Seguimiento)',
    '1': '⇅ Repetición (Ruido)',
    '0': '⇅ Repetición (Ruido)'
  };

  var panelIA = document.getElementById('d-analisis-ia');
  if (panelIA) {
    var sent = (d.sentimiento || '').toLowerCase();
    var nov = d.novedad || '2';

    if (sent || nov !== '2' || critica) {
      panelIA.style.display = 'flex';

      var valSent = document.getElementById('d-val-sentimiento');
      if (valSent) valSent.textContent = nombresSentimiento[sent] || nombresSentimiento[''];

      var descSent = document.getElementById('d-desc-sentimiento');
      if (descSent) descSent.textContent = descripcionesSentimiento[sent] || descripcionesSentimiento[''];

      var valNov = document.getElementById('d-val-novedad');
      if (valNov) valNov.textContent = nombresNovedad[nov] || nombresNovedad['2'];

      var descNov = document.getElementById('d-desc-novedad');
      if (descNov) descNov.textContent = descripcionesNovedad[nov] || descripcionesNovedad['2'];
    } else {
      panelIA.style.display = 'none';
    }
  }

  // Lógica del Contrapeso Editorial (Perspectiva Inversa)
  var contrapesoDiv = document.getElementById('d-contrapeso');
  var contrapesoLink = document.getElementById('d-contrapeso-link');
  
  if (contrapesoDiv && contrapesoLink) {
    var opuesto = (sesgoF === 'izquierda' || sesgoF === 'centro-izquierda') ? ['derecha', 'centro-derecha'] : ['izquierda', 'centro-izquierda'];
    var linkTarget = null;
    
    if (secEl) {
      // Buscar un artículo con sesgo opuesto en la misma sección
      var otras = secEl.querySelectorAll('.tarjeta, .tarjeta-destacada');
      for (var i = 0; i < otras.length; i++) {
        var o = otras[i];
        if (o !== el) {
          var oSesgo = (o.dataset.sesgoFuente || 'desconocido').toLowerCase();
          if (opuesto.includes(oSesgo)) {
            linkTarget = o;
            break;
          }
        }
      }
    }
    
    if (linkTarget) {
      contrapesoDiv.style.display = 'block';
      contrapesoLink.textContent = linkTarget.dataset.titulo + " (" + linkTarget.dataset.fuente + ")";
      contrapesoLink.onclick = function(e) {
        e.preventDefault();
        abrirArticulo(linkTarget);
      };
    } else {
      // Fallback: Buscar en todo el DOM (todas las noticias) que tengan la misma categoría y sesgo opuesto
      var todasTarjetas = document.querySelectorAll('#tab-todas .tarjeta, #tab-todas .tarjeta-destacada');
      var actualCat = cat || el.dataset.categoria || '';
      for (var i = 0; i < todasTarjetas.length; i++) {
        var o = todasTarjetas[i];
        if (o !== el) {
          var oSesgo = (o.dataset.sesgoFuente || 'desconocido').toLowerCase();
          var oCat = o.dataset.categoria || o.closest('.tab-content')?.id?.replace('tab-', '') || '';
          if (opuesto.includes(oSesgo) && (oCat.toLowerCase() === actualCat.toLowerCase() || actualCat === '')) {
            linkTarget = o;
            break;
          }
        }
      }
      
      if (linkTarget) {
        contrapesoDiv.style.display = 'block';
        contrapesoLink.textContent = linkTarget.dataset.titulo + " (" + linkTarget.dataset.fuente + ")";
        contrapesoLink.onclick = function(e) {
          e.preventDefault();
          abrirArticulo(linkTarget);
        };
      } else {
        contrapesoDiv.style.display = 'none';
      }
    }
  }

  document.getElementById('d-btn-leer').href     = enlace;
  document.getElementById('d-btn-traducir').href = 'https://translate.google.com/translate?sl=auto&tl=es&u=' + encodeURIComponent(enlace);

  document.getElementById('drawer-overlay').classList.add('open');
  document.getElementById('drawer').classList.add('open');
  document.body.style.overflow = 'hidden';
  document.body.classList.add('drawer-open');
}

function cerrarDrawer() {
  cancelVoz();
  document.getElementById('drawer-overlay').classList.remove('open');
  document.getElementById('drawer').classList.remove('open');
  document.body.style.overflow = '';
  document.body.classList.remove('drawer-open');
}

function compartirArticulo() {
  var titulo = document.getElementById('d-titulo').textContent;
  var enlace = document.getElementById('d-btn-leer').href;
  var btn    = document.getElementById('d-btn-compartir');
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

/* ── Lector de voz del Drawer ── */
function toggleVozDrawer(ev) {
  if (ev) ev.stopPropagation();
  if (!_synth) {
    alert("Tu navegador no soporta síntesis de voz.");
    return;
  }
  if (_isPlayingVoz) {
    cancelVoz();
  } else {
    playVoz();
  }
}

function playVoz() {
  _synth.cancel();
  
  var titulo = document.getElementById('d-titulo').textContent || '';
  var resumen = document.getElementById('d-resumen').textContent || '';
  var fuente = document.getElementById('d-fuente').textContent || '';
  var lang = localStorage.getItem('digestLang') || 'es';

  var textoALeer = "";
  if (lang === 'en') {
    textoALeer = titulo + ". Published by " + fuente + ". Summary: " + resumen;
  } else {
    textoALeer = titulo + ". Publicado por " + fuente + ". Resumen: " + resumen;
  }

  _utterance = new SpeechSynthesisUtterance(textoALeer);
  _utterance.lang = lang === 'en' ? 'en-US' : 'es-ES';
  _utterance.rate = 1.05;

  var voices = _synth.getVoices();
  var voice = voices.find(function(v) { return v.lang && v.lang.startsWith(lang); });
  if (voice) _utterance.voice = voice;

  _utterance.onstart = function() {
    _isPlayingVoz = true;
    actualizarBotonVoz(true);
  };

  _utterance.onend = function() {
    _isPlayingVoz = false;
    actualizarBotonVoz(false);
  };

  _utterance.onerror = function(e) {
    if (e.error !== 'interrupted') {
      _isPlayingVoz = false;
      actualizarBotonVoz(false);
    }
  };

  _synth.speak(_utterance);
}

function cancelVoz() {
  if (_synth) {
    _synth.cancel();
  }
  _isPlayingVoz = false;
  actualizarBotonVoz(false);
}

function actualizarBotonVoz(playing) {
  var btn = document.getElementById('d-btn-voz');
  if (!btn) return;
  var lang = localStorage.getItem('digestLang') || 'es';
  if (playing) {
    btn.classList.add('playing');
    btn.innerHTML = lang === 'en' ? '⏹ Stop' : '⏹ Detener';
  } else {
    btn.classList.remove('playing');
    btn.innerHTML = lang === 'en' ? '🔊 Listen' : '🔊 Escuchar';
  }
}

document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') cerrarDrawer();
});

/* ── Lectura en voz alta desde tarjeta ── */
var _leerBtn = null;
function leerArticuloTarjeta(ev, btn) {
  ev.stopPropagation();
  if (_synth && _synth.speaking) {
    _synth.cancel();
    if (_leerBtn) { _leerBtn.classList.remove('leyendo'); _leerBtn.textContent = '🔊'; }
    if (_leerBtn === btn) { _leerBtn = null; return; }
  }
  var card = btn.closest('.tarjeta,.tarjeta-destacada,.asombro-card');
  if (!card) return;
  var titulo  = card.dataset.titulo  || '';
  var resumen = card.dataset.resumen || '';
  var texto   = titulo + (resumen ? '. ' + resumen : '');
  var u = new SpeechSynthesisUtterance(texto);
  u.lang = 'es-ES'; u.rate = 1.0;
  var voices = _synth.getVoices();
  var voice  = voices.find(function(v) { return v.lang && v.lang.startsWith('es'); });
  if (voice) u.voice = voice;
  _leerBtn = btn;
  btn.classList.add('leyendo'); btn.textContent = '⏹';
  u.onend  = function() { btn.classList.remove('leyendo'); btn.textContent = '🔊'; _leerBtn = null; };
  u.onerror = function(e) { if (e.error !== 'interrupted') { btn.classList.remove('leyendo'); btn.textContent = '🔊'; _leerBtn = null; } };
  _synth.speak(u);
}
