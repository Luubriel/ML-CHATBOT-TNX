"""
Interface Gráfica — Predição de Risco Clínico
Biblioteca: tkinter (padrão Python, sem instalação extra)

Layout:
  - Header fixo no topo
  - Barra de botões SEMPRE visível na base (pack side=bottom antes do body)
  - Corpo (formulário | tabela) ocupa o espaço restante e escala com a janela
"""

import tkinter as tk
from tkinter import ttk, messagebox
import joblib
import os
import subprocess
import sys

# ── Modelo ────────────────────────────────────────────────────────────────────
BASE       = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE, 'modelo_risco_clinico.pkl')

if not os.path.exists(MODEL_PATH):
    subprocess.run([sys.executable, os.path.join(BASE, 'treinar_modelo.py')], check=True)

modelo   = joblib.load(MODEL_PATH)
FEATURES = ['idade', 'glicose', 'pressao_arterial', 'imc', 'colesterol']
ROTULO   = {0: 'Baixo', 1: 'Médio', 2: 'Alto'}
MAX_PAC  = 3

# ── Paleta ────────────────────────────────────────────────────────────────────
BG        = '#1a1a2e'
PANEL     = '#16213e'
ACCENT    = '#0f3460'
ENTRY_BG  = '#0d2044'
ENTRY_FG  = '#ffffff'
FG        = '#e0e0e0'
FG_LABEL  = '#a0aec0'
TITLE_FG  = '#e2e8f0'
BTN_ADD   = '#0d7377'
BTN_CALC  = '#533483'
BTN_CLEAR = '#7a3030'
BTN_BAR   = '#111827'


# ══════════════════════════════════════════════════════════════════════════════
class AppRisco(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Sistema de Predição de Risco Clínico — Biomedicina")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(820, 520)
        self._center(1000, 700)
        self.pacientes: list[dict] = []
        self._build_ui()

    # ── helpers ───────────────────────────────────────────────────────────────
    def _center(self, w, h):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _btn(self, parent, text, bg, cmd, state='normal', **kw):
        return tk.Button(
            parent, text=text, bg=bg, fg='white', font=('Segoe UI', 10, 'bold'),
            activebackground=bg, activeforeground='white',
            relief='flat', bd=0, pady=10, cursor='hand2',
            state=state, command=cmd, **kw
        )

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # 1. HEADER — topo
        hdr = tk.Frame(self, bg=ACCENT, pady=12)
        hdr.pack(side='top', fill='x')
        tk.Label(hdr, text="🏥  Predição de Risco Clínico",
                 font=('Segoe UI', 17, 'bold'), bg=ACCENT, fg=TITLE_FG).pack()
        tk.Label(hdr,
                 text="Modelo: Random Forest Classifier  •  Dataset: pacientes_tratados.csv  •  Acurácia: 89%",
                 font=('Segoe UI', 9), bg=ACCENT, fg=FG_LABEL).pack()

        # 2. BARRA DE BOTÕES — base (deve vir ANTES do body no pack)
        btn_bar = tk.Frame(self, bg=BTN_BAR, pady=10, padx=16)
        btn_bar.pack(side='bottom', fill='x')

        self.btn_calc = self._btn(
            btn_bar, "🔬  Calcular Risco dos Pacientes", BTN_CALC,
            self._calcular_risco, state='disabled'
        )
        self.btn_calc.pack(side='left', fill='x', expand=True, padx=(0, 10))

        self._btn(btn_bar, "🗑  Limpar Tudo", BTN_CLEAR,
                  self._limpar_tudo).pack(side='left', ipadx=16)

        # 3. CORPO — expande entre header e btn_bar
        body = tk.Frame(self, bg=BG)
        body.pack(side='top', fill='both', expand=True, padx=14, pady=12)

        # painel esquerdo: formulário (largura fixa, altura flexível)
        left = tk.Frame(body, bg=PANEL, padx=16, pady=14)
        left.pack(side='left', fill='y', padx=(0, 10))

        # painel direito: tabela (expansível)
        right = tk.Frame(body, bg=PANEL, padx=14, pady=14)
        right.pack(side='left', fill='both', expand=True)

        self._build_form(left)
        self._build_table(right)

    # ── Formulário ────────────────────────────────────────────────────────────
    def _build_form(self, p):
        tk.Label(p, text="Dados do Paciente",
                 font=('Segoe UI', 12, 'bold'), bg=PANEL, fg=TITLE_FG
                 ).pack(anchor='w', pady=(0, 6))

        campos = [
            ("Nome do Paciente",                   "nome_paciente",    str,   None,  None),
            ("Idade (anos)  [18 – 99]",            "idade",            int,   18,    99),
            ("Glicose (mg/dL)  [60 – 300]",        "glicose",          float, 60.0,  300.0),
            ("Pressão Arterial (mmHg)  [80 – 200]","pressao_arterial", float, 80.0,  200.0),
            ("IMC (kg/m²)  [13 – 55]",             "imc",              float, 13.0,  55.0),
            ("Colesterol (mg/dL)  [100 – 400]",    "colesterol",       float, 100.0, 400.0),
        ]
        self.entries: dict[str, tk.StringVar] = {}
        self._campos_meta = {key: (tipo, vmin, vmax)
                             for _, key, tipo, vmin, vmax in campos}

        for label, key, *_ in campos:
            tk.Label(p, text=label, font=('Segoe UI', 8),
                     bg=PANEL, fg=FG_LABEL, anchor='w').pack(fill='x', pady=(5, 1))
            var = tk.StringVar()
            self.entries[key] = var
            tk.Entry(p, textvariable=var,
                     font=('Segoe UI', 11),
                     bg=ENTRY_BG, fg=ENTRY_FG,
                     insertbackground=ENTRY_FG,
                     relief='flat', bd=6, width=28
                     ).pack(fill='x', ipady=5)

        tk.Frame(p, bg=PANEL, height=8).pack()

        self.btn_add = self._btn(p, "➕  Adicionar Paciente", BTN_ADD,
                                 self._adicionar_paciente)
        self.btn_add.pack(fill='x')

        self.lbl_count = tk.Label(p, text=f"Pacientes: 0 / {MAX_PAC}",
                                  font=('Segoe UI', 9), bg=PANEL, fg=FG_LABEL)
        self.lbl_count.pack(pady=(6, 0))

    # ── Tabela ────────────────────────────────────────────────────────────────
    def _build_table(self, p):
        tk.Label(p, text="Pacientes Inseridos",
                 font=('Segoe UI', 12, 'bold'), bg=PANEL, fg=TITLE_FG
                 ).pack(anchor='w', pady=(0, 8))

        cols    = ('nome', 'idade', 'glicose', 'pa', 'imc', 'colesterol', 'risco')
        headers = ('Nome', 'Idade', 'Glicose', 'PA (mmHg)', 'IMC', 'Colesterol', 'Risco')
        widths  = (150, 55, 80, 90, 60, 95, 120)

        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('T.Treeview',
                        background=ENTRY_BG, fieldbackground=ENTRY_BG,
                        foreground=FG, rowheight=34,
                        font=('Segoe UI', 10))
        style.configure('T.Treeview.Heading',
                        background=ACCENT, foreground=TITLE_FG,
                        font=('Segoe UI', 10, 'bold'), relief='flat')
        style.map('T.Treeview', background=[('selected', ACCENT)])

        wrap = tk.Frame(p, bg=PANEL)
        wrap.pack(fill='both', expand=True)

        self.tree = ttk.Treeview(wrap, columns=cols, show='headings',
                                 height=MAX_PAC, style='T.Treeview',
                                 selectmode='none')

        for col, hdr, w in zip(cols, headers, widths):
            self.tree.heading(col, text=hdr)
            self.tree.column(col, width=w, anchor='center',
                             stretch=(col == 'nome'))  # só Nome estica

        self.tree.pack(fill='both', expand=True)

        self.tree.tag_configure('Baixo',    foreground='#2ecc71')
        self.tree.tag_configure('Médio',    foreground='#f39c12')
        self.tree.tag_configure('Alto',     foreground='#e74c3c')
        self.tree.tag_configure('pendente', foreground=FG_LABEL)

    # ══════════════════════════════════════════════════════════════════════════
    #  Lógica
    # ══════════════════════════════════════════════════════════════════════════

    def _adicionar_paciente(self):
        if len(self.pacientes) >= MAX_PAC:
            messagebox.showwarning("Limite atingido",
                                   f"Máximo de {MAX_PAC} pacientes inseridos.\n"
                                   "Use 'Limpar Tudo' para recomeçar.")
            return

        dados, erros = {}, []

        # Nome
        nome = self.entries['nome_paciente'].get().strip()
        if not nome:
            erros.append("• Nome do Paciente é obrigatório.")
        else:
            dados['nome_paciente'] = nome

        # Campos numéricos
        campos_num = [
            ('idade',            'Idade',            int,   18,    99),
            ('glicose',          'Glicose',          float, 60.0,  300.0),
            ('pressao_arterial', 'Pressão Arterial', float, 80.0,  200.0),
            ('imc',              'IMC',              float, 13.0,  55.0),
            ('colesterol',       'Colesterol',       float, 100.0, 400.0),
        ]
        for key, label, tipo, vmin, vmax in campos_num:
            raw = self.entries[key].get().strip().replace(',', '.')
            if not raw:
                erros.append(f"• {label} é obrigatório.")
                continue
            try:
                val = tipo(raw)
            except ValueError:
                erros.append(f"• {label}: '{raw}' não é um número válido.")
                continue
            if not (vmin <= val <= vmax):
                erros.append(f"• {label}: deve estar entre {vmin} e {vmax}.")
                continue
            dados[key] = val

        if erros:
            messagebox.showerror("Dados inválidos", "\n".join(erros))
            return

        # Insere
        self.pacientes.append(dados)
        self.tree.insert('', 'end', iid=str(len(self.pacientes)), values=(
            dados['nome_paciente'],
            dados['idade'],
            f"{dados['glicose']:.1f}",
            f"{dados['pressao_arterial']:.1f}",
            f"{dados['imc']:.1f}",
            f"{dados['colesterol']:.1f}",
            '—'
        ), tags=('pendente',))

        for v in self.entries.values():
            v.set('')

        n = len(self.pacientes)
        self.lbl_count.config(text=f"Pacientes: {n} / {MAX_PAC}")
        if n >= MAX_PAC:
            self.btn_add.config(state='disabled')
            self.btn_calc.config(state='normal')

    def _calcular_risco(self):
        import pandas as pd

        df_in = pd.DataFrame([
            [p['idade'], p['glicose'], p['pressao_arterial'], p['imc'], p['colesterol']]
            for p in self.pacientes
        ], columns=FEATURES)

        preds  = modelo.predict(df_in)
        probas = modelo.predict_proba(df_in)

        for i, (pred, proba) in enumerate(zip(preds, probas)):
            label = ROTULO[pred]
            conf  = proba[pred] * 100
            p     = self.pacientes[i]
            self.tree.item(str(i + 1), values=(
                p['nome_paciente'], p['idade'],
                f"{p['glicose']:.1f}", f"{p['pressao_arterial']:.1f}",
                f"{p['imc']:.1f}", f"{p['colesterol']:.1f}",
                f"{label} ({conf:.0f}%)"
            ), tags=(label,))

        self.btn_calc.config(state='disabled', text="✅  Risco Calculado")

        resumo = "\n".join(
            f"  {self.pacientes[i]['nome_paciente']:20s}  →  "
            f"{ROTULO[preds[i]]:5s}  ({probas[i][preds[i]]*100:.0f}% confiança)"
            for i in range(len(self.pacientes))
        )
        messagebox.showinfo("Resultados da Predição", resumo)

    def _limpar_tudo(self):
        if self.pacientes and not messagebox.askyesno(
            "Confirmar", "Deseja apagar todos os pacientes e recomeçar?"
        ):
            return
        self.pacientes.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for v in self.entries.values():
            v.set('')
        self.btn_add.config(state='normal')
        self.btn_calc.config(state='disabled', text="🔬  Calcular Risco dos Pacientes")
        self.lbl_count.config(text=f"Pacientes: 0 / {MAX_PAC}")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    AppRisco().mainloop()
