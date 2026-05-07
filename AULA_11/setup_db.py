"""
setup_db.py — Cria o banco clinica.db e importa pacientes_tratados.csv
Referência: roteiro_final_ML-BIO.pdf – Passo 1 (Persistência)

Tabelas:
  usuarios  → login do sistema
  pacientes → cadastro básico (nome, idade)
  exames    → resultados clínicos + predição da IA
"""

import sqlite3
import pandas as pd
import bcrypt
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DB   = os.path.join(BASE, 'clinica.db')
CSV  = os.path.join(BASE, '..', 'AULA_09', 'pacientes_tratados.csv')

conn = sqlite3.connect(DB)
cur  = conn.cursor()

# ── Tabelas ───────────────────────────────────────────────────────────────────
cur.executescript("""
CREATE TABLE IF NOT EXISTS usuarios (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario  TEXT    UNIQUE NOT NULL,
    senha    TEXT    NOT NULL,
    perfil   TEXT    DEFAULT 'medico'
);

CREATE TABLE IF NOT EXISTS pacientes (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    nome  TEXT    NOT NULL,
    idade INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS exames (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    id_paciente  INTEGER NOT NULL,
    glicose      REAL    NOT NULL,
    pressao      REAL    NOT NULL,
    imc          REAL    NOT NULL,
    colesterol   REAL    NOT NULL,
    resultado_ia TEXT,
    confianca    REAL,
    data_exame   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_paciente) REFERENCES pacientes(id)
);

CREATE TABLE IF NOT EXISTS tipos_exame (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    nome         TEXT    NOT NULL,
    alerta_min   REAL,
    alerta_max   REAL,
    unidade      TEXT
);
""")

# ── Usuário padrão (admin / admin123) ─────────────────────────────────────────
senha_hash = bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode()
cur.execute("""
    INSERT OR IGNORE INTO usuarios (usuario, senha, perfil)
    VALUES (?, ?, 'admin')
""", ('admin', senha_hash))

# ── Tipos de exame padrão ─────────────────────────────────────────────────────
tipos = [
    ('Glicose',          126.0, 300.0, 'mg/dL'),
    ('Pressão Arterial',  140.0, 200.0, 'mmHg'),
    ('IMC',               30.0,  55.0, 'kg/m²'),
    ('Colesterol',        240.0, 400.0, 'mg/dL'),
]
cur.executemany("""
    INSERT OR IGNORE INTO tipos_exame (nome, alerta_min, alerta_max, unidade)
    VALUES (?, ?, ?, ?)
""", tipos)

# ── Importa CSV de pacientes (se existir) ─────────────────────────────────────
if os.path.exists(CSV):
    df = pd.read_csv(CSV)
    importados = 0
    for _, row in df.iterrows():
        cur.execute("INSERT INTO pacientes (nome, idade) VALUES (?, ?)",
                    (row['nome_paciente'], int(row['idade'])))
        pid = cur.lastrowid
        cur.execute("""
            INSERT INTO exames
                (id_paciente, glicose, pressao, imc, colesterol, resultado_ia)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            pid,
            float(row['glicose']),
            float(row['pressao_arterial']),
            float(row['imc']),
            float(row['colesterol']),
            ['Baixo', 'Médio', 'Alto'][int(row['classificacao_risco'])]
        ))
        importados += 1
    print(f"✅ {importados} pacientes importados do CSV.")
else:
    print(f"⚠️  CSV não encontrado em {CSV} — banco criado sem dados iniciais.")

conn.commit()
conn.close()
print(f"✅ Banco '{DB}' pronto.")
