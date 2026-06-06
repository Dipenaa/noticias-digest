/* ── Inicialización ───────────────────────────────────────────────────── */

/* Splash */
function dismissSplash() {
  var s = document.getElementById('splash');
  if (!s || s.classList.contains('saliendo')) return;
  s.classList.add('saliendo');
  setTimeout(function() { s.classList.add('ido'); }, 720);
}

(function() {
  var s = document.getElementById('splash');
  if (!s) return;
  try {
    var today = new Date().toDateString();
    if (localStorage.getItem('digestSplashDate') === today) { s.classList.add('ido'); return; }
    localStorage.setItem('digestSplashDate', today);
  } catch(e) {}
  setTimeout(dismissSplash, 2600);
})();

/* Saludo según hora */
(function() {
  var h = new Date().getHours();
  var g = h < 6 ? 'Buenas noches' : h < 14 ? 'Buenos días' : h < 21 ? 'Buenas tardes' : 'Buenas noches';
  var el = document.getElementById('header-greeting');
  if (el) el.textContent = g;
})();

/* Modo día / oscuro */
function toggleDark() {
  var light = document.body.classList.toggle('light');
  try { localStorage.setItem('digestLight', light ? '1' : '0'); } catch(e) {}
  var btn = document.getElementById('dark-toggle');
  if (btn) btn.textContent = light ? '☾ Modo oscuro' : '☀ Modo día';
}

(function() {
  try {
    var pref = localStorage.getItem('digestLight');
    var btn = document.getElementById('dark-toggle');
    if (pref === '0') {            /* el usuario eligió oscuro explícitamente */
      document.body.classList.remove('light');
      if (btn) btn.textContent = '☀ Modo día';
    } else {                        /* por defecto (o '1') → día claro */
      document.body.classList.add('light');
      if (btn) btn.textContent = '☾ Modo oscuro';
    }
  } catch(e) {}
})();

/* Sidebar toggle */
function toggleSidebar() {
  var hidden = document.body.classList.toggle('sidebar-hidden');
  try { localStorage.setItem('digestSidebarHidden', hidden ? '1' : '0'); } catch(e) {}
}

(function() {
  try {
    if (localStorage.getItem('digestSidebarHidden') === '1') {
      document.body.classList.add('sidebar-hidden');
    }
  } catch(e) {}
})();


/* Restaurar keywords guardadas */
(function() {
  try {
    var kw = localStorage.getItem('digestKeywords');
    if (kw) {
      var kwInput = document.getElementById('kw-input');
      if (kwInput) { kwInput.value = kw; aplicarKeywords(kw); }
    }
  } catch(e) {}
})();

/* Restaurar bookmarks y abrir la última pestaña */
(function() {
  try { _actualizarContadorBK(); } catch(e) {}

  var last = 'destacadas';
  try {
    var saved = localStorage.getItem('digestTab') || 'destacadas';
    last = (saved === 'todas') ? 'destacadas' : saved;
  } catch(e) {}

  switchTab(last);
})();

/* ── Traducciones y Multilenguaje ────────────────────────────────────── */
var _TRANSLATIONS = {
  'es': {
    'lang_label': 'Idioma:',
    'sort_label': 'Ordenar:',
    'sort_defecto': 'Por defecto',
    'sort_recientes': 'Más recientes',
    'sort_antiguos': 'Más antiguos',
    'sort_novedad': 'Por novedad',
    'sort_sesgo_izq': 'Sesgo ← izquierda',
    'sort_sesgo_der': 'Sesgo → derecha',
    'search_placeholder': 'Buscar en noticias...',
    'legend_label': 'Espectrómetro Editorial:',
    'legend_tip': '(deslice o haga clic para filtrar)',
    'legend_clear': '✕ Quitar filtro',
    'meta_news': 'noticias',
    'meta_alts': 'alternativas',
    'drawer_ia': 'IA:',
    'footer_text': 'Sin publicidad · Sin algoritmos · Generado localmente · Análisis por Claude (Anthropic)',
    'drawer_reading': 'min',
    'drawer_source': 'Fuente:',
    'drawer_btn_read': 'Leer artículo ↗',
    'drawer_btn_translate': '🌐 Traducir',
    'drawer_btn_share': 'Copiar enlace',
    'drawer_btn_voice': '🔊 Escuchar',
    'drawer_btn_voice_stop': '⏹ Detener',
    'ia_title_tono': 'Tono Emocional',
    'ia_title_novedad': 'Índice de Novedad',
    'tab_destacadas': 'Destacadas',
    'tab_todas': 'Todas las noticias',
    'tab_sintesis': 'Síntesis',
    'tab_libertaria': 'Izquierda Crítica',
    'tab_actualidad': 'Actualidad',
    'tab_asombro': 'Asombro',
    'tab_para-leer': 'Para leer',
    'tab_stats': 'Estadísticas',
    'dark_mode': '🌙 Modo oscuro',
    'light_mode': '☀️ Modo claro',
    
    // Nuevas cadenas Premium
    'enfoque_label': 'Enfoque:',
    'enfoque_zen': 'Objetivo',
    'enfoque_normal': 'Normal',
    'enfoque_alerta': 'Alerta',
    'timeline_label': 'Filtrar por fecha:',
    'time_todos': 'Todos',
    'time_hoy': 'Hoy',
    'time_hoy_ayer': 'Hoy y ayer',
    'time_3d': '3 días',
    'time_5d': '5 días',
    'time_10d': '10 días',
    'contrapeso_title': 'Contrapeso Editorial',
    'contrapeso_desc': 'Lee una perspectiva diferente sobre esta misma historia en medios del espectro opuesto:',
    'barometer_title': 'Tensión Semántica',
    'barometer_modal_title': 'Análisis de Tensión Semántica',
    'barometer_modal_desc': 'Análisis de la retórica emocional y lenguaje alarmista detectado en las noticias de hoy.',
    'barometer_lbl_pct': 'Titulares Alarmistas',
    'barometer_lbl_status': 'Clima Mediático',
    'barometer_vocab_title': 'Términos Alarmistas Clave Detectados',
    'audio_player_title': 'Boletín de Voz',
    'audio_status_empty': 'Cola vacía',
    'audio_btn_clear': 'Vaciar',
    'calibrator_title': 'Laboratorio de Enmarque y Contraste',
    'calibrator_desc': 'Compara y analiza cómo construyen el relato los distintos medios sobre un mismo hecho, estudiando sus técnicas lingüísticas, perfil ideológico y enmarque periodístico.',
    'lab_selector_label': 'Seleccionar artículo de hoy para desglosar:',
    'lab_select_placeholder': 'Seleccione una noticia de la lista...',
    'lab_calibrador_label': '¿Cómo percibes tú el sesgo/enfoque de este redactado?',
    'lab_btn_revelar': 'Estudiar Enmarque e Intención',
    'lab_analysis_title': 'Análisis del Enmarque',
    'lab_media_profile_title': 'Ficha Técnica de la Cabecera',
    'lab_contrapeso_title': 'Perspectiva Alternativa de Hoy',
    'lab_contrapeso_desc': 'Lee cómo cubren esta misma categoría otros medios del espectro político opuesto:',
    'sesgo_izq_abreviado': 'Izquierda',
    'sesgo_c_izq_abreviado': 'C-Izq',
    'sesgo_ctr_abreviado': 'Centro',
    'sesgo_c_der_abreviado': 'C-Der',
    'sesgo_der_abreviado': 'Derecha',
    'scatter_chart_title': 'Cartografía del Espectro de Noticias'
  },
  'en': {
    'lang_label': 'Language:',
    'sort_label': 'Sort by:',
    'sort_defecto': 'Default',
    'sort_recientes': 'Newest',
    'sort_antiguos': 'Oldest',
    'sort_novedad': 'Novelty',
    'sort_sesgo_izq': 'Bias ← Left',
    'sort_sesgo_der': 'Bias → Right',
    'search_placeholder': 'Search news...',
    'legend_label': 'Editorial Spectrometer:',
    'legend_tip': '(slide or click to filter)',
    'legend_clear': '✕ Clear filter',
    'meta_news': 'news',
    'meta_alts': 'alternatives',
    'drawer_ia': 'AI:',
    'footer_text': 'No ads · No algorithms · Generated locally · Analysis by Claude (Anthropic)',
    'drawer_reading': 'min',
    'drawer_source': 'Source:',
    'drawer_btn_read': 'Read article ↗',
    'drawer_btn_translate': '🌐 Translate',
    'drawer_btn_share': 'Copy link',
    'drawer_btn_voice': '🔊 Listen',
    'drawer_btn_voice_stop': '⏹ Stop',
    'ia_title_tono': 'Emotional Tone',
    'ia_title_novedad': 'Novelty Index',
    'tab_destacadas': 'Highlights',
    'tab_todas': 'All News',
    'tab_sintesis': 'Syntheses',
    'tab_libertaria': 'Critical Left',
    'tab_actualidad': 'Trends',
    'tab_asombro': 'Insights',
    'tab_para-leer': 'Bookmarks',
    'tab_stats': 'Statistics',
    'dark_mode': '🌙 Dark mode',
    'light_mode': '☀️ Light mode',
    
    // New Premium strings
    'enfoque_label': 'Focus:',
    'enfoque_zen': 'Objective',
    'enfoque_normal': 'Normal',
    'enfoque_alerta': 'Alert',
    'timeline_label': 'Filter by date:',
    'time_todos': 'All',
    'time_hoy': 'Today',
    'time_hoy_ayer': 'Today & yesterday',
    'time_3d': '3 days',
    'time_5d': '5 days',
    'time_10d': '10 days',
    'contrapeso_title': 'Editorial Counterweight',
    'contrapeso_desc': 'Read an alternative perspective on this story from the opposite spectrum:',
    'barometer_title': 'Semantic Tension',
    'barometer_modal_title': 'Semantic Tension Analysis',
    'barometer_modal_desc': 'Analysis of emotional rhetoric and alarmist language detected in today\'s news.',
    'barometer_lbl_pct': 'Alarmist Headlines',
    'barometer_lbl_status': 'Media Climate',
    'barometer_vocab_title': 'Key Alarmist Terms Detected',
    'audio_player_title': 'Voice Digest',
    'audio_status_empty': 'Queue empty',
    'audio_btn_clear': 'Clear',
    'calibrator_title': 'Editorial Framing & Contrast Laboratory',
    'calibrator_desc': 'Compare and analyze how different outlets frame the same news story, studying their linguistic style, historical profile, and political perspective.',
    'lab_selector_label': 'Select an article to analyze:',
    'lab_select_placeholder': 'Choose a story from the list...',
    'lab_calibrador_label': 'How do you personally perceive the bias/framing of this text?',
    'lab_btn_revelar': 'Study Framing & Editorial Intent',
    'lab_analysis_title': 'Framing Analysis',
    'lab_media_profile_title': 'Publisher Fact Sheet',
    'lab_contrapeso_title': 'Alternative Perspective Today',
    'lab_contrapeso_desc': 'Read how other outlets from the opposing political spectrum cover the same topic:',
    'sesgo_izq_abreviado': 'Left',
    'sesgo_c_izq_abreviado': 'C-Left',
    'sesgo_ctr_abreviado': 'Center',
    'sesgo_c_der_abreviado': 'C-Right',
    'sesgo_der_abreviado': 'Right',
    'scatter_chart_title': 'News Spectrum Mapping'
  }
};

function changeLanguage(lang) {
  try { localStorage.setItem('digestLang', lang); } catch(e) {}
  
  // Resaltar botón activo
  document.querySelectorAll('.lang-btn').forEach(function(b) {
    if (b.getAttribute('data-lang') === lang) {
      b.classList.add('active');
    } else {
      b.classList.remove('active');
    }
  });

  // Traducir todos los elementos con data-translate
  document.querySelectorAll('[data-translate]').forEach(function(el) {
    var key = el.getAttribute('data-translate');
    if (_TRANSLATIONS[lang] && _TRANSLATIONS[lang][key]) {
      var txt = _TRANSLATIONS[lang][key];
      if (el.tagName === 'INPUT') {
        el.setAttribute('placeholder', txt);
      } else {
        // Preservar cualquier elemento hijo como badges de conteo si existen
        var child = el.querySelector('.tab-count, style');
        if (child) {
          el.innerHTML = '<span data-translate-text="true">' + txt + '</span>';
          el.appendChild(child);
        } else {
          el.textContent = txt;
        }
      }
    }
  });
  
  // Traducción especial para el toggle de modo oscuro
  var btn = document.getElementById('dark-toggle');
  if (btn) {
    var isLight = document.body.classList.contains('light');
    if (lang === 'en') {
      btn.textContent = isLight ? '🌙 Dark mode' : '☀️ Light mode';
    } else {
      btn.textContent = isLight ? '🌙 Modo oscuro' : '☀️ Modo claro';
    }
  }
}

// Inicializar idioma al cargar e invocar componentes visuales/juego
(function() {
  try {
    var savedLang = localStorage.getItem('digestLang') || 'es';
    changeLanguage(savedLang);
  } catch(e) {}
  
  try {
    if (typeof inicializarTimelineHistogram === 'function') inicializarTimelineHistogram();
    if (typeof inicializarBarometroTension === 'function') inicializarBarometroTension();
  } catch(e) {}
})();
