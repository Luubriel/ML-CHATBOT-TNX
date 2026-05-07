"""
Sistema de Diagnóstico Clínico — Entry Point
============================================

Aplicação desktop em PySide6 que une:
  - Banco SQLite local (clinica.db)
  - Modelo Random Forest treinado na AULA_09 (modelo_risco_clinico.pkl)
  - Interface gráfica com login + 3 telas

Para rodar:
    python criar_banco.py     # 1x para gerar clinica.db
    python app.py
"""

import os
import sys

from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

# Garante imports relativos a esta pasta
BASE = os.path.dirname(os.path.abspath(__file__))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

from ui.style import QSS
from ui.login_window import LoginWindow
from ui.main_window import MainWindow


def garantir_banco() -> bool:
    from paths import DB_PATH
    if os.path.exists(DB_PATH):
        return True
    try:
        import criar_banco
        criar_banco.main()
        return True
    except Exception as e:
        QMessageBox.critical(None, "Erro ao criar banco",
                             f"Falha ao inicializar o banco:\n{e}")
        return False


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Diagnóstico Clínico")
    app.setStyleSheet(QSS)

    if not garantir_banco():
        return 1

    # Loop login → app → logout → login (até o usuário cancelar o login).
    while True:
        login = LoginWindow()
        if login.exec() != QDialog.DialogCode.Accepted or not login.username:
            return 0

        janela = MainWindow(login.username)
        sair = {"logout": False}
        janela.logout_requested.connect(lambda: sair.update(logout=True))
        janela.show()
        app.exec()

        if not sair["logout"]:
            return 0


if __name__ == "__main__":
    sys.exit(main())
