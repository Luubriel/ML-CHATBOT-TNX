#!/usr/bin/env bash
# Empacota o Sistema de Diagnóstico Clínico com PyInstaller.
#
# Uso:
#   ./build.sh            # one-file (executável único, mais lento p/ abrir)
#   ./build.sh --onedir   # one-dir  (pasta com vários arquivos, mais rápido)
#   ./build.sh --debug    # mantém console p/ ver erros em runtime

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_PY="${VENV_PY:-$SCRIPT_DIR/../.venv/bin/python}"
if [ ! -x "$VENV_PY" ]; then
    echo "❌ Python do venv não encontrado em: $VENV_PY"
    echo "   Defina VENV_PY=/caminho/para/python ou crie o venv."
    exit 1
fi

# Garante PyInstaller instalado
if ! "$VENV_PY" -c "import PyInstaller" 2>/dev/null; then
    echo "📦 Instalando PyInstaller no venv..."
    "$VENV_PY" -m pip install --quiet pyinstaller
fi

NAME="DiagnosticoClinico"
MODE="--onefile"
WINDOWED="--windowed"

for arg in "$@"; do
    case "$arg" in
        --onedir)  MODE="--onedir"  ;;
        --onefile) MODE="--onefile" ;;
        --debug)   WINDOWED="--console" ;;
        *) echo "Argumento desconhecido: $arg"; exit 1 ;;
    esac
done

echo "🔧 Build: $NAME ($MODE $WINDOWED)"
echo "🧹 Limpando builds anteriores..."
rm -rf build dist "${NAME}.spec"

# Separador de --add-data: ':' Linux/macOS, ';' Windows.
SEP=":"
case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*) SEP=";" ;;
esac

"$VENV_PY" -m PyInstaller \
    --noconfirm \
    --clean \
    --name "$NAME" \
    $MODE \
    $WINDOWED \
    --add-data "modelo_risco_clinico.pkl${SEP}." \
    --add-data "pacientes.csv${SEP}." \
    --hidden-import "criar_banco" \
    --hidden-import "bcrypt" \
    --hidden-import "sklearn.tree._utils" \
    --hidden-import "sklearn.utils._heap" \
    --hidden-import "sklearn.utils._sorting" \
    --hidden-import "sklearn.utils._typedefs" \
    --hidden-import "sklearn.utils._weight_vector" \
    --hidden-import "sklearn.neighbors._partition_nodes" \
    --collect-submodules sklearn \
    --collect-data sklearn \
    --collect-data joblib \
    --paths "$SCRIPT_DIR" \
    app.py

echo ""
echo "✅ Build finalizado."
if [ "$MODE" = "--onefile" ]; then
    echo "   Executável: dist/$NAME"
    echo "   Rodar:      ./dist/$NAME"
else
    echo "   Pasta:      dist/$NAME/"
    echo "   Rodar:      ./dist/$NAME/$NAME"
fi
echo ""
echo "ℹ️  O 'clinica.db' será criado ao lado do executável na 1ª execução."
