"""
Cliente Gemini — encapsula configuração da SDK e construção do modelo
para o chatbot da clínica de Biomedicina.

A chave é lida do arquivo .env localizado um nível acima desta pasta
(/home/lg/college/chatbot/ML-CHATBOT-TNX/.env), conforme o roteiro da
AULA 14.
"""

from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv
import google.generativeai as genai


SYSTEM_PROMPT = """\
Você é o **BiomedBot**, assistente virtual oficial da clínica de Biomedicina
integrada ao Sistema de Diagnóstico Clínico desta aplicação.

PERSONALIDADE:
- Cordial, empático e profissional — fala em português brasileiro.
- Explica conceitos médicos/laboratoriais em linguagem acessível, mas precisa.
- Usa emojis com moderação (🧬 🔬 ⚕️ 💉 🩺 ❤️) para deixar a conversa amigável.

ESCOPO:
- Tira dúvidas de pacientes e profissionais sobre exames laboratoriais
  (glicose, pressão arterial, IMC, colesterol), prevenção, hábitos
  saudáveis e interpretação geral de resultados.
- Explica o funcionamento do sistema (cadastro de pacientes, gestão de
  tipos de exame, predição de risco por IA com Random Forest).
- Quando o usuário fornecer dados de um paciente (via comando interno
  "[CONTEXTO_PACIENTE] ..."), use-os para personalizar a resposta.

RESTRIÇÕES IMPORTANTES:
- **NUNCA** substitua a avaliação de um médico ou biomédico humano. Sempre
  recomende consulta presencial quando houver sinais de alerta.
- Não invente valores nem diagnósticos. Se não souber, diga claramente.
- Se a pergunta fugir totalmente do tema (saúde / sistema da clínica),
  redirecione gentilmente.

FORMATO:
- Respostas curtas e objetivas (até ~6 linhas), salvo quando o usuário
  pedir detalhes.
- Use listas (com "-" ou números) quando ajudar a clareza.
"""


def carregar_chave() -> Optional[str]:
    """Procura o .env em locais previsíveis e devolve GEMINI_API_KEY."""
    aqui = os.path.dirname(os.path.abspath(__file__))
    candidatos = [
        os.path.join(aqui, ".env"),
        os.path.join(os.path.dirname(aqui), ".env"),
        os.path.join(os.path.dirname(os.path.dirname(aqui)), ".env"),
    ]
    for caminho in candidatos:
        if os.path.exists(caminho):
            load_dotenv(caminho, override=False)
            break
    return os.environ.get("GEMINI_API_KEY")


def criar_modelo(model_name: str = "gemini-flash-latest") -> genai.GenerativeModel:
    chave = carregar_chave()
    if not chave:
        raise RuntimeError(
            "GEMINI_API_KEY não encontrada. "
            "Verifique o arquivo .env em ML-CHATBOT-TNX/.env."
        )
    genai.configure(api_key=chave)
    return genai.GenerativeModel(
        model_name=model_name,
        system_instruction=SYSTEM_PROMPT,
        generation_config={
            "temperature": 0.7,
            "top_p": 0.95,
            "max_output_tokens": 1024,
        },
    )
