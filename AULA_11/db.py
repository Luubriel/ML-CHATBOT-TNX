"""
Helpers de acesso ao banco SQLite 'clinica.db'.
Todas as telas da UI conversam com o banco através destas funções.
"""

import sqlite3
import bcrypt

from paths import DB_PATH


def conectar() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


# ── Autenticação ─────────────────────────────────────────────────────────────
def autenticar(username: str, senha: str) -> bool:
    with conectar() as con:
        row = con.execute(
            "SELECT password_hash FROM usuarios WHERE username = ?", (username,)
        ).fetchone()
    if not row:
        return False
    return bcrypt.checkpw(senha.encode("utf-8"), row["password_hash"].encode("utf-8"))


def criar_usuario(username: str, senha: str) -> bool:
    pw_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    try:
        with conectar() as con:
            con.execute(
                "INSERT INTO usuarios (username, password_hash) VALUES (?, ?)",
                (username, pw_hash),
            )
        return True
    except sqlite3.IntegrityError:
        return False


# ── Tipos de exame ───────────────────────────────────────────────────────────
def listar_tipos_exame() -> list[sqlite3.Row]:
    with conectar() as con:
        return con.execute(
            "SELECT id, nome, unidade, valor_alerta FROM tipos_exame ORDER BY nome"
        ).fetchall()


def inserir_tipo_exame(nome: str, unidade: str, valor_alerta: float) -> bool:
    try:
        with conectar() as con:
            con.execute(
                "INSERT INTO tipos_exame (nome, unidade, valor_alerta) VALUES (?, ?, ?)",
                (nome, unidade, valor_alerta),
            )
        return True
    except sqlite3.IntegrityError:
        return False


def atualizar_tipo_exame(id_tipo: int, valor_alerta: float) -> None:
    with conectar() as con:
        con.execute(
            "UPDATE tipos_exame SET valor_alerta = ? WHERE id = ?",
            (valor_alerta, id_tipo),
        )


def excluir_tipo_exame(id_tipo: int) -> None:
    with conectar() as con:
        con.execute("DELETE FROM tipos_exame WHERE id = ?", (id_tipo,))


# ── Pacientes ────────────────────────────────────────────────────────────────
def listar_pacientes(busca: str = "") -> list[sqlite3.Row]:
    sql = "SELECT id, nome, idade FROM pacientes"
    params: tuple = ()
    if busca:
        sql += " WHERE nome LIKE ?"
        params = (f"%{busca}%",)
    sql += " ORDER BY id DESC LIMIT 200"
    with conectar() as con:
        return con.execute(sql, params).fetchall()


def inserir_paciente(nome: str, idade: int) -> int:
    with conectar() as con:
        cur = con.execute(
            "INSERT INTO pacientes (nome, idade) VALUES (?, ?)", (nome, idade)
        )
        return cur.lastrowid


# ── Exames ───────────────────────────────────────────────────────────────────
def registrar_exame(
    id_paciente: int,
    glicose: float,
    pressao: float,
    imc: float,
    colesterol: float,
    resultado_ia: int,
    confianca: float,
) -> None:
    with conectar() as con:
        con.execute(
            """
            INSERT INTO exames
              (id_paciente, glicose, pressao_arterial, imc, colesterol,
               resultado_ia, confianca)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (id_paciente, glicose, pressao, imc, colesterol, resultado_ia, confianca),
        )


def historico_exames(id_paciente: int) -> list[sqlite3.Row]:
    with conectar() as con:
        return con.execute(
            """
            SELECT data, glicose, pressao_arterial, imc, colesterol,
                   resultado_ia, confianca
            FROM exames
            WHERE id_paciente = ?
            ORDER BY data DESC
            LIMIT 50
            """,
            (id_paciente,),
        ).fetchall()
