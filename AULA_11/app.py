"""
app.py — Sistema de Diagnóstico Clínico com IA
Referência: roteiro_final_ML-BIO.pdf

Stack: Streamlit + SQLite3 + Scikit-Learn (Random Forest .pkl)

Telas:
  🔐 Login
  🏠 Menu Principal
  👥 Cadastro de Pacientes
  🧪 Gestão de Exames (tipos + limites de alerta)
  🤖 Lançamento de Resultados + Predição IA
  📊 Avaliação do Modelo
"""

import streamlit as st
import sqlite3
import pandas as pd
import joblib
import bcrypt
import os
import subprocess
import sys

# ── Configuração da página ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Diagnóstico Clínico IA",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Caminhos ──────────────────────────────────────────────────────────────────
BASE       = os.path.dirname(os.path.abspath(__file__))
DB_PATH    = os.path.join(BASE, 'clinica.db')
MODEL_PATH = os.path.join(BASE, '..', 'AULA_09', 'modelo_risco_clinico.pkl')
SETUP      = os.path.join(BASE, 'setup_db.py')

# Inicializa BD se não existir
if not os.path.exists(DB_PATH):
    subprocess.run([sys.executable, SETUP], check=True)

# ── Helpers de BD ─────────────────────────────────────────────────────────────
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def query(sql, params=()):
    with get_conn() as c:
        return c.execute(sql, params).fetchall()

def execute(sql, params=()):
    with get_conn() as c:
        c.execute(sql, params)
        c.commit()

# ── CSS global ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: #0f172a; }
    [data-testid="stSidebar"]          { background: #1e293b; }
    .main-title { font-size:2rem; font-weight:700; color:#38bdf8; }
    .card {
        background:#1e293b; border-radius:12px;
        padding:1.2rem 1.5rem; margin-bottom:1rem;
        border-left: 4px solid #38bdf8;
    }
    .risk-alto   { color:#ef4444; font-weight:700; font-size:1.4rem; }
    .risk-medio  { color:#f59e0b; font-weight:700; font-size:1.4rem; }
    .risk-baixo  { color:#22c55e; font-weight:700; font-size:1.4rem; }
    .metric-box {
        background:#0f172a; border-radius:8px;
        padding:.8rem 1rem; text-align:center;
    }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 🔐  TELA DE LOGIN
# ══════════════════════════════════════════════════════════════════════════════
def tela_login():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown('<p class="main-title">🏥 Diagnóstico Clínico IA</p>',
                    unsafe_allow_html=True)
        st.caption("Sistema de Predição de Risco Clínico — Biomedicina")
        st.divider()

        with st.form("login_form"):
            usuario = st.text_input("👤 Usuário", placeholder="admin")
            senha   = st.text_input("🔒 Senha",   type="password", placeholder="••••••••")
            submit  = st.form_submit_button("Entrar", use_container_width=True)

        if submit:
            rows = query("SELECT senha, perfil FROM usuarios WHERE usuario = ?", (usuario,))
            if rows and bcrypt.checkpw(senha.encode(), rows[0]['senha'].encode()):
                st.session_state['logged_in'] = True
                st.session_state['usuario']   = usuario
                st.session_state['perfil']    = rows[0]['perfil']
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

        st.markdown("---")
        st.caption("💡 Acesso padrão: **admin** / **admin123**")


# ══════════════════════════════════════════════════════════════════════════════
# 👥  CADASTRO DE PACIENTES
# ══════════════════════════════════════════════════════════════════════════════
def tela_pacientes():
    st.markdown('<p class="main-title">👥 Cadastro de Pacientes</p>',
                unsafe_allow_html=True)

    with st.expander("➕ Novo Paciente", expanded=True):
        with st.form("form_paciente"):
            c1, c2 = st.columns(2)
            nome  = c1.text_input("Nome completo")
            idade = c2.number_input("Idade", 1, 120, 30)
            if st.form_submit_button("Cadastrar", use_container_width=True):
                if nome.strip():
                    execute("INSERT INTO pacientes (nome, idade) VALUES (?, ?)",
                            (nome.strip(), int(idade)))
                    st.success(f"✅ Paciente **{nome}** cadastrado!")
                else:
                    st.warning("Informe o nome do paciente.")

    st.divider()
    st.subheader("📋 Pacientes Cadastrados")
    rows = query("SELECT id, nome, idade FROM pacientes ORDER BY nome")
    if rows:
        df = pd.DataFrame(rows, columns=['ID', 'Nome', 'Idade'])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum paciente cadastrado ainda.")


# ══════════════════════════════════════════════════════════════════════════════
# 🧪  GESTÃO DE EXAMES (tipos + limites de alerta)
# ══════════════════════════════════════════════════════════════════════════════
def tela_exames():
    st.markdown('<p class="main-title">🧪 Gestão de Tipos de Exame</p>',
                unsafe_allow_html=True)

    with st.expander("➕ Novo Tipo de Exame", expanded=False):
        with st.form("form_exame_tipo"):
            c1, c2, c3, c4 = st.columns(4)
            nome_ex   = c1.text_input("Nome do Exame")
            alerta_min = c2.number_input("Valor Mín. Alerta", value=0.0)
            alerta_max = c3.number_input("Valor Máx. Alerta", value=999.0)
            unidade    = c4.text_input("Unidade", "mg/dL")
            if st.form_submit_button("Salvar Tipo", use_container_width=True):
                if nome_ex.strip():
                    execute("""INSERT INTO tipos_exame (nome, alerta_min, alerta_max, unidade)
                               VALUES (?, ?, ?, ?)""",
                            (nome_ex.strip(), alerta_min, alerta_max, unidade))
                    st.success(f"✅ Tipo **{nome_ex}** salvo!")

    st.divider()
    st.subheader("📐 Parâmetros de Alerta Configurados")
    rows = query("SELECT id, nome, alerta_min, alerta_max, unidade FROM tipos_exame")
    if rows:
        df = pd.DataFrame(rows, columns=['ID', 'Exame', 'Mín. Alerta', 'Máx. Alerta', 'Unidade'])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum tipo de exame cadastrado.")


# ══════════════════════════════════════════════════════════════════════════════
# 🤖  LANÇAMENTO DE RESULTADOS + PREDIÇÃO IA
# ══════════════════════════════════════════════════════════════════════════════
def tela_predicao():
    st.markdown('<p class="main-title">🤖 Lançamento de Resultados + Predição IA</p>',
                unsafe_allow_html=True)

    # Carrega modelo
    if not os.path.exists(MODEL_PATH):
        st.error(f"Modelo não encontrado em `{MODEL_PATH}`. Execute `treinar_modelo.py` primeiro.")
        return
    modelo = joblib.load(MODEL_PATH)
    ROTULO = {0: 'Baixo', 1: 'Médio', 2: 'Alto'}

    # Seleciona paciente
    pac_rows = query("SELECT id, nome, idade FROM pacientes ORDER BY nome")
    if not pac_rows:
        st.warning("Nenhum paciente cadastrado. Vá em **Cadastro de Pacientes** primeiro.")
        return

    pac_opts = {f"{r['nome']} (ID {r['id']})": r['id'] for r in pac_rows}
    escolha  = st.selectbox("Selecione o Paciente", list(pac_opts.keys()))
    pac_id   = pac_opts[escolha]

    # Histórico do paciente
    hist = query("""
        SELECT glicose, pressao, imc, colesterol, resultado_ia, confianca, data_exame
        FROM exames WHERE id_paciente = ?
        ORDER BY data_exame DESC LIMIT 5
    """, (pac_id,))
    if hist:
        with st.expander("📜 Últimos exames deste paciente"):
            st.dataframe(pd.DataFrame(hist,
                columns=['Glicose','PA','IMC','Colesterol','Resultado IA','Confiança (%)','Data']),
                use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("📝 Inserir Novos Dados Clínicos")

    with st.form("form_predicao"):
        c1, c2, c3, c4 = st.columns(4)
        glicose    = c1.number_input("Glicose (mg/dL)",   60.0,  300.0, 100.0, step=0.5)
        pressao    = c2.number_input("Pressão Art. (mmHg)",80.0, 200.0, 120.0, step=0.5)
        imc        = c3.number_input("IMC (kg/m²)",        13.0,  55.0,  25.0, step=0.1)
        colesterol = c4.number_input("Colesterol (mg/dL)", 100.0, 400.0, 200.0, step=0.5)
        submitted  = st.form_submit_button("🔬 Calcular Risco com IA",
                                           use_container_width=True)

    if submitted:
        import numpy as np
        df_in  = pd.DataFrame([[glicose, pressao, imc, colesterol]],
                              columns=['glicose', 'pressao_arterial', 'imc', 'colesterol'])
        # modelo espera: idade, glicose, pressao_arterial, imc, colesterol
        pac_info = query("SELECT idade FROM pacientes WHERE id = ?", (pac_id,))
        idade    = pac_info[0]['idade'] if pac_info else 40
        df_full  = pd.DataFrame([[idade, glicose, pressao, imc, colesterol]],
                                columns=['idade','glicose','pressao_arterial','imc','colesterol'])

        pred   = modelo.predict(df_full)[0]
        proba  = modelo.predict_proba(df_full)[0]
        label  = ROTULO[pred]
        conf   = proba[pred] * 100

        # Salva no BD
        execute("""
            INSERT INTO exames (id_paciente, glicose, pressao, imc, colesterol,
                                resultado_ia, confianca)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (pac_id, glicose, pressao, imc, colesterol, label, round(conf, 1)))

        # Exibe resultado
        st.divider()
        col_r, col_c = st.columns(2)

        css_class = {'Alto': 'risk-alto', 'Médio': 'risk-medio', 'Baixo': 'risk-baixo'}[label]
        icon      = {'Alto': '🔴', 'Médio': '🟠', 'Baixo': '🟢'}[label]

        col_r.markdown(f"""
        <div class="card">
            <b>Resultado da Predição</b><br>
            <span class="{css_class}">{icon} Risco {label}</span>
        </div>
        """, unsafe_allow_html=True)

        col_c.markdown(f"""
        <div class="card">
            <b>Confiança do Modelo</b><br>
            <span style="font-size:1.4rem;color:#38bdf8;font-weight:700;">{conf:.1f}%</span>
        </div>
        """, unsafe_allow_html=True)

        # Barra de probabilidades
        st.subheader("Distribuição de Probabilidades")
        prob_df = pd.DataFrame({'Classe': ['Baixo', 'Médio', 'Alto'],
                                'Probabilidade (%)': [round(p*100,1) for p in proba]})
        st.bar_chart(prob_df.set_index('Classe'))

        if label == 'Alto':
            st.error("⚠️  **ATENÇÃO MÉDICA NECESSÁRIA** — Paciente em risco clínico elevado!")
        elif label == 'Médio':
            st.warning("⚡ Acompanhamento recomendado — indicadores em nível de alerta.")
        else:
            st.success("✅ Indicadores dentro da faixa normal.")


# ══════════════════════════════════════════════════════════════════════════════
# 📊  AVALIAÇÃO DO MODELO
# ══════════════════════════════════════════════════════════════════════════════
def tela_avaliacao():
    st.markdown('<p class="main-title">📊 Avaliação do Modelo de IA</p>',
                unsafe_allow_html=True)

    if not os.path.exists(MODEL_PATH):
        st.error("Modelo não encontrado.")
        return

    modelo  = joblib.load(MODEL_PATH)
    CSV     = os.path.join(BASE, '..', 'AULA_09', 'pacientes_tratados.csv')

    if not os.path.exists(CSV):
        st.warning("Dataset de avaliação não encontrado.")
        return

    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, confusion_matrix
    import numpy as np

    df = pd.read_csv(CSV)
    FEATURES = ['idade', 'glicose', 'pressao_arterial', 'imc', 'colesterol']
    X, y = df[FEATURES], df['classificacao_risco']
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2,
                                            random_state=42, stratify=y)
    y_pred = modelo.predict(X_test)

    # Métricas gerais
    from sklearn.metrics import accuracy_score, f1_score
    acc = accuracy_score(y_test, y_pred)
    f1  = f1_score(y_test, y_pred, average='weighted')

    c1, c2, c3 = st.columns(3)
    c1.metric("🎯 Acurácia",          f"{acc*100:.1f}%")
    c2.metric("📐 F1-Score (weighted)", f"{f1*100:.1f}%")
    c3.metric("🗂 Amostras de Teste",  len(y_test))

    st.divider()
    # Relatório por classe
    st.subheader("Relatório por Classe")
    report = classification_report(y_test, y_pred,
                                   target_names=['Baixo','Médio','Alto'],
                                   output_dict=True)
    st.dataframe(pd.DataFrame(report).T.round(2), use_container_width=True)

    # Matriz de confusão
    st.subheader("Matriz de Confusão")
    cm = confusion_matrix(y_test, y_pred)
    cm_df = pd.DataFrame(cm,
                         index=['Real: Baixo','Real: Médio','Real: Alto'],
                         columns=['Pred: Baixo','Pred: Médio','Pred: Alto'])
    st.dataframe(cm_df, use_container_width=True)

    # Importância das features
    st.subheader("Importância das Features (Random Forest)")
    imp = pd.DataFrame({'Feature': FEATURES,
                        'Importância': modelo.feature_importances_}
                       ).sort_values('Importância', ascending=False)
    st.bar_chart(imp.set_index('Feature'))


# ══════════════════════════════════════════════════════════════════════════════
# 👤  GESTÃO DE USUÁRIOS (apenas admin)
# ══════════════════════════════════════════════════════════════════════════════
def tela_usuarios():
    st.markdown('<p class="main-title">👤 Gestão de Usuários</p>',
                unsafe_allow_html=True)

    if st.session_state.get('perfil') != 'admin':
        st.error("Acesso restrito ao administrador.")
        return

    with st.expander("➕ Novo Usuário"):
        with st.form("form_usuario"):
            c1, c2, c3 = st.columns(3)
            novo_user   = c1.text_input("Usuário")
            nova_senha  = c2.text_input("Senha", type="password")
            novo_perfil = c3.selectbox("Perfil", ['medico', 'admin'])
            if st.form_submit_button("Criar Usuário", use_container_width=True):
                if novo_user.strip() and nova_senha:
                    h = bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt()).decode()
                    try:
                        execute("INSERT INTO usuarios (usuario, senha, perfil) VALUES (?,?,?)",
                                (novo_user.strip(), h, novo_perfil))
                        st.success(f"✅ Usuário **{novo_user}** criado!")
                    except Exception:
                        st.error("Usuário já existe.")

    st.divider()
    rows = query("SELECT id, usuario, perfil FROM usuarios")
    st.dataframe(pd.DataFrame(rows, columns=['ID','Usuário','Perfil']),
                 use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# 🏠  ROTEAMENTO PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
def main():
    if not st.session_state.get('logged_in'):
        tela_login()
        return

    # Sidebar
    with st.sidebar:
        st.markdown(f"### 🏥 Diagnóstico Clínico IA")
        st.caption(f"👤 {st.session_state['usuario']} · {st.session_state['perfil']}")
        st.divider()
        pagina = st.radio("Navegação", [
            "🏠 Início",
            "👥 Pacientes",
            "🧪 Tipos de Exame",
            "🤖 Predição IA",
            "📊 Avaliação do Modelo",
            "👤 Usuários",
        ])
        st.divider()
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # Roteamento
    if pagina == "🏠 Início":
        st.markdown('<p class="main-title">🏠 Painel Principal</p>', unsafe_allow_html=True)
        total_pac = query("SELECT COUNT(*) as n FROM pacientes")[0]['n']
        total_ex  = query("SELECT COUNT(*) as n FROM exames")[0]['n']
        alto      = query("SELECT COUNT(*) as n FROM exames WHERE resultado_ia='Alto'")[0]['n']

        c1, c2, c3 = st.columns(3)
        c1.metric("👥 Pacientes",     total_pac)
        c2.metric("🧪 Exames",        total_ex)
        c3.metric("🔴 Risco Alto",    alto)

        st.divider()
        st.subheader("📋 Últimos Exames Realizados")
        ultimos = query("""
            SELECT p.nome, e.glicose, e.pressao, e.imc, e.colesterol,
                   e.resultado_ia, e.confianca, e.data_exame
            FROM exames e JOIN pacientes p ON e.id_paciente = p.id
            ORDER BY e.data_exame DESC LIMIT 10
        """)
        if ultimos:
            st.dataframe(pd.DataFrame(ultimos,
                columns=['Paciente','Glicose','PA','IMC','Colesterol',
                         'Resultado IA','Confiança (%)','Data']),
                use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum exame registrado ainda.")

    elif pagina == "👥 Pacientes":
        tela_pacientes()
    elif pagina == "🧪 Tipos de Exame":
        tela_exames()
    elif pagina == "🤖 Predição IA":
        tela_predicao()
    elif pagina == "📊 Avaliação do Modelo":
        tela_avaliacao()
    elif pagina == "👤 Usuários":
        tela_usuarios()


if __name__ == '__main__':
    main()
