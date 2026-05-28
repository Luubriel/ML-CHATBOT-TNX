"""
Tema visual centralizado — paleta inspirada no app Tkinter da AULA_09
adaptada para PySide6 (QSS).
"""

BG = "#1a1a2e"
PANEL = "#16213e"
ACCENT = "#0f3460"
ENTRY_BG = "#0d2044"
FG = "#e0e0e0"
FG_LABEL = "#a0aec0"
TITLE_FG = "#e2e8f0"

BTN_PRIMARY = "#533483"
BTN_OK = "#0d7377"
BTN_DANGER = "#7a3030"

RISCO_BAIXO = "#2ecc71"
RISCO_MEDIO = "#f39c12"
RISCO_ALTO = "#e74c3c"

QSS = f"""
QWidget {{
    background-color: {BG};
    color: {FG};
    font-family: "Segoe UI", "Inter", Arial, sans-serif;
    font-size: 11pt;
}}

QFrame#Panel {{
    background-color: {PANEL};
    border-radius: 10px;
}}

QLabel#Title {{
    color: {TITLE_FG};
    font-size: 18pt;
    font-weight: bold;
}}

QLabel#Subtitle {{
    color: {FG_LABEL};
    font-size: 9pt;
}}

QLabel#FieldLabel {{
    color: {FG_LABEL};
    font-size: 9pt;
}}

QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background-color: {ENTRY_BG};
    color: {FG};
    border: 1px solid {ACCENT};
    border-radius: 6px;
    padding: 6px 10px;
    selection-background-color: {ACCENT};
}}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
    border: 1px solid {BTN_PRIMARY};
}}

QPushButton {{
    background-color: {BTN_PRIMARY};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 9px 16px;
    font-weight: bold;
}}

QPushButton:hover  {{ background-color: #6a44a8; }}
QPushButton:pressed{{ background-color: #432972; }}
QPushButton:disabled{{ background-color: #2a2a3e; color: #6c6c80; }}

QPushButton#Ok     {{ background-color: {BTN_OK}; }}
QPushButton#Ok:hover{{ background-color: #119a9f; }}

QPushButton#Danger {{ background-color: {BTN_DANGER}; }}
QPushButton#Danger:hover{{ background-color: #a04040; }}

QFrame#Sidebar {{
    background-color: {ACCENT};
    border: none;
}}

QListWidget#Sidebar {{
    background-color: {ACCENT};
    color: {FG};
    border: none;
    padding: 8px 0;
    font-size: 11pt;
}}

QListWidget#Sidebar::item {{
    padding: 14px 18px;
    border-left: 3px solid transparent;
}}

QListWidget#Sidebar::item:selected {{
    background-color: {PANEL};
    border-left: 3px solid {BTN_PRIMARY};
    color: white;
}}

QFrame#Sidebar > QPushButton#Danger {{
    border-radius: 0;
    margin: 0;
    padding: 12px;
    font-weight: bold;
}}

QTableWidget, QTableView {{
    background-color: {ENTRY_BG};
    alternate-background-color: #102348;
    gridline-color: {ACCENT};
    border: 1px solid {ACCENT};
    border-radius: 6px;
}}

QHeaderView::section {{
    background-color: {ACCENT};
    color: {TITLE_FG};
    padding: 8px;
    border: none;
    font-weight: bold;
}}

QStatusBar {{
    background-color: {ACCENT};
    color: {FG_LABEL};
}}

QTextEdit#ChatArea {{
    background-color: {ENTRY_BG};
    border: 1px solid {ACCENT};
    border-radius: 10px;
    padding: 12px;
    font-size: 11pt;
}}

QPushButton#Chip {{
    background-color: {ACCENT};
    color: {FG};
    border: 1px solid {BTN_PRIMARY};
    border-radius: 14px;
    padding: 5px 12px;
    font-weight: normal;
    font-size: 9pt;
}}
QPushButton#Chip:hover {{
    background-color: {BTN_PRIMARY};
    color: white;
}}
"""
