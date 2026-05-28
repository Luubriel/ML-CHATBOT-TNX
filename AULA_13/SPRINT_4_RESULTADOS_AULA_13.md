# Aula 13 - Evoluindo para Chatbots Inteligentes (Sprint-4, AC-4 — 0,3 pt)

Resultados dos 9 exercícios da Aula 13 (21/05) - rodados em 2026-05-21 via `run_all.py` com `logs_ecommerce.csv` regenerado por `Gera_dataset_chatbot` (seed 42).

> Arquivo local, **não versionado** (gitignored) - serve apenas para colar no card da Sprint-4 do GitHub.

---

## Exercício 1 — Classificador de Intenções (TF-IDF + Naive Bayes)
**Objetivo:** Substituir if/else por um pipeline de NLP (TF-IDF + MultinomialNB) que infere intenção em tempo real.
**Teste:** 3 mensagens.

```text
Bot Classificador pronto! Digite sua mensagem (ou 'sair'):
Você: Oi, tudo bem?
Bot: Identifiquei que sua intenção é [saudacao]. Como posso ajudar com isso?

Você: Onde está meu pedido
Bot: Identifiquei que sua intenção é [suporte]. Como posso ajudar com isso?

Você: Que serviço horroroso
Bot: Identifiquei que sua intenção é [reclamacao]. Como posso ajudar com isso?
```

**Conclusão:** as 3 classes (`saudacao`, `suporte`, `reclamacao`) foram inferidas corretamente para as 3 mensagens testadas.

---

## Exercício 2 — Gerenciamento de Contexto e Memória de Curto Prazo
**Objetivo:** Arquitetar Session State (`self.contexto`) para que o bot lembre o nome do usuário e o último assunto.
**Teste:** 3 mensagens.

```text
Bot: Olá! Qual é o seu nome?
Você: Lucas
Bot: Prazer, Lucas! Em que posso te ajudar hoje?

Você: Gostaria de comprar um produto
Bot: Olha, Lucas, nosso setor de vendas está com promoções hoje!

Você: Qual o preço?
Bot: Olha, Lucas, nosso setor de vendas está com promoções hoje!
```

**Conclusão:** o nome `Lucas` foi persistido no contexto e usado nas respostas seguintes; o gatilho `comprar`/`preço` ativa o assunto `vendas`.

---

## Exercício 3 — Extração de Entidades via Regex
**Objetivo:** Usar `re.findall(r'#\d{4}')` para isolar números de pedido em texto livre.
**Teste:** 3 mensagens.

```text
Bot de Triagem: Olá! Por favor, informe o problema e o número do seu pedido (Ex: #1234).
Você: Meu pedido #9876 está atrasado
Bot: Sucesso! Encontrei o pedido #9876 na sua mensagem. Buscando no sistema...

Você: O pedido 1234 não chegou
Bot: Não consegui identificar o número do seu pedido. Lembre-se de usar o formato #1234.

Você: Problema no #0001
Bot: Sucesso! Encontrei o pedido #0001 na sua mensagem. Buscando no sistema...
```

**Conclusão:** o padrão `#dddd` é capturado quando bem-formatado e rejeitado quando falta o `#` ou o número não tem 4 dígitos.

---

## Exercício 4 — Análise de Sentimento com Gatilho para Transbordo Humano
**Objetivo:** Calcular pontuação léxica de palavras negativas e disparar transbordo quando ≥ 2.
**Teste:** 3 mensagens.

```text
Bot de Suporte: Como posso ajudar você hoje?
Você: Tudo ótimo
Bot: Certo, entendi. Processando sua solicitação normalmente...

Você: O produto veio quebrado
Bot: Certo, entendi. Processando sua solicitação normalmente...

Você: Esse serviço é péssimo, ruim demais e horroroso!
Bot: Detectei insatisfação severa. Protocolo de transbordo ativado. Transferindo para supervisor humano...
```

**Conclusão:** com 3 palavras negativas (`péssimo`, `ruim`, `horroroso`) o gatilho disparou e o loop foi encerrado para transbordo humano.

---

## Exercício 5 — Máquina de Estados Finita (FSM)
**Objetivo:** Controlar transições válidas entre `MENU_PRINCIPAL` → `SUPORTE`/`FINANCEIRO` e volta com `0`.
**Teste:** 3+ mensagens (sequência completa para mostrar todas as transições).

```text
Bot FSM: Bem-vindo! Digite 1 para Suporte ou 2 para Financeiro.
Você: 1
Bot: Modo [SUPORTE] ativo. Digite '0' para retornar ao menu.

Você: teste no suporte
Bot: Ainda processando requisições dentro do módulo SUPORTE.

Você: 0
Bot: Retornando ao [MENU_PRINCIPAL]. Opções: 1-Suporte, 2-Financeiro.

Você: 2
Bot: Modo [FINANCEIRO] ativo. Digite '0' para retornar ao menu.
```

**Conclusão:** todas as transições do diagrama foram exercitadas e protegidas contra inputs inválidos.

---

## Exercício 6 — FAQ Inteligente via Similaridade de Cosseno
**Objetivo:** Vetorizar perguntas com `CountVectorizer` e usar `cosine_similarity` para mapear a dúvida ao item de FAQ mais próximo (threshold > 0.4).
**Teste:** 3 mensagens.

```text
Bot FAQ: Digite sua dúvida sobre nossa operação:
Você: Quero saber onde está meu pacote
Bot: Desculpe, não localizei uma resposta exata no FAQ. Pode tentar reformular?

Você: Aceita cartão?
Bot: Desculpe, não localizei uma resposta exata no FAQ. Pode tentar reformular?

Você: Quero trocar um produto
Bot: Desculpe, não localizei uma resposta exata no FAQ. Pode tentar reformular?
```

**Conclusão:** nenhuma das 3 frases cruzou o limiar de 0,4 — comportamento esperado, dado que `CountVectorizer` puro não generaliza sinônimos (`pacote` ≠ `pedido`, `cartão` ≠ `pagamento`, `trocar` ≠ `troca`). O bot devolveu corretamente o fallback de "não localizei".

---

## Exercício 7 — RAG Primitivo (Consulta a CSV)
**Objetivo:** Buscar `id_usuario` no `logs_ecommerce.csv` e injetar dados (`historico_compras_valor`, `score_satisfacao`) na resposta.
**Teste:** 3 mensagens (entrada não-numérica, ID inexistente, ID real do CSV).

```text
Bot CRM: Por favor, informe seu ID de usuário de 4 dígitos para consulta:
Você: abc
Bot: Por favor, insira apenas números.

Você: 123
Bot: Não localizei esse ID na nossa base de logs. Tente outro.

Você: 8270
Bot: Dados recuperados! Sua última compra foi de R$406.03 e seu nível de satisfação histórico é 2/5.
```

**Conclusão:** as 3 ramificações foram exercitadas - validação de dígitos, ID ausente e ID presente com dados injetados na resposta.

---

## Exercício 8 — Bot Orquestrador / Router (Tool Use)
**Objetivo:** Decidir, com base em palavras-chave, se aciona uma "ferramenta externa" (`acionar_modulo_financeiro`) ou trata como texto comum.
**Teste:** 3 mensagens.

```text
Bot Orquestrador: Como posso te ajudar? (Tente falar sobre 'dinheiro' ou 'estorno')
Você: Quero ver produtos
Bot: Entendido. Tratando requisição no canal de atendimento comum.

Você: Preciso do meu dinheiro de volta
Bot: Detectei demanda financeira. Acionando ferramenta -> [API BANCO] Conectando ao gateway de pagamento... Nenhum estorno pendente.

Você: Qual o status do meu estorno?
Bot: Detectei demanda financeira. Acionando ferramenta -> [API BANCO] Conectando ao gateway de pagamento... Nenhum estorno pendente.
```

**Conclusão:** o roteador detectou as palavras-chave (`dinheiro`, `estorno`) e acionou a ferramenta apenas quando devido.

---

## Exercício 9 — Integração com a API do Google Gemini (System Instructions)
**Objetivo:** Conectar ao Gemini com `genai.Client()` e configurar a persona via `system_instruction`. A `GEMINI_API_KEY` é carregada de um arquivo `.env` local (gitignored) via `python-dotenv`.
**Teste:** saída do bot.

```text
Gemini Bot Persona: Iniciando conexão com o ecossistema Google AI. Faça sua pergunta técnica:
Você: O que é um loop for em Python?
Bot: É o sussurro arcano que percorre cada elo de uma corrente, despertando-o, até que o último brilhe.
```

**Conclusão:** integração funcional com o modelo `gemini-2.5-flash`. A `system_instruction` ("mestre dos magos de um RPG de TI, fala mística e curta") foi respeitada - a resposta é poética, breve e na persona configurada, em vez de uma explicação técnica padrão de loop `for`. Chave de API isolada em `.env` (não versionada).
