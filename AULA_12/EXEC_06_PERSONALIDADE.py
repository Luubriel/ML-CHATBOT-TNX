"""
EXERCÍCIO 6 — Chatbot Multi-Personalidade
Implementação completa — System Prompting e Filtros.
"""

class Personalidade:
    def __init__(self, nome, tom, prefixo, vocab_proibido):
        # TODO REPLETO
        self.nome = nome
        self.tom = tom
        self.prefixo = prefixo
        self.vocab_proibido = vocab_proibido

# Definição das personalidades
PERSONALIDADES = {
    'formal': Personalidade(
        nome='Assistente Formal',
        tom='cordial e profissional',
        prefixo='Prezado usuário, ',
        vocab_proibido=['cara', 'mano', 'oi', 'beleza', 'vlw']
    ),
    'casual': Personalidade(
        nome='ChatZinho',
        tom='descontraído e jovem',
        prefixo='Oi! ',
        vocab_proibido=['prezado', 'solicito', 'outrossim', 'conforme']
    ),
    'tecnico': Personalidade(
        nome='TechBot',
        tom='técnico e direto',
        prefixo='[SYSTEM_LOG] ',
        vocab_proibido=['acho', 'talvez', 'quem sabe']
    ),
}

RESPOSTAS_GENERICAS = {
    'python': 'Python é uma linguagem de programação interpretada e de alto nível.',
    'chatbot': 'Chatbot é um sistema que simula conversas humanas de forma automatizada.',
    'ia': 'Inteligência Artificial é a capacidade de máquinas realizarem tarefas cognitivas.',
    'ajuda': 'Posso falar sobre: python, chatbot, ia. Troque personalidade com /modo.',
}

class ChatbotMultiPersonalidade:
    def __init__(self):
        self.personalidade_ativa = PERSONALIDADES['formal']

    def trocar_personalidade(self, nome: str) -> str:
        # TODO REPLETO
        if nome in PERSONALIDADES:
            self.personalidade_ativa = PERSONALIDADES[nome]
            return f"Modo alterado para: {self.personalidade_ativa.nome} ({self.personalidade_ativa.tom})"
        return f"Erro: Personalidade '{nome}' não encontrada."

    def gerar_resposta(self, mensagem: str) -> str:
        # TODO REPLETO
        msg = mensagem.lower()
        resposta_base = "Não tenho informações sobre esse assunto. Tente: python, ia ou chatbot."
        
        for chave in RESPOSTAS_GENERICAS:
            if chave in msg:
                resposta_base = RESPOSTAS_GENERICAS[chave]
                break
        
        # Aplica prefixo
        resposta_final = self.personalidade_ativa.prefixo + resposta_base
        
        # Filtra vocabulário proibido
        for termo in self.personalidade_ativa.vocab_proibido:
            if termo in resposta_final.lower():
                # Substitui mantendo o case original se possível (simplificado para ***)
                import re
                insensivel = re.compile(re.escape(termo), re.IGNORECASE)
                resposta_final = insensivel.sub('***', resposta_final)
                
        return resposta_final

    def executar(self):
        print('=== Chatbot Multi-Personalidade ===')
        print('Comandos: /modo formal | /modo casual | /modo tecnico | sair')
        print(f'Personalidade ativa: {self.personalidade_ativa.nome}')
        print('='*40)
        while True:
            entrada = input('Você: ').strip()
            if not entrada: continue
            if entrada.lower() == 'sair':
                print('Encerrando. Até logo!')
                break
            elif entrada.lower().startswith('/modo '):
                nome = entrada.split(' ', 1)[1].lower()
                print(f'Bot: {self.trocar_personalidade(nome)}')
            else:
                resposta = self.gerar_resposta(entrada)
                print(f'Bot: {resposta}')
            print()

if __name__ == '__main__':
    bot = ChatbotMultiPersonalidade()
    bot.executar()
