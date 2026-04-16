"""
ATIVIDADE 3 - Gerador de Dataset Sintético para Biomedicina
Referência: Documento Técnico - Predição de Risco Clínico (PDF aprovado)
            AULA_09/prompt_biomedicina.txt

Variáveis obrigatórias (conforme RF01 do documento técnico):
  - nome_paciente (fictício, sem sobrenome)
  - idade (18–99 anos)
  - glicose
  - pressao_arterial
  - imc
  - colesterol
  - classificacao_risco (0=Baixo / 1=Médio / 2=Alto)

Gera 2000 registros e salva como 'pacientes.csv'.
As regras de risco espelham a lógica clínica descrita no documento técnico
e são coerentes com o modelo de dados da tabela 'avaliacao_risco_clinico'.
"""

import pandas as pd
import numpy as np
import os

np.random.seed(42)
N = 2000

print("=" * 60)
print("GERADOR DE DATASET SINTÉTICO - BIOMEDICINA")
print("Referência: Documento Técnico - Predição de Risco Clínico")
print(f"  Gerando {N} registros de pacientes...")
print("=" * 60)

# ----------------------------------------------------------
# 1. NOMES FICTÍCIOS (conforme RF01: "Nome fictício, simples,
#    sem sobrenomes")
# ----------------------------------------------------------
nomes_masc = [
    "Lucas", "Gabriel", "Mateus", "Pedro", "João", "Rafael",
    "Bruno", "Diego", "Thiago", "Felipe", "André", "Carlos",
    "Marcos", "Douglas", "Gustavo", "Eduardo", "Pablo", "Igor",
    "Vitor", "Alan", "Sergio", "Roberto", "Henrique", "Fábio"
]
nomes_fem = [
    "Ana", "Maria", "Julia", "Beatriz", "Laura", "Camila",
    "Fernanda", "Larissa", "Mariana", "Patricia", "Sandra",
    "Isabela", "Leticia", "Renata", "Simone", "Tamires", "Vanessa",
    "Priscila", "Natalia", "Aline", "Cristina", "Daniela", "Elaine"
]
todos_nomes = nomes_masc + nomes_fem
nomes = np.random.choice(todos_nomes, N)

# ----------------------------------------------------------
# 2. IDADE — foco de 18 a 99 anos (conforme prompt_biomedicina)
# ----------------------------------------------------------
idade = np.random.randint(18, 100, N)

# ----------------------------------------------------------
# 3. GLICOSE (mg/dL) — faixas clínicas reais
#    Normal: 70–99 | Pré-diabético: 100–125 | Diabético: ≥126
#    Documento técnico: DECIMAL(5,2), NOT NULL
# ----------------------------------------------------------
glicose = np.clip(np.random.normal(108, 32, N), 60, 300).round(2)

# ----------------------------------------------------------
# 4. PRESSÃO ARTERIAL SISTÓLICA (mmHg)
#    Normal: 90–120 | Elevada: 121–139 | Hipertensão: ≥140
#    Documento técnico: DECIMAL(5,2), NOT NULL
#    (campo pressao_arterial — armazena valor sistólico)
# ----------------------------------------------------------
pressao_arterial = np.clip(np.random.normal(122, 22, N), 80, 200).round(2)

# ----------------------------------------------------------
# 5. IMC (kg/m²)
#    Abaixo do peso: <18.5 | Normal: 18.5–24.9
#    Sobrepeso: 25–29.9  | Obeso: ≥30
#    Documento técnico: DECIMAL(5,2), NOT NULL
# ----------------------------------------------------------
imc = np.clip(np.random.normal(26.5, 6, N), 13.0, 55.0).round(2)

# ----------------------------------------------------------
# 6. COLESTEROL TOTAL (mg/dL)
#    Desejável: <200 | Limítrofe: 200–239 | Alto: ≥240
#    Documento técnico: DECIMAL(6,2), NOT NULL
# ----------------------------------------------------------
colesterol = np.clip(np.random.normal(205, 48, N), 100, 400).round(2)

# ----------------------------------------------------------
# 7. CLASSIFICAÇÃO DE RISCO — regra coerente com o documento técnico
#    O modelo preditivo (RF06_ML) usa Random Forest Classifier
#    multiclasse: 0=Baixo | 1=Médio | 2=Alto
#    A lógica abaixo simula a regra que o modelo aprenderá
# ----------------------------------------------------------
def classificar_risco(i):
    """
    Sistema de pontuação clínica alinhado às variáveis do RF01.
    Cada variável contribui com pontos; a soma define o risco.
    """
    pontos = 0

    # Glicose
    if glicose[i] >= 126:
        pontos += 2  # Faixa diabética
    elif glicose[i] >= 100:
        pontos += 1  # Faixa pré-diabética

    # Pressão Arterial
    if pressao_arterial[i] >= 140:
        pontos += 2  # Hipertensão estágio 1+
    elif pressao_arterial[i] >= 121:
        pontos += 1  # Pressão elevada

    # IMC
    if imc[i] >= 30:
        pontos += 2  # Obesidade
    elif imc[i] >= 25:
        pontos += 1  # Sobrepeso

    # Colesterol
    if colesterol[i] >= 240:
        pontos += 2  # Alto
    elif colesterol[i] >= 200:
        pontos += 1  # Limítrofe

    # Idade (fator de risco cumulativo)
    if idade[i] >= 65:
        pontos += 2  # Idoso
    elif idade[i] >= 45:
        pontos += 1  # Meia-idade

    # Classificação final (espelha o ENUM do modelo de dados)
    if pontos <= 2:
        return 0   # Baixo
    elif pontos <= 5:
        return 1   # Médio
    else:
        return 2   # Alto

classificacao_risco = np.array([classificar_risco(i) for i in range(N)])

# ----------------------------------------------------------
# 8. MONTAGEM DO DATAFRAME
#    Nomes das colunas espelham o modelo de dados do documento técnico
#    (tabela avaliacao_risco_clinico)
# ----------------------------------------------------------
df = pd.DataFrame({
    'nome_paciente'      : nomes,
    'idade'              : idade,
    'glicose'            : glicose,
    'pressao_arterial'   : pressao_arterial,
    'imc'                : imc,
    'colesterol'         : colesterol,
    'classificacao_risco': classificacao_risco
})

# ----------------------------------------------------------
# 9. INJEÇÃO DE RUÍDO CONTROLADO
#    Simula inconsistências reais para o script de análise (RF02)
#    Zeros são biologicamente impossíveis em glicose, PA e IMC
# ----------------------------------------------------------
idx_glicose  = df.sample(frac=0.03, random_state=10).index
idx_pressao  = df.sample(frac=0.02, random_state=20).index
idx_imc      = df.sample(frac=0.02, random_state=30).index

df.loc[idx_glicose, 'glicose']           = 0
df.loc[idx_pressao, 'pressao_arterial']  = 0
df.loc[idx_imc,     'imc']               = 0

# ----------------------------------------------------------
# 10. SALVAMENTO
# ----------------------------------------------------------
output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pacientes.csv')
df.to_csv(output_path, index=False)

# Relatório de geração
label = {0: 'Baixo', 1: 'Médio', 2: 'Alto'}
dist  = df['classificacao_risco'].value_counts().sort_index()

print(f"\n✅ 'pacientes.csv' gerado com sucesso!")
print(f"   Registros          : {len(df)}")
print(f"   Colunas            : {list(df.columns)}")
print(f"\n   Distribuição de Risco (ENUM Baixo/Médio/Alto):")
for k, v in dist.items():
    print(f"     [{label[k]:5s}] : {v:4d} pacientes ({v/N*100:.1f}%)")
print(f"\n   Zeros injetados (ruído para validação do RF02):")
print(f"     glicose=0         : {(df['glicose']==0).sum()}")
print(f"     pressao_arterial=0: {(df['pressao_arterial']==0).sum()}")
print(f"     imc=0             : {(df['imc']==0).sum()}")

print("\n" + "=" * 60)
print("Estatísticas descritivas do dataset gerado:")
print(df.describe().round(2).to_string())
print("=" * 60)
