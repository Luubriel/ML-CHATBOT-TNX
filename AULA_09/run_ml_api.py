"""
ATIVIDADE 1 - Persistência e APIs com Machine Learning
Adaptado do ml_api.txt para execução local (sem Google Colab / ngrok).
Referência: AULA_09/ml_api.txt
"""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib
import json
import os

# ==============================================================
# TAREFA 1: Persistência de Modelos (Joblib)
# ==============================================================

print("=" * 60)
print("TAREFA 1: Treinamento e Persistência do Modelo")
print("=" * 60)

# Dados de exemplo: intenções de um Chatbot
data = {
    'texto': [
        "cancelar pedido", "estorno", "quero reembolso", "cobrado errado",
        "ajuda login", "senha errada", "não consigo acessar", "esqueci minha senha",
        "produto com defeito", "entrega atrasada", "rastrear pedido", "onde está meu pedido"
    ],
    'classe': [
        "financeiro", "financeiro", "financeiro", "financeiro",
        "suporte", "suporte", "suporte", "suporte",
        "reclamacao", "reclamacao", "reclamacao", "reclamacao"
    ]
}
df = pd.DataFrame(data)

# Criando um Pipeline que une Vetorização + Modelo
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('clf', LogisticRegression(max_iter=200))
])

# Treinando
pipeline.fit(df['texto'], df['classe'])
print("✅ Modelo treinado com sucesso!")

# SALVANDO O MODELO NO DISCO
model_path = os.path.join(os.path.dirname(__file__), 'modelo_chatbot.pkl')
joblib.dump(pipeline, model_path)
print(f"✅ Modelo salvo com sucesso como '{model_path}'!")

# ==============================================================
# TAREFA 2 & 3: Simulação de API + Teste de Integração Local
# (Substitui ngrok + FastAPI server por chamadas diretas ao modelo)
# ==============================================================

print("\n" + "=" * 60)
print("TAREFA 2 & 3: Simulação de API e Teste de Integração")
print("=" * 60)

# Carrega o modelo (simulando o que a API faria)
model = joblib.load(model_path)
print("✅ Modelo carregado em memória (simulando startup da API).")

# Simula o endpoint POST /predict
def predict(texto: str) -> dict:
    """Simula o endpoint POST /predict da FastAPI."""
    predicao = model.predict([texto])[0]
    probabilidades = model.predict_proba([texto])
    confianca = probabilidades.max()
    return {
        "texto_enviado": texto,
        "intencao": predicao,
        "confianca": round(float(confianca), 4),
        "status": "sucesso"
    }

# Casos de teste (simulando o Try it out do /docs)
casos_de_teste = [
    "não consigo entrar",
    "quero cancelar minha compra",
    "meu pedido sumiu",
    "fui cobrado duas vezes",
    "como redefinir minha senha?"
]

print("\n--- Resultados dos Testes de Integração ---")
resultados = []
for texto in casos_de_teste:
    resultado = predict(texto)
    resultados.append(resultado)
    print(f"\n  Entrada : \"{resultado['texto_enviado']}\"")
    print(f"  Intenção: {resultado['intencao']}")
    print(f"  Confiança: {resultado['confianca'] * 100:.2f}%")
    print(f"  Status: {resultado['status']}")

# Salva resultado em arquivo para Sprint-3
output_path = os.path.join(os.path.dirname(__file__), 'resultado_api.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)

print(f"\n✅ Resultados salvos em '{output_path}' para submissão na Sprint-3.")
print("=" * 60)
print("ATIVIDADE 1 CONCLUÍDA!")
print("=" * 60)
