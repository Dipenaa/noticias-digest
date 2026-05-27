/* ── Vista inmersiva (drawer de artículo) ────────────────────────────── */
function abrirArticulo(el) {
  var d       = el.dataset;
  var titulo  = d.titulo    || '';
  var fuente  = d.fuente    || '';
  var fecha   = d.fecha     || '';
  var enlace  = d.enlace    || '#';
  var resumen = d.resumen   || '';
  var critica = d.critica   || '';
  var sesgoF  = d.sesgoFuente || 'desconocido';
  var sesgoIA = d.sesgoIa    || 'desconocido';

  var secEl = el.closest('.seccion');
  var cat   = secEl ? (secEl.querySelector('.seccion-titulo') || {}).textContent || '' : (d.categoria || '');

  var palabras = (titulo + ' ' + resumen).split(/\s+/).filter(Boolean).length;
  var minutos  = Math.max(1, Math.round(palabras / 200));

  document.getElementById('d-categoria').textContent = cat;
  document.getElementById('d-fuente').textContent    = fuente;
  document.getElementById('d-fecha').textContent     = fecha;
  document.getElementById('d-reading').textContent   = minutos + ' min';
  document.getElementById('d-titulo').textContent    = titulo;
  document.getElementById('d-resumen').textContent   = resumen;

  var badgeF = document.getElementById('d-sesgo-f');
  if (badgeF) {
    badgeF.textContent = sesgoF.toUpperCase();
    badgeF.style.background = (window.DIGEST_CONFIG.sesgoColores[sesgoF] || '#9ca3af');
  }
  var badgeIA = document.getElementById('d-sesgo-ia');
  if (badgeIA) {
    badgeIA.textContent = sesgoIA.toUpperCase();
    badgeIA.style.background = (window.DIGEST_CONFIG.sesgoColores[sesgoIA] || '#9ca3af');
  }

  var sentEl = document.getElementById('d-sent');
  if (sentEl) sentEl.textContent = d.sentimiento ? d.sentimiento.toUpperCase() : '';

  var criticaEl = document.getElementById('d-critica');
  if (critica) {
    criticaEl.textContent  = '💡 ' + critica;
    criticaEl.style.display = '';
  } else {
    criticaEl.style.display = 'none';
  }

  document.getElementById('d-btn-leer').href     = enlace;
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

document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') cerrarDrawer();
});
