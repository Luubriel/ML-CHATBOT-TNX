#!/usr/bin/env bash
# Inicia o Sistema de Diagnóstico Clínico (PySide6).
# Reaproveita o venv da raiz do projeto.

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PY="$SCRIPT_DIR/../.venv/bin/python"

if [ ! -x "$VENV_PY" ]; then
    echo "❌ venv não encontrado em $VENV_PY"
    echo "   Crie um e instale: pip install -r requirements.txt"
    exit 1
fi

cd "$SCRIPT_DIR"

if [ ! -f "clinica.db" ]; then
    echo "📦 Inicializando banco clinica.db..."
    "$VENV_PY" criar_banco.py
fi

echo "🩺 Iniciando aplicação..."
exec "$VENV_PY" app.py
