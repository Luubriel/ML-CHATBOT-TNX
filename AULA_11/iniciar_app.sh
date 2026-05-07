#!/usr/bin/env bash
# Inicializa o banco (se necessário) e sobe o Streamlit
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/../.venv"

source "$VENV/bin/activate"

echo "🔧 Inicializando banco de dados..."
python3 "$SCRIPT_DIR/setup_db.py"

echo "🚀 Iniciando Streamlit..."
streamlit run "$SCRIPT_DIR/app.py" \
    --server.port 8501 \
    --server.headless false \
    --browser.gatherUsageStats false
