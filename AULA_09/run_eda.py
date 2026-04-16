"""
ATIVIDADE 2 - EDA (Análise Exploratória de Dados) - 3 Exercícios
Adaptado dos arquivos exec01_atv02_aula09.txt, exec02_atv02_aula09.txt, exec03_atv02_aula09.txt
para execução local, salvando os gráficos como imagens ao invés de plt.show().
Referência: AULA_09/Roteiro_atv02_aula09
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Backend não-interativo para salvar imagens
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os

# Redireciona o stdout para capturar os prints (relatório textual)
OUTPUT_DIR = os.path.dirname(__file__)
log_lines = []

def log(msg=""):
    print(msg)
    log_lines.append(msg)

# Configuração visual
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = [10, 6]

# ==============================================================
# GERAÇÃO DO DATASET (deve rodar o Gerador_dados_Aula09.py antes)
# ==============================================================
dataset_path = os.path.join(OUTPUT_DIR, 'logs_chatbot_eda.csv')
if not os.path.exists(dataset_path):
    log("⚠️  Dataset 'logs_chatbot_eda.csv' não encontrado. Gerando agora...")
    import subprocess
    gerador_path = os.path.join(OUTPUT_DIR, 'Gerador_dados_Aula09.py')
    subprocess.run(['python', gerador_path], check=True, cwd=OUTPUT_DIR)

# Carrega o CSV
df = pd.read_csv(dataset_path)

log("=" * 60)
log("ATIVIDADE 2 - EDA: Análise Exploratória de Dados")
log("=" * 60)
log("\n--- Resumo Inicial dos Dados ---")
log(str(df.dtypes))
log(f"\nTotal de registros: {len(df)}")
log("-" * 30)

# ==============================================================
# EXERCÍCIO 1: LIMPEZA E PERFILAMENTO
# ==============================================================
log("\n" + "=" * 60)
log("EXERCÍCIO 1: LIMPEZA E PERFILAMENTO")
log("=" * 60)

# Identificar nulos
nulos = df['satisfacao'].isnull().sum()
pct_nulos = nulos / len(df) * 100
log(f"\n→ Clientes que não avaliaram o atendimento (nulos em 'satisfacao'):")
log(f"  Total: {nulos} registros ({pct_nulos:.2f}% de dados faltantes)")

# Preencher nulos com a mediana por grupo
df['satisfacao'] = df.groupby('categoria_cliente')['satisfacao'].transform(
    lambda x: x.fillna(x.median())
)
log(f"\n→ Valores nulos preenchidos com a mediana da categoria do cliente.")
log(f"  Nulos restantes: {df['satisfacao'].isnull().sum()}")

# Remover outliers de tamanho de mensagem (Z-Score manual)
limite_superior = df['tamanho_msg'].mean() + 3 * df['tamanho_msg'].std()
df_limpo = df[df['tamanho_msg'] <= limite_superior].copy()
removidos = len(df) - len(df_limpo)
log(f"\n→ Outliers removidos (mensagens de Spam com tamanho > {limite_superior:.0f} chars):")
log(f"  Total removido: {removidos} linhas")
log(f"  Dataset limpo: {len(df_limpo)} registros")

top10_spam = df.nlargest(10, 'tamanho_msg')[['ticket_id', 'tamanho_msg', 'canal']]
log("\n→ As 10 mensagens identificadas como Spam (outliers):")
log(str(top10_spam.to_string(index=False)))

# ==============================================================
# EXERCÍCIO 2: ANÁLISE POR CATEGORIA
# ==============================================================
log("\n" + "=" * 60)
log("EXERCÍCIO 2: COMPORTAMENTO POR CATEGORIA")
log("=" * 60)

analise_cat = df_limpo.groupby('categoria_cliente').agg(
    tempo_resposta_medio=('tempo_resposta_seg', 'mean'),
    satisfacao_media=('satisfacao', 'mean'),
    volume_tickets=('ticket_id', 'count')
).round(2)

log("\n→ Performance por Categoria de Cliente (SLA):")
log(str(analise_cat.to_string()))

# Volume por canal
canal_vol = df_limpo['canal'].value_counts()
log("\n→ Volume de mensagens por canal:")
log(str(canal_vol.to_string()))
log(f"\n  Canal com maior volume: {canal_vol.idxmax()} ({canal_vol.max()} mensagens)")

# Gráfico de Barras: Satisfação Média
fig, ax = plt.subplots()
sns.barplot(data=df_limpo, x='categoria_cliente', y='satisfacao',
            palette='viridis', ax=ax, order=['Free', 'Standard', 'Premium'])
ax.set_title('Satisfação Média por Categoria de Cliente', fontsize=14, fontweight='bold')
ax.set_ylabel('Score Médio (1-5)')
ax.set_xlabel('Categoria')
for bar in ax.patches:
    ax.annotate(f'{bar.get_height():.2f}',
                (bar.get_x() + bar.get_width() / 2., bar.get_height()),
                ha='center', va='bottom', fontweight='bold')
plt.tight_layout()
grafico2_path = os.path.join(OUTPUT_DIR, 'grafico_satisfacao_categoria.png')
plt.savefig(grafico2_path, dpi=150)
plt.close()
log(f"\n→ Gráfico salvo: '{grafico2_path}'")

# ==============================================================
# EXERCÍCIO 3: CORRELAÇÕES E HIPÓTESES
# ==============================================================
log("\n" + "=" * 60)
log("EXERCÍCIO 3: CORRELAÇÕES E HIPÓTESES")
log("=" * 60)

# Matriz de Correlação
corr = df_limpo[['tamanho_msg', 'tempo_resposta_seg', 'satisfacao']].corr()
log("\n→ Matriz de Correlação:")
log(str(corr.round(3).to_string()))

corr_tamanho_tempo = corr.loc['tamanho_msg', 'tempo_resposta_seg']
if abs(corr_tamanho_tempo) < 0.3:
    interpretacao = "fraca correlação (sem relação significativa)"
elif abs(corr_tamanho_tempo) < 0.6:
    interpretacao = "correlação moderada"
else:
    interpretacao = "forte correlação"
log(f"\n  Correlação tamanho_msg x tempo_resposta_seg: {corr_tamanho_tempo:.3f} → {interpretacao}")

# Histograma do Tempo de Resposta
fig, ax = plt.subplots()
sns.histplot(df_limpo['tempo_resposta_seg'], kde=True, color='skyblue', ax=ax)
ax.set_title('Distribuição do Tempo de Resposta (Segundos)', fontsize=14, fontweight='bold')
ax.set_xlabel('Segundos')
ax.set_ylabel('Frequência')
plt.tight_layout()
grafico3a_path = os.path.join(OUTPUT_DIR, 'grafico_histograma_tempo_resposta.png')
plt.savefig(grafico3a_path, dpi=150)
plt.close()
log(f"\n→ Histograma salvo: '{grafico3a_path}'")

skewness = df_limpo['tempo_resposta_seg'].skew()
log(f"  Assimetria (Skewness): {skewness:.3f}")
log(f"  Interpretação: {'distribuição assimétrica à direita (Skewed Right)' if skewness > 0.5 else 'distribuição aproximadamente normal'}")

# Boxplot: Satisfação vs Intenção
fig, ax = plt.subplots(figsize=(12, 6))
ordem = df_limpo.groupby('intencao')['satisfacao'].median().sort_values().index
sns.boxplot(data=df_limpo, x='intencao', y='satisfacao',
            palette='Set3', ax=ax, order=ordem)
ax.set_title('Variabilidade da Satisfação por Tipo de Intenção', fontsize=14, fontweight='bold')
ax.set_xlabel('Intenção do Contato')
ax.set_ylabel('Score de Satisfação (1-5)')
plt.xticks(rotation=30)
plt.tight_layout()
grafico3b_path = os.path.join(OUTPUT_DIR, 'grafico_boxplot_satisfacao_intencao.png')
plt.savefig(grafico3b_path, dpi=150)
plt.close()
log(f"\n→ Boxplot salvo: '{grafico3b_path}'")

# Heatmap de Correlação
fig, ax = plt.subplots()
sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", ax=ax, linewidths=0.5)
ax.set_title('Mapa de Calor de Correlação', fontsize=14, fontweight='bold')
plt.tight_layout()
grafico3c_path = os.path.join(OUTPUT_DIR, 'grafico_heatmap_correlacao.png')
plt.savefig(grafico3c_path, dpi=150)
plt.close()
log(f"\n→ Heatmap salvo: '{grafico3c_path}'")

# Menor satisfação por intenção
satisfacao_intencao = df_limpo.groupby('intencao')['satisfacao'].agg(['mean', 'std']).round(3)
log("\n→ Satisfação média e desvio padrão por Intenção:")
log(str(satisfacao_intencao.sort_values('mean').to_string()))
pior_intencao = satisfacao_intencao['mean'].idxmin()
log(f"\n  Intenção com notas mais baixas e mais voláteis: {pior_intencao}")

# ==============================================================
# SALVA RELATÓRIO TEXTUAL
# ==============================================================
log("\n" + "=" * 60)
log("ATIVIDADE 2 CONCLUÍDA! Todos os gráficos foram salvos.")
log("=" * 60)

relatorio_path = os.path.join(OUTPUT_DIR, 'resultado_eda.txt')
with open(relatorio_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(log_lines))
print(f"\n✅ Relatório textual salvo em '{relatorio_path}'")
