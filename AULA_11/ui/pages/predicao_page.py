"""
Página: Lançamento de Resultados + Predição de IA.
Carrega o modelo Random Forest da AULA_09 (modelo_risco_clinico.pkl),
executa a predição e exibe risco com cores conforme a classe.
"""

from __future__ import annotations

import os
import pandas as pd
import joblib

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (
    QComboBox, QDoubleSpinBox, QFrame, QHBoxLayout, QHeaderView, QLabel,
    QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget,
)

import db
from paths import MODEL_PATH
from ui.style import RISCO_BAIXO, RISCO_MEDIO, RISCO_ALTO, FG_LABEL

FEATURES = ["idade", "glicose", "pressao_arterial", "imc", "colesterol"]
ROTULO = {0: "Baixo", 1: "Médio", 2: "Alto"}
COR_RISCO = {0: RISCO_BAIXO, 1: RISCO_MEDIO, 2: RISCO_ALTO}


class PredicaoPage(QWidget):
    def __init__(self):
        super().__init__()
        self.modelo = None
        self._load_modelo()
        self._alertas: dict[str, float] = {}
        self._build_ui()
        self.recarregar_pacientes()
        self.recarregar_alertas()

    def _load_modelo(self) -> None:
        if not os.path.exists(MODEL_PATH):
            QMessageBox.critical(
                self, "Modelo não encontrado",
                f"Arquivo de modelo ausente:\n{MODEL_PATH}\n\n"
                "Copie 'modelo_risco_clinico.pkl' da AULA_09 para esta pasta."
            )
            return
        self.modelo = joblib.load(MODEL_PATH)

    # ── UI ────────────────────────────────────────────────────────────────
    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(14)

        titulo = QLabel("🔬 Lançamento de Exames + Predição IA")
        titulo.setObjectName("Title")
        root.addWidget(titulo)

        sub = QLabel("Selecione o paciente, lance os valores e o modelo "
                     "Random Forest indicará o grau de risco.")
        sub.setObjectName("Subtitle")
        root.addWidget(sub)

        # ── Linha 1: paciente + form ───────────────────────────────────────
        form_panel = QFrame()
        form_panel.setObjectName("Panel")
        form = QVBoxLayout(form_panel)
        form.setContentsMargins(16, 16, 16, 16)
        form.setSpacing(10)

        # Paciente
        row_pac = QHBoxLayout()
        row_pac.addWidget(QLabel("Paciente:"))
        self.combo_paciente = QComboBox()
        self.combo_paciente.setMinimumWidth(280)
        row_pac.addWidget(self.combo_paciente, 1)
        self.btn_refresh = QPushButton("↻ Atualizar")
        self.btn_refresh.clicked.connect(self.recarregar_pacientes)
        row_pac.addWidget(self.btn_refresh)
        form.addLayout(row_pac)

        # Campos numéricos
        grid = QHBoxLayout()
        self.input_idade = self._spin(0, 130, 1, decimais=0)
        self.input_glicose = self._spin(40, 500, 1.0, decimais=1)
        self.input_pressao = self._spin(50, 250, 1.0, decimais=1)
        self.input_imc = self._spin(10, 70, 0.1, decimais=2)
        self.input_colesterol = self._spin(80, 500, 1.0, decimais=1)

        for label, w in [
            ("Idade", self.input_idade),
            ("Glicose (mg/dL)", self.input_glicose),
            ("Pressão (mmHg)", self.input_pressao),
            ("IMC (kg/m²)", self.input_imc),
            ("Colesterol (mg/dL)", self.input_colesterol),
        ]:
            col = QVBoxLayout()
            lab = QLabel(label)
            lab.setObjectName("FieldLabel")
            col.addWidget(lab)
            col.addWidget(w)
            grid.addLayout(col)

        form.addLayout(grid)

        # Botão calcular
        actions = QHBoxLayout()
        actions.addStretch()
        self.btn_calc = QPushButton("🔬 Calcular Risco")
        self.btn_calc.clicked.connect(self._calcular)
        actions.addWidget(self.btn_calc)
        form.addLayout(actions)

        root.addWidget(form_panel)

        # ── Resultado ──────────────────────────────────────────────────────
        self.result_panel = QFrame()
        self.result_panel.setObjectName("Panel")
        self.result_panel.setMinimumHeight(110)
        rl = QVBoxLayout(self.result_panel)
        rl.setContentsMargins(20, 16, 20, 16)
        self.lbl_resultado = QLabel("Aguardando lançamento de exame…")
        self.lbl_resultado.setAlignment(Qt.AlignCenter)
        self.lbl_resultado.setStyleSheet(f"font-size:18pt;font-weight:bold;color:{FG_LABEL};")
        rl.addWidget(self.lbl_resultado)
        self.lbl_alertas = QLabel("")
        self.lbl_alertas.setAlignment(Qt.AlignCenter)
        self.lbl_alertas.setObjectName("Subtitle")
        self.lbl_alertas.setWordWrap(True)
        rl.addWidget(self.lbl_alertas)
        root.addWidget(self.result_panel)

        # ── Histórico ──────────────────────────────────────────────────────
        sub_h = QLabel("Histórico de exames do paciente selecionado")
        sub_h.setObjectName("Subtitle")
        root.addWidget(sub_h)

        self.tabela_hist = QTableWidget(0, 7)
        self.tabela_hist.setHorizontalHeaderLabels(
            ["Data", "Glicose", "Pressão", "IMC", "Colesterol", "Risco IA", "Confiança"]
        )
        self.tabela_hist.verticalHeader().setVisible(False)
        self.tabela_hist.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela_hist.setAlternatingRowColors(True)
        h = self.tabela_hist.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for i in range(1, 7):
            h.setSectionResizeMode(i, QHeaderView.Stretch)
        root.addWidget(self.tabela_hist, 1)

        self.combo_paciente.currentIndexChanged.connect(self._on_paciente_change)

    def _spin(self, vmin: float, vmax: float, step: float, decimais: int) -> QDoubleSpinBox:
        sp = QDoubleSpinBox()
        sp.setRange(float(vmin), float(vmax))
        sp.setSingleStep(step)
        sp.setDecimals(decimais)
        return sp

    # ── Reload helpers ────────────────────────────────────────────────────
    def recarregar_pacientes(self) -> None:
        atual = self.combo_paciente.currentData()
        self.combo_paciente.blockSignals(True)
        self.combo_paciente.clear()
        for r in db.listar_pacientes():
            self.combo_paciente.addItem(f"#{r['id']} — {r['nome']} ({r['idade']}a)", r["id"])
        # Reposiciona se possível
        if atual is not None:
            idx = self.combo_paciente.findData(atual)
            if idx >= 0:
                self.combo_paciente.setCurrentIndex(idx)
        self.combo_paciente.blockSignals(False)
        self._on_paciente_change()

    def recarregar_alertas(self) -> None:
        self._alertas = {r["nome"].lower(): r["valor_alerta"] for r in db.listar_tipos_exame()}

    def _on_paciente_change(self) -> None:
        pid = self.combo_paciente.currentData()
        if pid is None:
            self.tabela_hist.setRowCount(0)
            return
        # Auto-preenche idade do paciente, se houver
        with db.conectar() as con:
            row = con.execute("SELECT idade FROM pacientes WHERE id = ?", (pid,)).fetchone()
            if row:
                self.input_idade.setValue(row["idade"])

        rows = db.historico_exames(pid)
        self.tabela_hist.setRowCount(len(rows))
        for i, r in enumerate(rows):
            classe = int(r["resultado_ia"])
            valores = [
                r["data"], f"{r['glicose']:.1f}", f"{r['pressao_arterial']:.1f}",
                f"{r['imc']:.2f}", f"{r['colesterol']:.1f}",
                ROTULO.get(classe, "?"),
                f"{(r['confianca'] or 0)*100:.0f}%",
            ]
            for j, val in enumerate(valores):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                if j == 5:
                    item.setForeground(QBrush(QColor(COR_RISCO.get(classe, "#888888"))))
                self.tabela_hist.setItem(i, j, item)

    # ── Predição ──────────────────────────────────────────────────────────
    def _calcular(self) -> None:
        if self.modelo is None:
            QMessageBox.critical(self, "Modelo indisponível",
                                 "Não foi possível carregar o modelo de IA.")
            return

        pid = self.combo_paciente.currentData()
        if pid is None:
            QMessageBox.warning(self, "Sem paciente",
                                "Cadastre ou selecione um paciente.")
            return

        # Recarrega alertas para refletir mudanças na tela de exames
        self.recarregar_alertas()

        valores = {
            "idade":            int(self.input_idade.value()),
            "glicose":          float(self.input_glicose.value()),
            "pressao_arterial": float(self.input_pressao.value()),
            "imc":              float(self.input_imc.value()),
            "colesterol":       float(self.input_colesterol.value()),
        }

        df = pd.DataFrame([valores], columns=FEATURES)
        pred = int(self.modelo.predict(df)[0])
        proba = self.modelo.predict_proba(df)[0]
        confianca = float(proba[pred])

        rotulo = ROTULO[pred]
        cor = COR_RISCO[pred]
        self.lbl_resultado.setText(f"Risco {rotulo}  ·  {confianca*100:.0f}% de confiança")
        self.lbl_resultado.setStyleSheet(
            f"font-size:20pt;font-weight:bold;color:{cor};"
        )

        # Alertas configurados (tela de Gestão de Exames)
        flags = []
        for nome_alerta, key in [
            ("glicose", "glicose"),
            ("pressão arterial", "pressao_arterial"),
            ("imc", "imc"),
            ("colesterol", "colesterol"),
        ]:
            limite = self._alertas.get(nome_alerta)
            if limite is not None and valores[key] >= limite:
                flags.append(f"⚠️ {nome_alerta.title()} ≥ {limite:g}")
        self.lbl_alertas.setText("  •  ".join(flags) if flags
                                 else "Nenhum exame ultrapassou o limite de alerta configurado.")

        db.registrar_exame(
            id_paciente=pid,
            glicose=valores["glicose"],
            pressao=valores["pressao_arterial"],
            imc=valores["imc"],
            colesterol=valores["colesterol"],
            resultado_ia=pred,
            confianca=confianca,
        )

        self._on_paciente_change()
