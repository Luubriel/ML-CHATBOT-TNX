"""
EXERCÍCIO 4 — Chatbot com Memória de Contexto
Implementação completa dos TODOs do PDF.
"""
from datetime import datetime

# Estrutura do histórico
historico = [] # Lista de dicionários {'turno': N, 'usuario': '...', 'bot': '...'}

RESPOSTAS = {
    'nome': 'Meu nome é ByteBot, seu assistente digital!',
    'ajuda': 'Posso responder sobre: nome, turno, historico, hora.',
    'hora': lambda: f'Agora são {datetime.now().strftime("%H:%M:%S")}.',
}

def processar_mensagem(mensagem: str, turno: int) -> str:
    msg = mensagem.lower().strip()
    
    if 'nome' in msg:
        return RESPOSTAS['nome']
    elif 'hora' in msg:
        return RESPOSTAS['hora']()
    elif 'turno' in msg:
        # TODO REPLETO: retorne quantos turnos já ocorreram
        return f'Este é o turno número {turno} da nossa conversa.'
    elif 'historico' in msg or 'histórico' in msg:
        # TODO REPLETO: retorne um resumo do histórico (últimas 3 mensagens do usuário)
        if not historico:
            return "Ainda não temos histórico de mensagens."
        ultimas = historico[-3:]
        resumo = "Últimas interações:\n"
        for h in ultimas:
            resumo += f"  T{h['turno']} - Você: '{h['usuario']}'\n"
        return resumo
    else:
        return 'Não entendi. Digite "ajuda" para ver o que posso fazer.'

def registrar_turno(turno: int, usuario: str, bot: str):
    # TODO REPLETO: adicione o turno ao histórico com os campos corretos
    historico.append({
        'turno': turno,
        'usuario': usuario,
        'bot': bot
    })

def chatbot_contextual():
    print('=== ByteBot — Chatbot com Memória ===')
    print('Digite "ajuda" para começar ou "sair" para encerrar.')
    print('='*40)
    turno = 0
    while True:
        entrada = input('Você: ').strip()
        if not entrada: continue
        if entrada.lower() in ('sair', 'tchau'):
            print(f'Bot: Até mais! Foram {turno} turnos de conversa.')
            break
        
        turno += 1
        resposta = processar_mensagem(entrada, turno)
        registrar_turno(turno, entrada, resposta)
        print(f'Bot: {resposta}\n')

if __name__ == '__main__':
    chatbot_contextual()
