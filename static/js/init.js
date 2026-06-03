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
    'sort_relevancia': 'Por relevancia',
    'sort_novedad': 'Por novedad',
    'sort_sesgo_izq': 'Sesgo ← izquierda',
    'sort_sesgo_der': 'Sesgo → derecha',
    'search_placeholder': 'Buscar en noticias...',
    'legend_label': 'Leyenda:',
    'legend_tip': '(clic para filtrar)',
    'legend_clear': '✕ Quitar filtro',
    'meta_news': 'noticias',
    'meta_alts': 'alternativas',
    'footer_text': 'Sin publicidad · Sin algoritmos · Generado localmente · Análisis por IA (Gemini)',
    'drawer_reading': 'min',
    'drawer_source': 'Fuente:',
    'drawer_ia': 'IA:',
    'drawer_btn_read': 'Leer artículo ↗',
    'drawer_btn_translate': '🌐 Traducir',
    'drawer_btn_share': 'Copiar enlace',
    'ia_title_sesgo': 'Sesgo Político IA',
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
    'light_mode': '☀️ Modo claro'
  },
  'en': {
    'lang_label': 'Language:',
    'sort_label': 'Sort by:',
    'sort_defecto': 'Default',
    'sort_recientes': 'Newest',
    'sort_relevancia': 'Relevance',
    'sort_novedad': 'Novelty',
    'sort_sesgo_izq': 'Bias ← Left',
    'sort_sesgo_der': 'Bias → Right',
    'search_placeholder': 'Search news...',
    'legend_label': 'Legend:',
    'legend_tip': '(click to filter)',
    'legend_clear': '✕ Clear filter',
    'meta_news': 'news',
    'meta_alts': 'alternatives',
    'footer_text': 'No ads · No algorithms · Generated locally · AI analysis (Gemini)',
    'drawer_reading': 'min',
    'drawer_source': 'Source:',
    'drawer_ia': 'AI:',
    'drawer_btn_read': 'Read article ↗',
    'drawer_btn_translate': '🌐 Translate',
    'drawer_btn_share': 'Copy link',
    'ia_title_sesgo': 'AI Political Bias',
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
    'light_mode': '☀️ Light mode'
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

// Inicializar idioma al cargar
(function() {
  try {
    var savedLang = localStorage.getItem('digestLang') || 'es';
    changeLanguage(savedLang);
  } catch(e) {}
})();
