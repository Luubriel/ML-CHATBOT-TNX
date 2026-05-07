"""
Janela principal — sidebar com navegação + QStackedWidget central.
Só é instanciada após login bem-sucedido.
"""

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QListWidget, QListWidgetItem, QMainWindow,
    QMessageBox, QPushButton, QStackedWidget, QStatusBar, QVBoxLayout,
    QWidget,
)

from ui.pages.exames_page import ExamesPage
from ui.pages.pacientes_page import PacientesPage
from ui.pages.predicao_page import PredicaoPage


class MainWindow(QMainWindow):
    logout_requested = Signal()

    def __init__(self, username: str):
        super().__init__()
        self.username = username
        self._fazendo_logout = False
        self.setWindowTitle("Sistema de Diagnóstico Clínico — Biomedicina")
        self.resize(1180, 760)
        self.setMinimumSize(960, 620)
        self._build_ui()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Sidebar (navegação + logout) ──────────────────────────────────
        side = QFrame()
        side.setObjectName("Sidebar")
        side.setFixedWidth(240)
        side_layout = QVBoxLayout(side)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.setSpacing(0)

        self.sidebar = QListWidget()
        self.sidebar.setObjectName("Sidebar")
        for icon, texto in [
            ("👤", "Pacientes"),
            ("🧪", "Tipos de Exame"),
            ("🔬", "Predição IA"),
        ]:
            item = QListWidgetItem(f"  {icon}   {texto}")
            item.setSizeHint(QSize(0, 50))
            self.sidebar.addItem(item)

        side_layout.addWidget(self.sidebar, 1)

        self.btn_logout = QPushButton("🚪  Sair (Logout)")
        self.btn_logout.setObjectName("Danger")
        self.btn_logout.setMinimumHeight(46)
        self.btn_logout.clicked.connect(self._fazer_logout)
        side_layout.addWidget(self.btn_logout)

        layout.addWidget(side)

        # ── Páginas ────────────────────────────────────────────────────────
        self.stack = QStackedWidget()
        self.page_pacientes = PacientesPage()
        self.page_exames = ExamesPage()
        self.page_predicao = PredicaoPage()

        self.stack.addWidget(self.page_pacientes)
        self.stack.addWidget(self.page_exames)
        self.stack.addWidget(self.page_predicao)
        layout.addWidget(self.stack, 1)

        # ── Eventos ────────────────────────────────────────────────────────
        self.sidebar.currentRowChanged.connect(self._on_nav)
        self.sidebar.setCurrentRow(0)

        # Quando um novo paciente é cadastrado, recarrega o combo da predição
        self.page_pacientes.paciente_criado.connect(
            lambda _id: self.page_predicao.recarregar_pacientes()
        )

        # ── Status bar ─────────────────────────────────────────────────────
        sb = QStatusBar()
        sb.showMessage(f"  Logado como: {self.username}  •  Banco: clinica.db")
        self.setStatusBar(sb)

    def _on_nav(self, row: int) -> None:
        self.stack.setCurrentIndex(row)
        # Recarregar dados ao trocar de aba
        if row == 2:
            self.page_predicao.recarregar_pacientes()
            self.page_predicao.recarregar_alertas()
        elif row == 0:
            self.page_pacientes.recarregar()
        elif row == 1:
            self.page_exames.recarregar()

    def _fazer_logout(self) -> None:
        ok = QMessageBox.question(
            self, "Confirmar logout",
            f"Deseja realmente sair, {self.username}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if ok != QMessageBox.Yes:
            return
        self._fazendo_logout = True
        self.logout_requested.emit()
        self.close()
