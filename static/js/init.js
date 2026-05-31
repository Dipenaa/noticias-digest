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
