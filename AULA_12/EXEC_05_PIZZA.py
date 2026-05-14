"""
EXERCÍCIO 5 — Intent + Entity Extraction
Chatbot de Pedido de Pizza — Implementação completa.
"""
import re

SABORES = ['calabresa', 'frango', 'queijo', 'portuguesa', 'vegetariana', 'pepperoni']
TAMANHOS = ['pequena', 'media', 'média', 'grande', 'gigante', 'família', 'familia']

def detectar_intencao(mensagem: str) -> str:
    msg = mensagem.lower()
    if any(p in msg for p in ['quero', 'pedir', 'pedido', 'comprar', 'queria', 'vê', 'vou', 'querer']):
        return 'FAZER_PEDIDO'
    elif any(p in msg for p in ['cancelar', 'desistir', 'não quero', 'nao quero']):
        return 'CANCELAR'
    elif any(p in msg for p in ['cardápio', 'cardapio', 'opções', 'opcoes', 'tem']):
        return 'VER_CARDAPIO'
    return 'DESCONHECIDO'

def extrair_entidades(mensagem: str) -> dict:
    msg = mensagem.lower()
    # TODO REPLETO: identifica sabor e tamanho
    entidades = {'sabor': None, 'tamanho': None}
    
    for s in SABORES:
        if s in msg:
            entidades['sabor'] = s
            break
            
    for t in TAMANHOS:
        if t in msg:
            entidades['tamanho'] = t
            break
            
    return entidades

def confirmar_pedido(entidades: dict) -> str:
    # TODO REPLETO: formata confirmação
    sabor = entidades['sabor']
    tamanho = entidades['tamanho']
    
    if sabor and tamanho:
        return f"✅ Perfeito! Registrei seu pedido: uma pizza {tamanho.upper()} de {sabor.upper()}. Posso enviar?"
    elif sabor:
        return f"🍕 Entendi que você quer de {sabor.upper()}, mas qual o TAMANHO? (Pequena, Média ou Grande?)"
    elif tamanho:
        return f"🍕 Uma pizza {tamanho.upper()}! Qual o SABOR você deseja?"
    else:
        return "🤔 Quero te ajudar com o pedido! Me diga o sabor e o tamanho da sua pizza."

def chatbot_pizza():
    print('=== PizzaBot — Faça seu pedido! ===')
    print('Ex: "Quero uma pizza grande de calabresa"')
    print('='*40)
    while True:
        entrada = input('Você: ').strip()
        if not entrada: continue
        if entrada.lower() in ('sair', 'tchau'):
            print('Bot: Pedido cancelado. Até logo!')
            break
            
        intencao = detectar_intencao(entrada)
        print(f' [DEBUG] Intenção: {intencao}')
        
        if intencao == 'VER_CARDAPIO':
            print(f'Bot: Sabores disponíveis: {", ".join(SABORES)}')
            print(f'Bot: Tamanhos: Pequena, Média, Grande, Gigante')
        elif intencao == 'FAZER_PEDIDO':
            entidades = extrair_entidades(entrada)
            print(f' [DEBUG] Entidades: {entidades}')
            resposta = confirmar_pedido(entidades)
            print(f'Bot: {resposta}')
        elif intencao == 'CANCELAR':
            print('Bot: Seu pedido foi cancelado.')
        else:
            print('Bot: Não entendi. Você pode pedir uma pizza ou ver o cardápio.')
        print()

if __name__ == '__main__':
    chatbot_pizza()
