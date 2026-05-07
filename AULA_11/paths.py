"""
Resolução de caminhos compatível com modo desenvolvimento e empacotado
(PyInstaller --onefile / --onedir).

  - BUNDLE_DIR : recursos somente-leitura (modelo .pkl, CSV inicial).
                 Em frozen mode aponta para sys._MEIPASS.
  - USER_DIR   : diretório gravável onde o clinica.db é mantido.
                 Em frozen mode é o diretório do executável (persiste
                 entre execuções do --onefile).
"""

import os
import sys


def _is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


if _is_frozen():
    BUNDLE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    USER_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    BUNDLE_DIR = os.path.dirname(os.path.abspath(__file__))
    USER_DIR = BUNDLE_DIR


DB_PATH = os.path.join(USER_DIR, "clinica.db")
MODEL_PATH = os.path.join(BUNDLE_DIR, "modelo_risco_clinico.pkl")
CSV_PATH = os.path.join(BUNDLE_DIR, "pacientes.csv")
