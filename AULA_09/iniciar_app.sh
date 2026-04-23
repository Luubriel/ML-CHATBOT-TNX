#!/usr/bin/env bash
# Executa a interface gráfica usando o Python do sistema (que tem tkinter)
# enquanto garante acesso às bibliotecas do venv (joblib, sklearn, pandas).

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_SITE="$SCRIPT_DIR/../.venv/lib/python3.13/site-packages"

echo "🔬 Iniciando Sistema de Predição de Risco Clínico..."
PYTHONPATH="$VENV_SITE" python3 "$SCRIPT_DIR/app_risco_clinico.py"
