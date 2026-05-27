"""Pestaña Estadísticas — distribución de sesgos y cobertura (calculada por JS)."""

TAB_ID    = "estadisticas"
TAB_LABEL = "Estadísticas"
TAB_ICON  = "📊"


def render(fuentes_fallidas: list[str] | None = None, **_) -> str:
    bloque_fallidas = ""
    if fuentes_fallidas:
        items = "".join(f"<li>{n}</li>" for n in fuentes_fallidas)
        bloque_fallidas = f"""
<div class="stats-fallidas">
  <strong>⚠ Fuentes sin artículos en esta generación ({len(fuentes_fallidas)})</strong>
  <ul>{items}</ul>
  <span>Puede ser una caída temporal del feed o URL incorrecta.</span>
</div>"""

    return f"""
<div class="stats-header">
  <h2>Estadísticas del digest</h2>
  <p>Distribución ideológica, cobertura por fuente y diversidad — calculado en tiempo real</p>
</div>
{bloque_fallidas}
<div class="stats-kpi-row">
  <div class="stat-kpi">
    <div class="stat-kpi-valor" id="kpi-total">—</div>
    <div class="stat-kpi-label">artículos totales</div>
  </div>
  <div class="stat-kpi">
    <div class="stat-kpi-valor" id="kpi-fuentes">—</div>
    <div class="stat-kpi-label">fuentes distintas</div>
  </div>
  <div class="stat-kpi">
    <div class="stat-kpi-valor" id="kpi-diversidad">—</div>
    <div class="stat-kpi-label">diversidad ideológica</div>
  </div>
  <div class="stat-kpi">
    <div class="stat-kpi-valor" id="kpi-sesgos">—</div>
    <div class="stat-kpi-label">sesgos detectados</div>
  </div>
</div>
<div class="stats-grid">
  <div class="stat-card">
    <div class="stat-card-title">Sesgo por fuente (siempre disponible)</div>
    <div id="stat-sesgo-chart"><span style="color:var(--txt-3);font-size:.8rem">Calculando…</span></div>
  </div>
  <div class="stat-card">
    <div class="stat-card-title">Sesgo según análisis IA</div>
    <div id="stat-sesgo-ia-chart"><span style="color:var(--txt-3);font-size:.8rem">Calculando…</span></div>
  </div>
  <div class="stat-card">
    <div class="stat-card-title">Top fuentes por volumen</div>
    <div id="stat-fuentes-chart"><span style="color:var(--txt-3);font-size:.8rem">Calculando…</span></div>
  </div>
  <div class="stat-card">
    <div class="stat-card-title">Artículos por categoría</div>
    <div id="stat-cat-chart"><span style="color:var(--txt-3);font-size:.8rem">Calculando…</span></div>
  </div>
</div>"""
