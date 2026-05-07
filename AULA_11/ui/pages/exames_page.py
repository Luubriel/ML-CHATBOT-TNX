"""
Página: Gestão de Tipos de Exame.
Permite cadastrar novos tipos e definir os valores de alerta usados
no destaque visual da tela de predição.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDoubleSpinBox, QFrame, QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget,
)

import db


class ExamesPage(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self.recarregar()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(14)

        titulo = QLabel("🧪 Gestão de Tipos de Exame")
        titulo.setObjectName("Title")
        root.addWidget(titulo)

        subtitle = QLabel("Cadastre tipos de exame e defina os valores de alerta.")
        subtitle.setObjectName("Subtitle")
        root.addWidget(subtitle)

        # ── Form de cadastro ───────────────────────────────────────────────
        form_panel = QFrame()
        form_panel.setObjectName("Panel")
        form_layout = QHBoxLayout(form_panel)
        form_layout.setContentsMargins(16, 16, 16, 16)
        form_layout.setSpacing(10)

        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText("Nome do exame")

        self.input_unidade = QLineEdit()
        self.input_unidade.setPlaceholderText("Unidade (ex: mg/dL)")
        self.input_unidade.setMaximumWidth(140)

        self.input_alerta = QDoubleSpinBox()
        self.input_alerta.setRange(0.0, 100000.0)
        self.input_alerta.setDecimals(2)
        self.input_alerta.setSingleStep(1.0)
        self.input_alerta.setMaximumWidth(140)

        self.btn_add = QPushButton("➕ Adicionar")
        self.btn_add.setObjectName("Ok")
        self.btn_add.clicked.connect(self._adicionar)

        form_layout.addWidget(QLabel("Nome:"))
        form_layout.addWidget(self.input_nome, 2)
        form_layout.addWidget(QLabel("Unidade:"))
        form_layout.addWidget(self.input_unidade, 1)
        form_layout.addWidget(QLabel("Alerta a partir de:"))
        form_layout.addWidget(self.input_alerta, 1)
        form_layout.addWidget(self.btn_add)

        root.addWidget(form_panel)

        # ── Tabela ─────────────────────────────────────────────────────────
        self.tabela = QTableWidget(0, 4)
        self.tabela.setHorizontalHeaderLabels(["ID", "Nome", "Unidade", "Valor de Alerta"])
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setAlternatingRowColors(True)
        h = self.tabela.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(1, QHeaderView.Stretch)
        h.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        root.addWidget(self.tabela, 1)

        # ── Ações ──────────────────────────────────────────────────────────
        actions = QHBoxLayout()
        self.btn_atualizar = QPushButton("✏️ Atualizar Alerta da Linha")
        self.btn_atualizar.clicked.connect(self._atualizar)

        self.btn_excluir = QPushButton("🗑 Excluir")
        self.btn_excluir.setObjectName("Danger")
        self.btn_excluir.clicked.connect(self._excluir)

        actions.addStretch()
        actions.addWidget(self.btn_atualizar)
        actions.addWidget(self.btn_excluir)
        root.addLayout(actions)

    # ── Lógica ────────────────────────────────────────────────────────────
    def recarregar(self) -> None:
        rows = db.listar_tipos_exame()
        self.tabela.setRowCount(len(rows))
        for i, r in enumerate(rows):
            for j, val in enumerate([r["id"], r["nome"], r["unidade"] or "", f"{r['valor_alerta']:.2f}"]):
                item = QTableWidgetItem(str(val))
                if j in (0, 3):
                    item.setTextAlignment(Qt.AlignCenter)
                self.tabela.setItem(i, j, item)

    def _adicionar(self) -> None:
        nome = self.input_nome.text().strip()
        unidade = self.input_unidade.text().strip()
        alerta = self.input_alerta.value()

        if not nome:
            QMessageBox.warning(self, "Campo vazio", "Informe o nome do exame.")
            return
        if alerta <= 0:
            QMessageBox.warning(self, "Valor inválido",
                                "Informe um valor de alerta maior que zero.")
            return

        if db.inserir_tipo_exame(nome, unidade, alerta):
            self.input_nome.clear()
            self.input_unidade.clear()
            self.input_alerta.setValue(0.0)
            self.recarregar()
        else:
            QMessageBox.warning(self, "Duplicado",
                                f"Já existe um tipo de exame com o nome '{nome}'.")

    def _id_selecionado(self) -> int | None:
        row = self.tabela.currentRow()
        if row < 0:
            return None
        return int(self.tabela.item(row, 0).text())

    def _atualizar(self) -> None:
        id_tipo = self._id_selecionado()
        if id_tipo is None:
            QMessageBox.information(self, "Selecione",
                                    "Selecione uma linha da tabela.")
            return
        valor = self.input_alerta.value()
        if valor <= 0:
            QMessageBox.warning(self, "Valor inválido",
                                "Informe um novo valor de alerta no campo acima.")
            return
        db.atualizar_tipo_exame(id_tipo, valor)
        self.recarregar()

    def _excluir(self) -> None:
        id_tipo = self._id_selecionado()
        if id_tipo is None:
            QMessageBox.information(self, "Selecione",
                                    "Selecione uma linha da tabela.")
            return
        ok = QMessageBox.question(self, "Confirmar",
                                  "Excluir o tipo de exame selecionado?")
        if ok == QMessageBox.Yes:
            db.excluir_tipo_exame(id_tipo)
            self.recarregar()
