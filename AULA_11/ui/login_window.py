"""
Tela de Login — QDialog inicial.
Valida usuário/senha contra a tabela 'usuarios' (bcrypt).
Só permite entrar no sistema quando autenticado.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit,
    QMessageBox, QPushButton, QVBoxLayout,
)

import db


class LoginWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login — Sistema de Diagnóstico Clínico")
        self.setModal(True)
        self.setMinimumSize(420, 320)
        self.username: str | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(14)

        title = QLabel("🏥  Diagnóstico Clínico")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Faça login para acessar o sistema")
        subtitle.setObjectName("Subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(10)

        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("Usuário")

        self.input_pass = QLineEdit()
        self.input_pass.setPlaceholderText("Senha")
        self.input_pass.setEchoMode(QLineEdit.Password)

        form = QFormLayout()
        form.setSpacing(10)
        form.addRow("Usuário:", self.input_user)
        form.addRow("Senha:", self.input_pass)
        layout.addLayout(form)

        btns = QHBoxLayout()
        self.btn_entrar = QPushButton("Entrar")
        self.btn_entrar.setObjectName("Ok")
        self.btn_entrar.clicked.connect(self._tentar_login)
        self.btn_entrar.setDefault(True)

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("Danger")
        self.btn_cancelar.clicked.connect(self.reject)

        btns.addWidget(self.btn_cancelar)
        btns.addWidget(self.btn_entrar)
        layout.addLayout(btns)

        hint = QLabel("Usuário padrão: admin / admin123")
        hint.setObjectName("Subtitle")
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)

        self.input_pass.returnPressed.connect(self._tentar_login)
        self.input_user.returnPressed.connect(self.input_pass.setFocus)

    def _tentar_login(self) -> None:
        user = self.input_user.text().strip()
        senha = self.input_pass.text()
        if not user or not senha:
            QMessageBox.warning(self, "Campos vazios",
                                "Informe usuário e senha.")
            return

        if db.autenticar(user, senha):
            self.username = user
            self.accept()
        else:
            QMessageBox.critical(self, "Falha no login",
                                 "Usuário ou senha inválidos.")
            self.input_pass.clear()
            self.input_pass.setFocus()
