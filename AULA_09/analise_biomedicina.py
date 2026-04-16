"""
ATIVIDADE 3 - Análise e Validação do Dataset de Biomedicina
Referência: Documento Técnico - Predição de Risco Clínico (PDF aprovado)
            AULA_09/Roteiro_Aula09 — Itens 8.1 e 8.2

Alinhamento com o Documento Técnico:
  RF01: Variáveis usadas: nome_paciente, idade, glicose, pressao_arterial, imc, colesterol
  RF02: Validação e normalização — zeros impossíveis substituídos pela mediana
  RF06_ML: Risco classificado como Baixo (0) / Médio (1) / Alto (2)
  Modelo de dados: colunas espelham tabela 'avaliacao_risco_clinico'

Requisito 8.1: Identificar zeros/nulos em colunas biomédicas críticas
               (glicose, pressao_arterial, imc) e substituir pela mediana.

Requisito 8.2: Listar os 10 pacientes com maiores glicose e
               os 10 com maiores colesterol.
"""

import pandas as pd
import numpy as np
import os
import subprocess

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(OUTPUT_DIR, 'pacientes.csv')

# Garante que o dataset existe
if not os.path.exists(dataset_path):
    print("⚠️  'pacientes.csv' não encontrado. Executando gerador...")
    subprocess.run(
        ['python3', os.path.join(OUTPUT_DIR, 'gerador_biomedicina.py')],
        check=True
    )

log_lines = []
def log(msg=""):
    print(msg)
    log_lines.append(str(msg))

# ----------------------------------------------------------
# CARREGAMENTO
# ----------------------------------------------------------
df = pd.read_csv(dataset_path)

log("=" * 60)
log("ATIVIDADE 3 — ANÁLISE E VALIDAÇÃO DO DATASET DE BIOMEDICINA")
log("Referência: Documento Técnico - Predição de Risco Clínico")
log("=" * 60)
log(f"\n→ Dataset carregado: {len(df)} registros, {len(df.columns)} colunas.")
log(f"  Colunas: {list(df.columns)}")

# Mapeamento do risco (espelha o ENUM do documento técnico)
rotulo_risco = {0: 'Baixo', 1: 'Médio', 2: 'Alto'}
df['risco_label'] = df['classificacao_risco'].map(rotulo_risco)

log("\n→ Distribuição de classificação_risco (conforme RF06_ML):")
dist = df['classificacao_risco'].value_counts().sort_index()
for k, v in dist.items():
    log(f"   [{rotulo_risco[k]:5s}] : {v:4d} pacientes ({v/len(df)*100:.1f}%)")

# ==============================================================
# REQUISITO 8.1 — RF02: Validação e Normalização
# Identificar zeros biologicamente impossíveis e nulos em
# colunas críticas; substituir pela mediana da coluna.
# ==============================================================
log("\n" + "-" * 60)
log("VALIDAÇÃO RF02: Zeros Impossíveis (glicose, pressao_arterial, imc)")
log("(Conforme especificação funcional RF02 — Processamento e Validação)")
log("-" * 60)

# Colunas onde zero é biologicamente impossível (RF01 do doc técnico)
colunas_vitais = ['glicose', 'pressao_arterial', 'imc']

for col in colunas_vitais:
    zeros = (df[col] == 0).sum()
    nulos = df[col].isnull().sum()
    total_problemas = zeros + nulos

    log(f"\n  Coluna '{col}':")
    log(f"    → Registros com valor 0 (biologicamente impossível): {zeros}")
    log(f"    → Registros nulos / ausentes                       : {nulos}")
    log(f"    → Total de inconsistências detectadas              : {total_problemas}")

    if total_problemas > 0:
        # Substitui zeros por NaN para cálculo correto da mediana
        df[col] = df[col].replace(0, np.nan)
        mediana = df[col].median()

        # Aplica a mediana (conforme requisito 8.1 do roteiro)
        df[col] = df[col].fillna(mediana)

        log(f"    → Mediana calculada (sem os zeros/nulos): {mediana:.2f}")
        log(f"    ✅ Substituição pela mediana concluída com sucesso.")
    else:
        log(f"    ✅ Nenhuma inconsistência detectada nesta coluna.")

log("\n→ Verificação pós-tratamento (RF02 — consistência garantida):")
for col in colunas_vitais:
    zeros_rest = (df[col] == 0).sum()
    nulos_rest = df[col].isnull().sum()
    log(f"  '{col}': zeros={zeros_rest} | nulos={nulos_rest} ✅")

# ==============================================================
# REQUISITO 8.2 — Listagem dos Top 10 por Glicose e Colesterol
# ==============================================================
log("\n" + "-" * 60)
log("ANÁLISE EXPLORATÓRIA: Top 10 Pacientes Críticos")
log("(Identificação de pacientes em situação de maior risco clínico)")
log("-" * 60)

# Colunas para exibição — espelham o modelo de dados do doc técnico
cols_exibir = ['nome_paciente', 'idade', 'glicose', 'pressao_arterial',
               'imc', 'colesterol', 'risco_label']

# Top 10 por Glicose (pacientes com maior risco de diabetes/complicações)
top10_glicose = df.nlargest(10, 'glicose')[cols_exibir].copy()
top10_glicose = top10_glicose.rename(columns={'risco_label': 'classificacao_risco'})

log("\n  🔴 Top 10 Pacientes com Maiores Níveis de GLICOSE (mg/dL):")
log("  (Referência clínica: ≥126 = faixa diabética conforme ADA Guidelines)")
log(top10_glicose.to_string(index=False))

# Top 10 por Colesterol (pacientes com maior risco cardiovascular)
top10_colesterol = df.nlargest(10, 'colesterol')[cols_exibir].copy()
top10_colesterol = top10_colesterol.rename(columns={'risco_label': 'classificacao_risco'})

log("\n  🟠 Top 10 Pacientes com Maiores Níveis de COLESTEROL (mg/dL):")
log("  (Referência clínica: ≥240 = colesterol alto conforme AHA Guidelines)")
log(top10_colesterol.to_string(index=False))

# ----------------------------------------------------------
# Estatísticas descritivas finais do dataset tratado
# ----------------------------------------------------------
log("\n" + "-" * 60)
log("ESTATÍSTICAS DESCRITIVAS DO DATASET TRATADO:")
log("-" * 60)
stats = df[['idade', 'glicose', 'pressao_arterial', 'imc', 'colesterol']].describe().round(2)
log(stats.to_string())

# ----------------------------------------------------------
# SALVA DATASET TRATADO
# ----------------------------------------------------------
# Remove coluna auxiliar antes de salvar
df_salvar = df.drop(columns=['risco_label'])
dataset_tratado_path = os.path.join(OUTPUT_DIR, 'pacientes_tratados.csv')
df_salvar.to_csv(dataset_tratado_path, index=False)
log(f"\n✅ Dataset tratado (RF02 aplicado) salvo como 'pacientes_tratados.csv'.")
log(f"   Pronto para uso no treinamento do modelo Random Forest (RF06_ML).")

# ==============================================================
# SALVA RELATÓRIO TEXTUAL PARA SPRINT-3
# ==============================================================
log("\n" + "=" * 60)
log("ATIVIDADE 3 CONCLUÍDA!")
log("Todos os requisitos do Roteiro_Aula09 e do Documento Técnico atendidos.")
log("=" * 60)

relatorio_path = os.path.join(OUTPUT_DIR, 'resultado_biomedicina.txt')
with open(relatorio_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(log_lines))

print(f"\n✅ Relatório completo salvo em '{relatorio_path}'")
print(f"   → Insira este arquivo na janela da SPRINT-3.")
