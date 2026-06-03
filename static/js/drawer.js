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
  var asombro = parseInt(d.asombro || 0);
  var asombroRazon = d.asombroRazon || '';
  var novedad = parseInt(d.novedad || 2);
  var sentimiento = d.sentimiento || 'neutral';

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

  // Sentimiento / Tono editorial
  var sentEl = document.getElementById('d-sent');
  if (sentEl) {
    sentEl.className = 'badge';
    if (sentimiento === 'alarmista') {
      sentEl.textContent = '⚠ ALARMISTA';
      sentEl.style.background = 'rgba(239,68,68,0.14)';
      sentEl.style.color = '#f87171';
      sentEl.style.border = '1px solid rgba(239,68,68,0.25)';
    } else if (sentimiento === 'optimista') {
      sentEl.textContent = '✦ OPTIMISTA';
      sentEl.style.background = 'rgba(45,212,160,0.12)';
      sentEl.style.color = '#4ade80';
      sentEl.style.border = '1px solid rgba(45,212,160,0.22)';
    } else {
      sentEl.textContent = '◉ NEUTRAL';
      sentEl.style.background = 'rgba(240,230,208,0.06)';
      sentEl.style.color = 'var(--txt-3)';
      sentEl.style.border = '1px solid var(--border-sub)';
    }
  }

  // Asombro / Valor de revelación
  var asombroEl = document.getElementById('d-asombro');
  if (asombroEl) {
    if (asombro >= 2 && asombroRazon) {
      var estrellas = '✦'.repeat(asombro) + '✧'.repeat(3 - asombro);
      var nivelTxt = asombro === 3 ? 'Excepcional' : 'Fascinante';
      asombroEl.innerHTML = '<span class="asombro-label">⭐ ' + estrellas + ' (' + nivelTxt + ')</span>' +
                            '<p class="asombro-desc">' + asombroRazon + '</p>';
      asombroEl.style.display = 'block';
    } else {
      asombroEl.style.display = 'none';
    }
  }

  // Novedad / Repetitividad
  var novedadEl = document.getElementById('d-novedad');
  if (novedadEl) {
    if (novedad === 3) {
      novedadEl.innerHTML = '⚡ <strong>SEÑAL:</strong> Aporta información o ángulos nuevos.';
      novedadEl.className = 'drawer-novedad novedad-senal';
      novedadEl.style.display = 'block';
    } else if (novedad <= 1) {
      novedadEl.innerHTML = '⇄ <strong>REPETICIÓN:</strong> Reitera hechos ya reportados en otras fuentes.';
      novedadEl.className = 'drawer-novedad novedad-ruido';
      novedadEl.style.display = 'block';
    } else {
      novedadEl.style.display = 'none';
    }
  }

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
