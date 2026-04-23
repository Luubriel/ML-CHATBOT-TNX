"""
Treina um Random Forest Classifier sobre o dataset 'pacientes_tratados.csv'
e salva o artefato treinado como 'modelo_risco_clinico.pkl'.
Execute este script uma vez antes de rodar a interface gráfica.
"""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

BASE = os.path.dirname(os.path.abspath(__file__))

# ── 1. Carrega o dataset tratado ─────────────────────────────
df = pd.read_csv(os.path.join(BASE, 'pacientes_tratados.csv'))

FEATURES = ['idade', 'glicose', 'pressao_arterial', 'imc', 'colesterol']
TARGET   = 'classificacao_risco'

X = df[FEATURES]
y = df[TARGET]

# ── 2. Split treino / teste ───────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ── 3. Treina Random Forest ───────────────────────────────────
modelo = RandomForestClassifier(
    n_estimators=200,
    max_depth=None,
    random_state=42,
    class_weight='balanced'
)
modelo.fit(X_train, y_train)

# ── 4. Avaliação ──────────────────────────────────────────────
y_pred = modelo.predict(X_test)
labels = ['Baixo', 'Médio', 'Alto']
print("=" * 60)
print("RELATÓRIO DE AVALIAÇÃO — Random Forest Classifier")
print("=" * 60)
print(classification_report(y_test, y_pred, target_names=labels))

# ── 5. Salva o artefato ───────────────────────────────────────
model_path = os.path.join(BASE, 'modelo_risco_clinico.pkl')
joblib.dump(modelo, model_path)
print(f"✅ Modelo salvo em: {model_path}")
