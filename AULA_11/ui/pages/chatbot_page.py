"""
Página: BiomedBot — chatbot inteligente da clínica.
Integra a API do Google Gemini ao sistema de Diagnóstico Clínico.

Características:
  - Conversa multi-turno (memória de contexto via chat.history do SDK).
  - "Anexar paciente": injeta automaticamente um resumo do paciente
    selecionado (último exame + histórico) como contexto antes da
    próxima pergunta — torna o bot capaz de comentar resultados reais.
  - Sugestões rápidas (botões pré-prontos) para guiar o usuário.
  - Worker thread para não travar a UI durante a chamada à API.
  - Tratamento de erros amigável (chave ausente, falha de rede etc.).
"""

from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
    QPushButton, QTextEdit, QVBoxLayout, QWidget,
)

import db
from gemini_client import criar_modelo

ROTULO_RISCO = {0: "Baixo", 1: "Médio", 2: "Alto"}

SUGESTOES = [
    "O que significa risco alto no meu exame?",
    "Como interpretar o resultado de glicose?",
    "Quais hábitos ajudam a reduzir o colesterol?",
    "Resuma o paciente selecionado",
    "Como o sistema calcula o risco?",
]


class WorkerGemini(QThread):
    """Thread que faz a chamada bloqueante ao Gemini sem travar a UI."""
    resposta = Signal(str)
    erro = Signal(str)

    def __init__(self, chat, prompt: str):
        super().__init__()
        self.chat = chat
        self.prompt = prompt

    def run(self) -> None:
        try:
            resp = self.chat.send_message(self.prompt)
            texto = (resp.text or "").strip()
            if not texto:
                texto = "(O modelo não retornou conteúdo. Tente reformular.)"
            self.resposta.emit(texto)
        except Exception as e:
            self.erro.emit(str(e))


class ChatbotPage(QWidget):
    def __init__(self):
        super().__init__()
        self.modelo = None
        self.chat = None
        self.worker: WorkerGemini | None = None
        self._erro_init: str | None = None

        try:
            self.modelo = criar_modelo()
            self.chat = self.modelo.start_chat(history=[])
        except Exception as e:
            self._erro_init = str(e)

        self._build_ui()
        self.recarregar_pacientes()
        self._mensagem_boas_vindas()

    # ── UI ────────────────────────────────────────────────────────────────
    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(12)

        titulo = QLabel("🤖 BiomedBot — Assistente da Clínica")
        titulo.setObjectName("Title")
        root.addWidget(titulo)

        sub = QLabel(
            "Tire dúvidas sobre exames, prevenção e o próprio sistema. "
            "Anexe um paciente para que o bot comente os resultados dele."
        )
        sub.setObjectName("Subtitle")
        sub.setWordWrap(True)
        root.addWidget(sub)

        # ── Linha de contexto (paciente) ──────────────────────────────────
        ctx_panel = QFrame()
        ctx_panel.setObjectName("Panel")
        ctx = QHBoxLayout(ctx_panel)
        ctx.setContentsMargins(14, 10, 14, 10)
        ctx.setSpacing(8)

        ctx.addWidget(QLabel("Paciente:"))
        self.combo_paciente = QComboBox()
        self.combo_paciente.setMinimumWidth(260)
        self.combo_paciente.addItem("— Nenhum (consulta geral) —", None)
        ctx.addWidget(self.combo_paciente, 1)

        self.btn_anexar = QPushButton("📎 Anexar paciente")
        self.btn_anexar.setObjectName("Ok")
        self.btn_anexar.clicked.connect(self._anexar_paciente)
        ctx.addWidget(self.btn_anexar)

        self.btn_recarregar = QPushButton("↻")
        self.btn_recarregar.setToolTip("Atualizar lista de pacientes")
        self.btn_recarregar.clicked.connect(self.recarregar_pacientes)
        ctx.addWidget(self.btn_recarregar)

        root.addWidget(ctx_panel)

        # ── Área de conversa ──────────────────────────────────────────────
        self.area_chat = QTextEdit()
        self.area_chat.setObjectName("ChatArea")
        self.area_chat.setReadOnly(True)
        root.addWidget(self.area_chat, 1)

        # ── Sugestões rápidas ─────────────────────────────────────────────
        sug_panel = QFrame()
        sug_panel.setObjectName("Panel")
        sug = QHBoxLayout(sug_panel)
        sug.setContentsMargins(10, 8, 10, 8)
        sug.setSpacing(6)
        sug.addWidget(QLabel("Sugestões:"))
        for texto in SUGESTOES:
            btn = QPushButton(texto)
            btn.setObjectName("Chip")
            btn.clicked.connect(lambda _=False, t=texto: self._usar_sugestao(t))
            sug.addWidget(btn)
        sug.addStretch()
        root.addWidget(sug_panel)

        # ── Linha de entrada ──────────────────────────────────────────────
        entrada_row = QHBoxLayout()
        self.input_msg = QLineEdit()
        self.input_msg.setPlaceholderText("Digite sua dúvida e pressione Enter…")
        self.input_msg.returnPressed.connect(self._enviar)
        entrada_row.addWidget(self.input_msg, 1)

        self.btn_enviar = QPushButton("Enviar  ➤")
        self.btn_enviar.clicked.connect(self._enviar)
        entrada_row.addWidget(self.btn_enviar)

        self.btn_limpar = QPushButton("🗑️ Limpar")
        self.btn_limpar.setObjectName("Danger")
        self.btn_limpar.clicked.connect(self._limpar_conversa)
        entrada_row.addWidget(self.btn_limpar)

        root.addLayout(entrada_row)

        # Se houve falha em carregar a API, desabilita o envio
        if self._erro_init:
            self.input_msg.setEnabled(False)
            self.btn_enviar.setEnabled(False)
            self.btn_anexar.setEnabled(False)

    # ── Helpers de UI ─────────────────────────────────────────────────────
    def _anexar_bloco(self, autor: str, texto: str, cor: str) -> None:
        hora = datetime.now().strftime("%H:%M")
        html = (
            f'<div style="margin:6px 0;">'
            f'<span style="color:{cor};font-weight:bold;">{autor}</span> '
            f'<span style="color:#7a8aa8;font-size:9pt;">· {hora}</span>'
            f'<div style="margin-top:2px;">{self._html_escape(texto)}</div>'
            f'</div>'
        )
        self.area_chat.append(html)
        self.area_chat.moveCursor(QTextCursor.End)

    @staticmethod
    def _html_escape(texto: str) -> str:
        return (
            texto.replace("&", "&amp;")
                 .replace("<", "&lt;")
                 .replace(">", "&gt;")
                 .replace("\n", "<br>")
        )

    def _mensagem_boas_vindas(self) -> None:
        if self._erro_init:
            self._anexar_bloco(
                "Sistema",
                "⚠️ Não foi possível inicializar o chatbot:\n"
                f"{self._erro_init}\n\n"
                "Verifique se o arquivo .env contém a chave GEMINI_API_KEY "
                "e se há conexão com a internet.",
                "#e74c3c",
            )
            return
        self._anexar_bloco(
            "BiomedBot 🤖",
            "Olá! Sou o assistente virtual da sua clínica de Biomedicina.\n"
            "Posso esclarecer dúvidas sobre exames, prevenção e até comentar "
            "resultados de um paciente específico — basta selecioná-lo acima "
            "e clicar em \"Anexar paciente\". Como posso ajudar hoje?",
            "#2ecc71",
        )

    # ── Pacientes ─────────────────────────────────────────────────────────
    def recarregar_pacientes(self) -> None:
        atual = self.combo_paciente.currentData()
        self.combo_paciente.blockSignals(True)
        self.combo_paciente.clear()
        self.combo_paciente.addItem("— Nenhum (consulta geral) —", None)
        for r in db.listar_pacientes():
            self.combo_paciente.addItem(
                f"#{r['id']} — {r['nome']} ({r['idade']}a)", r["id"]
            )
        if atual is not None:
            idx = self.combo_paciente.findData(atual)
            if idx >= 0:
                self.combo_paciente.setCurrentIndex(idx)
        self.combo_paciente.blockSignals(False)

    def _resumo_paciente(self, pid: int) -> str | None:
        with db.conectar() as con:
            pac = con.execute(
                "SELECT id, nome, idade FROM pacientes WHERE id = ?", (pid,)
            ).fetchone()
        if not pac:
            return None
        historico = db.historico_exames(pid)
        linhas = [
            f"Paciente #{pac['id']} — {pac['nome']}, {pac['idade']} anos.",
        ]
        if not historico:
            linhas.append("Sem exames registrados ainda.")
        else:
            ultimo = historico[0]
            linhas.append(
                f"Último exame ({ultimo['data']}): "
                f"glicose {ultimo['glicose']:.1f} mg/dL, "
                f"pressão {ultimo['pressao_arterial']:.1f} mmHg, "
                f"IMC {ultimo['imc']:.2f}, "
                f"colesterol {ultimo['colesterol']:.1f} mg/dL. "
                f"Predição IA: risco "
                f"{ROTULO_RISCO.get(int(ultimo['resultado_ia']), '?')} "
                f"({(ultimo['confianca'] or 0)*100:.0f}% de confiança)."
            )
            if len(historico) > 1:
                linhas.append(f"Histórico: {len(historico)} exames registrados.")
        return "\n".join(linhas)

    def _anexar_paciente(self) -> None:
        pid = self.combo_paciente.currentData()
        if pid is None:
            QMessageBox.information(
                self, "Sem paciente",
                "Selecione um paciente na lista acima para anexar."
            )
            return
        resumo = self._resumo_paciente(int(pid))
        if not resumo:
            QMessageBox.warning(self, "Paciente não encontrado", "")
            return

        prompt = (
            "[CONTEXTO_PACIENTE]\n" + resumo +
            "\n\nUse essas informações como contexto. Faça um breve "
            "comentário inicial sobre o paciente e fique pronto para "
            "responder dúvidas específicas sobre ele."
        )
        self._anexar_bloco("Sistema", f"📎 Contexto anexado:\n{resumo}", "#a0aec0")
        self._chamar_modelo(prompt, esconder_usuario=True)

    # ── Envio ─────────────────────────────────────────────────────────────
    def _usar_sugestao(self, texto: str) -> None:
        self.input_msg.setText(texto)
        self._enviar()

    def _enviar(self) -> None:
        texto = self.input_msg.text().strip()
        if not texto:
            return
        self.input_msg.clear()
        self._anexar_bloco("Você", texto, "#9b6dff")
        self._chamar_modelo(texto)

    def _chamar_modelo(self, prompt: str, esconder_usuario: bool = False) -> None:
        if self.chat is None:
            return
        # Bloqueia a UI durante a chamada
        self.input_msg.setEnabled(False)
        self.btn_enviar.setEnabled(False)
        self.btn_anexar.setEnabled(False)
        self._anexar_bloco("BiomedBot 🤖", "⏳ pensando…", "#2ecc71")

        self.worker = WorkerGemini(self.chat, prompt)
        self.worker.resposta.connect(self._on_resposta)
        self.worker.erro.connect(self._on_erro)
        self.worker.finished.connect(self._reabilitar)
        self.worker.start()

    def _remover_ultimo_placeholder(self) -> None:
        """Remove o último bloco '⏳ pensando…' inserido."""
        texto = self.area_chat.toHtml()
        # Estratégia simples: localizar a última ocorrência do placeholder.
        marcador = "⏳ pensando…"
        idx = texto.rfind(marcador)
        if idx == -1:
            return
        # Encontra o início do <div> que contém o placeholder.
        ini_div = texto.rfind('<div style="margin:6px 0;"', 0, idx)
        fim_div = texto.find('</div></div>', idx)
        if ini_div == -1 or fim_div == -1:
            return
        novo = texto[:ini_div] + texto[fim_div + len('</div></div>'):]
        self.area_chat.setHtml(novo)
        self.area_chat.moveCursor(QTextCursor.End)

    def _on_resposta(self, texto: str) -> None:
        self._remover_ultimo_placeholder()
        self._anexar_bloco("BiomedBot 🤖", texto, "#2ecc71")

    def _on_erro(self, msg: str) -> None:
        self._remover_ultimo_placeholder()
        self._anexar_bloco(
            "BiomedBot 🤖",
            f"❌ Erro ao consultar a IA: {msg}",
            "#e74c3c",
        )

    def _reabilitar(self) -> None:
        self.input_msg.setEnabled(True)
        self.btn_enviar.setEnabled(True)
        self.btn_anexar.setEnabled(True)
        self.input_msg.setFocus()

    # ── Limpeza ───────────────────────────────────────────────────────────
    def _limpar_conversa(self) -> None:
        if self.modelo is not None:
            self.chat = self.modelo.start_chat(history=[])
        self.area_chat.clear()
        self._mensagem_boas_vindas()
