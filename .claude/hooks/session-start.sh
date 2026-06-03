#!/bin/bash
set -euo pipefail

# Solo ejecutar en entorno remoto (Claude Code on the web)
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

pip install -q -r "$CLAUDE_PROJECT_DIR/requirements.txt"

# Mostrar contexto de última sesión si existe
CONTEXT_FILE="$CLAUDE_PROJECT_DIR/context/ultima-sesion.md"
if [ -f "$CONTEXT_FILE" ]; then
  echo ""
  echo "=== CONTEXTO DE ÚLTIMA SESIÓN ==="
  cat "$CONTEXT_FILE"
  echo "================================="
fi
