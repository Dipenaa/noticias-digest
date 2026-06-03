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
  document.getElementById('d-reading').textContent   = minutos;
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

  // Ficha de Análisis Editorial IA
  var descripcionesSesgo = {
    'izquierda': 'Enfoque progresista centrado en desigualdad, derechos sociales y crítica al conservadurismo o al libre mercado.',
    'centro-izquierda': 'Perspectiva reformista moderada, favorable a políticas de progreso gradual y defensa de instituciones.',
    'centro': 'Enfoque principalmente descriptivo, neutral u objetivo. Presenta múltiples puntos de vista sin jerarquías valorativas.',
    'centro-derecha': 'Perspectiva de centro-derecha que enfatiza el orden social, la libre iniciativa y eficiencia económica.',
    'derecha': 'Enfoque conservador centrado en soberanía, valores tradicionales, orden y crítica al intervencionismo o progresismo.',
    'desconocido': 'Sesgo no detectable o neutro por falta de marcadores ideológicos claros en la redacción.'
  };

  var nombresSesgo = {
    'izquierda': 'Izquierda',
    'centro-izquierda': 'Centro-Izquierda',
    'centro': 'Centro (Neutral)',
    'centro-derecha': 'Centro-Derecha',
    'derecha': 'Derecha',
    'desconocido': 'Desconocido'
  };

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
    var sesgoIa = (sesgoIA || 'desconocido').toLowerCase();
    var sent = (d.sentimiento || '').toLowerCase();
    var nov = d.novedad || '2';

    if (sesgoIa !== 'desconocido' || sent || nov !== '2' || critica) {
      panelIA.style.display = 'flex';

      var valSesgo = document.getElementById('d-val-sesgo');
      if (valSesgo) valSesgo.textContent = nombresSesgo[sesgoIa] || sesgoIa.toUpperCase();

      var descSesgo = document.getElementById('d-desc-sesgo');
      if (descSesgo) descSesgo.textContent = descripcionesSesgo[sesgoIa] || '';

      document.querySelectorAll('#d-escala-sesgo .escala-item').forEach(function(item) {
        var sesgoKey = item.getAttribute('data-sesgo');
        var color = window.DIGEST_CONFIG.sesgoColores[sesgoKey] || '#9ca3af';
        item.style.setProperty('--color-sesgo', color);
        if (sesgoKey === sesgoIa) {
          item.classList.add('selected');
        } else {
          item.classList.remove('selected');
        }
      });

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
