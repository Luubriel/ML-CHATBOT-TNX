"""
Cria o banco SQLite 'clinica.db' do Sistema de Diagnóstico Clínico.

Tabelas:
  - usuarios     : login do médico (username + bcrypt hash)
  - pacientes    : cadastro vindo do CSV da AULA_09 + novos cadastros
  - tipos_exame  : tipos de exames com valor de alerta configurável
  - exames       : histórico de lançamentos com resultado da IA

Uso:
    python criar_banco.py
"""

import os
import sqlite3
import bcrypt
import pandas as pd

from paths import DB_PATH, CSV_PATH


def hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def criar_tabelas(con: sqlite3.Connection) -> None:
    cur = con.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            criado_em     TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS pacientes (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            nome                TEXT NOT NULL,
            idade               INTEGER NOT NULL,
            glicose             REAL,
            pressao_arterial    REAL,
            imc                 REAL,
            colesterol          REAL,
            classificacao_risco INTEGER,
            criado_em           TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS tipos_exame (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            nome          TEXT NOT NULL UNIQUE,
            unidade       TEXT,
            valor_alerta  REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS exames (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            id_paciente         INTEGER NOT NULL,
            glicose             REAL NOT NULL,
            pressao_arterial    REAL NOT NULL,
            imc                 REAL NOT NULL,
            colesterol          REAL NOT NULL,
            resultado_ia        INTEGER NOT NULL,
            confianca           REAL,
            data                TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (id_paciente) REFERENCES pacientes(id) ON DELETE CASCADE
        );
        """
    )
    con.commit()


def seed_usuario_default(con: sqlite3.Connection) -> None:
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM usuarios")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO usuarios (username, password_hash) VALUES (?, ?)",
            ("admin", hash_senha("admin123")),
        )
        con.commit()
        print("✅ Usuário default criado: admin / admin123")


def seed_tipos_exame(con: sqlite3.Connection) -> None:
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM tipos_exame")
    if cur.fetchone()[0] > 0:
        return
    tipos = [
        ("Glicose",          "mg/dL", 126.0),
        ("Pressão Arterial", "mmHg",  140.0),
        ("IMC",              "kg/m²", 30.0),
        ("Colesterol",       "mg/dL", 240.0),
    ]
    cur.executemany(
        "INSERT INTO tipos_exame (nome, unidade, valor_alerta) VALUES (?, ?, ?)",
        tipos,
    )
    con.commit()
    print(f"✅ {len(tipos)} tipos de exame pré-cadastrados")


def importar_csv(con: sqlite3.Connection) -> None:
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM pacientes")
    if cur.fetchone()[0] > 0:
        print("ℹ️  Tabela 'pacientes' já populada — pulando import.")
        return

    if not os.path.exists(CSV_PATH):
        print(f"⚠️  CSV não encontrado em {CSV_PATH} — pulando import.")
        return

    df = pd.read_csv(CSV_PATH)
    df = df.rename(columns={"nome_paciente": "nome"})
    df.to_sql("pacientes", con, if_exists="append", index=False)
    print(f"✅ {len(df)} pacientes importados de pacientes.csv")


def main() -> None:
    novo = not os.path.exists(DB_PATH)
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON")

    criar_tabelas(con)
    seed_usuario_default(con)
    seed_tipos_exame(con)
    importar_csv(con)

    con.close()
    print(f"\n📦 Banco {'criado' if novo else 'atualizado'}: {DB_PATH}")


if __name__ == "__main__":
    main()
