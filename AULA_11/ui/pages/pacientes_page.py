"""
Página: Cadastro de Pacientes.
Formulário simples (nome + idade) + tabela com pacientes recentes
e busca por nome.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMessageBox,
    QPushButton, QSpinBox, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget,
)

import db


class PacientesPage(QWidget):
    paciente_criado = Signal(int)

    def __init__(self):
        super().__init__()
        self._build_ui()
        self.recarregar()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(14)

        titulo = QLabel("👤 Cadastro de Pacientes")
        titulo.setObjectName("Title")
        root.addWidget(titulo)

        sub = QLabel("Cadastre novos pacientes e consulte os já registrados.")
        sub.setObjectName("Subtitle")
        root.addWidget(sub)

        # ── Form ───────────────────────────────────────────────────────────
        form_panel = QFrame()
        form_panel.setObjectName("Panel")
        form_layout = QHBoxLayout(form_panel)
        form_layout.setContentsMargins(16, 16, 16, 16)
        form_layout.setSpacing(10)

        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText("Nome completo")

        self.input_idade = QSpinBox()
        self.input_idade.setRange(0, 130)
        self.input_idade.setMaximumWidth(110)

        self.btn_add = QPushButton("➕ Cadastrar")
        self.btn_add.setObjectName("Ok")
        self.btn_add.clicked.connect(self._adicionar)

        form_layout.addWidget(QLabel("Nome:"))
        form_layout.addWidget(self.input_nome, 3)
        form_layout.addWidget(QLabel("Idade:"))
        form_layout.addWidget(self.input_idade, 1)
        form_layout.addWidget(self.btn_add)

        root.addWidget(form_panel)

        # ── Busca ──────────────────────────────────────────────────────────
        busca_row = QHBoxLayout()
        self.input_busca = QLineEdit()
        self.input_busca.setPlaceholderText("🔍 Buscar por nome…")
        self.input_busca.textChanged.connect(self.recarregar)
        busca_row.addWidget(self.input_busca)
        root.addLayout(busca_row)

        # ── Tabela ─────────────────────────────────────────────────────────
        self.tabela = QTableWidget(0, 3)
        self.tabela.setHorizontalHeaderLabels(["ID", "Nome", "Idade"])
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setAlternatingRowColors(True)
        h = self.tabela.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(1, QHeaderView.Stretch)
        h.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        root.addWidget(self.tabela, 1)

    def recarregar(self) -> None:
        rows = db.listar_pacientes(self.input_busca.text().strip())
        self.tabela.setRowCount(len(rows))
        for i, r in enumerate(rows):
            for j, val in enumerate([r["id"], r["nome"], r["idade"]]):
                item = QTableWidgetItem(str(val))
                if j in (0, 2):
                    item.setTextAlignment(Qt.AlignCenter)
                self.tabela.setItem(i, j, item)

    def _adicionar(self) -> None:
        nome = self.input_nome.text().strip()
        idade = self.input_idade.value()
        if not nome:
            QMessageBox.warning(self, "Campo vazio", "Informe o nome do paciente.")
            return
        if idade < 1:
            QMessageBox.warning(self, "Idade inválida", "Informe uma idade válida.")
            return
        novo_id = db.inserir_paciente(nome, idade)
        self.input_nome.clear()
        self.input_idade.setValue(0)
        self.recarregar()
        self.paciente_criado.emit(novo_id)
        QMessageBox.information(self, "Cadastrado",
                                f"Paciente '{nome}' cadastrado (ID {novo_id}).")
