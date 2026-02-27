# -*- coding: utf-8 -*-

import os
from google import genai
from configuracoes import MODELO_GEMINI, MIN_PALAVRAS, MAX_PALAVRAS


class GeminiEngine:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)

    # ==========================================================
    # GERAR TEMA DINÂMICO BASEADO NA CATEGORIA
    # ==========================================================

    def gerar_tema(self, categoria):

        prompt = f"""
Você é um especialista em saúde, nutrição e emagrecimento baseado em evidências.

Gere um ÚNICO tema altamente relevante e específico dentro da categoria:

Categoria: {categoria}

Regras obrigatórias:
- Tema educativo
- Sem promessas milagrosas
- Sem sensacionalismo
- Foco prático e aplicável
- Linguagem clara
- Título com no máximo 15 palavras
- Extremamente atrativo para SEO

Entregue apenas o título final.
"""

        response = self.client.models.generate_content(
            model=MODELO_GEMINI,
            contents=prompt
        )

        return response.text.strip().replace('"', '')

    # ==========================================================
    # GERAR ARTIGO COMPLETO
    # ==========================================================

    def gerar_artigo(self, titulo, categoria):

        prompt = f"""
Atue como um redator especialista em saúde e emagrecimento saudável.

Escreva um artigo profundo e educativo com base no título abaixo:

Título: {titulo}
Categoria: {categoria}

Diretrizes obrigatórias:

- Entre {MIN_PALAVRAS} e {MAX_PALAVRAS} palavras
- Linguagem acessível
- Educativo e prático
- Sem promessas milagrosas
- Baseado em princípios científicos reconhecidos
- Não use primeira pessoa
- Não use sensacionalismo
- Não escreva avisos médicos exagerados
- Estruture com subtítulos claros
- Parágrafos bem desenvolvidos
- Finalize com orientação prática aplicável

Importante:
- Não inclua comentários extras
- Não inclua explicações externas
- Entregue apenas o texto final já estruturado
"""

        response = self.client.models.generate_content(
            model=MODELO_GEMINI,
            contents=prompt
        )

        return response.text.strip()
