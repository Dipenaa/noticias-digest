/* ── Boletín de Voz (Audio Player & TTS Queue) ── */
var _colaAudio = [];
var _audioIndex = -1;
var _isPlayingAudio = false;
var _audioSynth = window.speechSynthesis;
var _audioUtterance = null;
var _audioCtx = null;

// Inicializa el AudioContext bajo demanda por restricciones de interacción del navegador
function _obtenerAudioContext() {
  if (!_audioCtx) {
    _audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  }
  if (_audioCtx.state === 'suspended') {
    _audioCtx.resume();
  }
  return _audioCtx;
}

// Genera el timbre senoidal grave (150Hz, 250ms) clásico de radio informativa
function sonarTonoTransicion(callback) {
  try {
    var ctx = _obtenerAudioContext();
    var osc = ctx.createOscillator();
    var gain = ctx.createGain();
    
    osc.connect(gain);
    gain.connect(ctx.destination);
    
    osc.type = 'sine';
    osc.frequency.setValueAtTime(150, ctx.currentTime); // 150 Hz
    gain.gain.setValueAtTime(0.12, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.25);
    
    osc.start();
    osc.stop(ctx.currentTime + 0.25);
    
    setTimeout(callback, 280); // Inicia la síntesis de voz tras extinguirse el tono
  } catch (e) {
    // Fallback silencioso si falla la inicialización de audio
    callback();
  }
}

// Añade/quita un artículo de la cola de audio
function toggleAudioQueue(ev, btn) {
  if (ev) ev.stopPropagation();
  var d = btn.dataset;
  var enlace = d.enlace;
  var idx = _colaAudio.findIndex(function(x) { return x.enlace === enlace; });
  
  if (idx >= 0) {
    // Quitar de la cola
    _colaAudio.splice(idx, 1);
    btn.classList.remove('en-cola');
    btn.title = "Añadir al boletín de voz";
    // Si quitamos el artículo que estaba sonando o la cola se vacía
    if (_audioIndex === idx) {
      detenerAudio();
      _audioIndex = _colaAudio.length > 0 ? 0 : -1;
    } else if (_audioIndex > idx) {
      _audioIndex--;
    }
  } else {
    // Añadir a la cola
    _colaAudio.push({
      enlace: enlace,
      titulo: d.titulo,
      fuente: d.fuente,
      resumen: d.resumen || "",
      fecha: d.fecha
    });
    btn.classList.add('en-cola');
    btn.title = "Quitar del boletín de voz";
  }
  
  _sincronizarBotonesAudioDOM();
  actualizarAudioUI();
}

// Sincroniza el estado de los botones [🔊] en las tarjetas
function _sincronizarBotonesAudioDOM() {
  var enlacesEnCola = new Set(_colaAudio.map(function(x) { return x.enlace; }));
  document.querySelectorAll('.audio-queue-btn').forEach(function(btn) {
    if (enlacesEnCola.has(btn.dataset.enlace)) {
      btn.classList.add('en-cola');
      btn.title = "Quitar del boletín de voz";
    } else {
      btn.classList.remove('en-cola');
      btn.title = "Añadir al boletín de voz";
    }
  });
}

// Arranca o pausa la reproducción del boletín
function toggleAudioPlayback() {
  if (_colaAudio.length === 0) return;
  
  // Detener el lector del drawer si está activo
  if (typeof cancelVoz === 'function') cancelVoz();
  
  if (_isPlayingAudio) {
    pausarAudio();
  } else {
    if (_audioIndex === -1) _audioIndex = 0;
    reproducirArticuloCola(_audioIndex);
  }
}

function reproducirArticuloCola(idx) {
  if (idx < 0 || idx >= _colaAudio.length) {
    detenerAudio();
    return;
  }
  
  _audioSynth.cancel();
  _audioIndex = idx;
  _isPlayingAudio = true;
  actualizarAudioUI();
  
  var art = _colaAudio[_audioIndex];
  var lang = localStorage.getItem('digestLang') || 'es';
  var texto = "";
  
  if (lang === 'en') {
    texto = "Story " + (idx + 1) + ". " + art.titulo + ". From " + art.fuente + ". " + art.resumen;
  } else {
    texto = "Noticia " + (idx + 1) + ". " + art.titulo + ". De " + art.fuente + ". " + art.resumen;
  }
  
  sonarTonoTransicion(function() {
    if (!_isPlayingAudio) return; // Por si se pausa durante el tono de transición
    
    _audioUtterance = new SpeechSynthesisUtterance(texto);
    _audioUtterance.lang = lang === 'en' ? 'en-US' : 'es-ES';
    _audioUtterance.rate = 1.05;
    
    var voices = _audioSynth.getVoices();
    var voice = voices.find(function(v) { return v.lang && v.lang.startsWith(lang); });
    if (voice) _audioUtterance.voice = voice;
    
    _audioUtterance.onstart = function() {
      actualizarAudioUI();
    };
    
    _audioUtterance.onend = function() {
      if (_isPlayingAudio) {
        if (_audioIndex < _colaAudio.length - 1) {
          reproducirArticuloCola(_audioIndex + 1);
        } else {
          detenerAudio();
        }
      }
    };
    
    _audioUtterance.onerror = function(e) {
      if (e.error !== 'interrupted') {
        detenerAudio();
      }
    };
    
    _audioSynth.speak(_audioUtterance);
  });
}

function pausarAudio() {
  _audioSynth.cancel();
  _isPlayingAudio = false;
  actualizarAudioUI();
}

function detenerAudio() {
  _audioSynth.cancel();
  _isPlayingAudio = false;
  _audioIndex = -1;
  actualizarAudioUI();
}

function playAudioNext() {
  if (_audioIndex < _colaAudio.length - 1) {
    reproducirArticuloCola(_audioIndex + 1);
  }
}

function playAudioPrev() {
  if (_audioIndex > 0) {
    reproducirArticuloCola(_audioIndex - 1);
  }
}

function limpiarColaAudio() {
  detenerAudio();
  _colaAudio = [];
  _sincronizarBotonesAudioDOM();
  actualizarAudioUI();
}

function minimizarAudioPlayer() {
  var player = document.getElementById('audio-player-wrap');
  if (player) player.classList.toggle('minimizado');
}

// Actualiza el estado visual del reproductor
/* ── Sonidos de interfaz ──────────────────────────────────────────── */

/* Genera ruido rosa (1/f) — suena mucho más natural que ruido blanco */
function _ruidoRosa(d) {
  var b0=0,b1=0,b2=0,b3=0,b4=0,b5=0;
  for (var i = 0; i < d.length; i++) {
    var w = Math.random() * 2 - 1;
    b0 = 0.99886*b0 + w*0.0555179; b1 = 0.99332*b1 + w*0.0750759;
    b2 = 0.96900*b2 + w*0.1538520; b3 = 0.86650*b3 + w*0.3104856;
    b4 = 0.55000*b4 + w*0.5329522; b5 = -0.7616*b5 - w*0.0168980;
    d[i] = (b0+b1+b2+b3+b4+b5 + w*0.5362) * 0.11;
  }
}

function sonidoPasarPagina() {
  try {
    var ctx = _obtenerAudioContext();
    var dur = 0.48, sr = ctx.sampleRate;
    var buf = ctx.createBuffer(1, Math.floor(sr * dur), sr);
    var d   = buf.getChannelData(0);
    _ruidoRosa(d);

    /* Envolvente: sube suave → pico en 20% → decae orgánicamente */
    for (var i = 0; i < d.length; i++) {
      var t = i / d.length;
      d[i] *= t < 0.2 ? t / 0.2 : Math.pow(1 - (t - 0.2) / 0.8, 2.2);
    }

    var src = ctx.createBufferSource();
    src.buffer = buf;

    /* Filtro que barre de 600 Hz → 2200 Hz → 900 Hz: da el "vuelo" de la página */
    var bp = ctx.createBiquadFilter();
    bp.type = 'bandpass'; bp.Q.value = 0.7;
    bp.frequency.setValueAtTime(600,  ctx.currentTime);
    bp.frequency.linearRampToValueAtTime(2200, ctx.currentTime + 0.18);
    bp.frequency.exponentialRampToValueAtTime(900, ctx.currentTime + dur);

    /* Realce de agudos para textura de papel */
    var hs = ctx.createBiquadFilter();
    hs.type = 'highshelf'; hs.frequency.value = 2000; hs.gain.value = 7;

    var gain = ctx.createGain();
    gain.gain.setValueAtTime(0.09, ctx.currentTime);

    src.connect(bp); bp.connect(hs); hs.connect(gain); gain.connect(ctx.destination);
    src.start();
  } catch(e) {}
}

function sonidoArrugarPapel() {
  try {
    var ctx = _obtenerAudioContext();
    var dur = 0.22, sr = ctx.sampleRate;
    var buf = ctx.createBuffer(1, Math.floor(sr * dur), sr);
    var d   = buf.getChannelData(0);
    _ruidoRosa(d);

    /* Envolvente muy rápida con pequeños baches: simula pliegues irregulares */
    for (var i = 0; i < d.length; i++) {
      var t = i / d.length;
      var env = Math.exp(-14 * t) * (1 + 0.4 * Math.sin(2 * Math.PI * 22 * t));
      d[i] *= env;
    }

    var src = ctx.createBufferSource();
    src.buffer = buf;

    var bp = ctx.createBiquadFilter();
    bp.type = 'bandpass'; bp.frequency.value = 2800; bp.Q.value = 0.55;

    var hs = ctx.createBiquadFilter();
    hs.type = 'highshelf'; hs.frequency.value = 1500; hs.gain.value = 5;

    var gain = ctx.createGain();
    gain.gain.setValueAtTime(0.13, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + dur);

    src.connect(bp); bp.connect(hs); hs.connect(gain); gain.connect(ctx.destination);
    src.start();
  } catch(e) {}
}

function actualizarAudioUI() {
  var player = document.getElementById('audio-player-wrap');
  var playBtn = document.getElementById('audio-btn-play');
  var statusText = document.getElementById('audio-player-status');
  var progressBar = document.getElementById('audio-progress-bar');
  
  if (!player) return;
  
  var lang = localStorage.getItem('digestLang') || 'es';
  
  if (_colaAudio.length === 0) {
    player.classList.remove('visible');
    progressBar.style.width = "0%";
    statusText.textContent = lang === 'en' ? "Queue empty" : "Cola vacía";
    return;
  }
  
  player.classList.add('visible');
  
  // Actualizar botón de play
  if (playBtn) {
    if (_isPlayingAudio) {
      playBtn.classList.add('playing');
      playBtn.innerHTML = "&#9612;&#9612;"; // Pausa (dos barras)
      playBtn.title = lang === 'en' ? "Pause" : "Pausar";
    } else {
      playBtn.classList.remove('playing');
      playBtn.innerHTML = "&#9654;"; // Play
      playBtn.title = lang === 'en' ? "Play" : "Reproducir";
    }
  }
  
  // Actualizar barra de progreso
  if (progressBar) {
    var pct = 0;
    if (_audioIndex >= 0) {
      pct = ((_audioIndex + 1) / _colaAudio.length) * 100;
    }
    progressBar.style.width = pct + "%";
  }
  
  // Actualizar texto de estado
  if (statusText) {
    if (_audioIndex >= 0) {
      var art = _colaAudio[_audioIndex];
      statusText.textContent = (lang === 'en' ? "Playing " : "Leyendo ") + (_audioIndex + 1) + "/" + _colaAudio.length + ": " + art.fuente;
    } else {
      statusText.textContent = _colaAudio.length + (lang === 'en' ? " articles in queue" : " noticias en cola");
    }
  }
  
  // Control de botones de navegación
  var prevBtn = document.getElementById('audio-btn-prev');
  var nextBtn = document.getElementById('audio-btn-next');
  if (prevBtn) prevBtn.disabled = (_audioIndex <= 0);
  if (nextBtn) nextBtn.disabled = (_audioIndex >= _colaAudio.length - 1 || _audioIndex === -1);
}
