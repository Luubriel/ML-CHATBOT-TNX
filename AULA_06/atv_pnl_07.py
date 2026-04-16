from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

frases = [
    "quero comprar produto",
    "desejo fazer compra",
    "quero cancelar pedido",
    "cancelar minha compra",
    "qual horário funcionamento",
    "vocês abrem sábado"
]

intencoes = [
    "comprar",
    "comprar",
    "cancelar",
    "cancelar",
    "horario",
    "horario"
]

# TODO criar vetorizador
vetorizador = CountVectorizer()

# TODO transformar frases em vetores
X = vetorizador.fit_transform(frases)

# TODO treinar modelo Naive Bayes
modelo = MultinomialNB()
modelo.fit(X, intencoes)

# TODO pedir frase do usuário
entrada = input("Digite sua mensagem: ")

# TODO transformar entrada em vetor
entrada_vetor = vetorizador.transform([entrada])

# TODO prever intenção
predicao = modelo.predict(entrada_vetor)

print("Intenção detectada:", predicao[0])

#Resultado esperado:
# Digite sua mensagem: quero saber horário
# Intenção detectada: horario
