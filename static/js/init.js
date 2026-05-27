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

/* Modo oscuro */
function toggleDark() {
  var dark = document.body.classList.toggle('dark');
  try { localStorage.setItem('digestDark', dark ? '1' : '0'); } catch(e) {}
  var btn = document.getElementById('dark-toggle');
  if (btn) btn.textContent = dark ? '☀ Modo día' : '☾ Modo oscuro';
}

(function() {
  try {
    if (localStorage.getItem('digestDark') === '1') {
      document.body.classList.add('dark');
      var btn = document.getElementById('dark-toggle');
      if (btn) btn.textContent = '☀ Modo día';
    }
  } catch(e) {}
})();

/* Banner de IA (artículos sin análisis) */
(function() {
  try {
    var sinIA       = document.querySelectorAll('[data-sesgo-ia="desconocido"]').length;
    var bannerCount = document.getElementById('ia-banner-count');
    var bannerEl    = document.getElementById('ia-banner');
    if (sinIA > 0) {
      if (bannerCount) bannerCount.textContent = sinIA;
      if (bannerEl)    bannerEl.style.display  = 'flex';
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
