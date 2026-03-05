# -*- coding: utf-8 -*-

import os
import re
from google import genai
from configuracoes import MODELO_GEMINI, MIN_PALAVRAS, MAX_PALAVRAS


class GeminiEngine:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)

    def _limpar_e_formatar_markdown(self, texto):
        """
        Transforma negritos Markdown em HTML <strong> e remove marcadores de título e lista.
        """
        if not texto:
            return ""
            
        # 1. Transforma **texto** em <strong>texto</strong>
        texto = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', texto)
        
        # 2. Suprime os marcadores de título #, ##, ###, etc.
        texto = re.sub(r'#+\s?', '', texto)
        
        # 3. Suprime asteriscos isolados (marcadores de lista ou itálico simples)
        # Remove '* ' no início de linhas e '*' soltos
        texto = re.sub(r'^\s*\*\s?', '', texto, flags=re.MULTILINE)
        texto = texto.replace('*', '')
        
        return texto.strip()

    # ==========================================================
    # GERAR TEMA DINÂMICO BASEADO NA CATEGORIA
    # ==========================================================

    def gerar_tema(self, categoria):

        prompt = f"""
Atue como um especialista em saúde, nutrição e emagrecimento baseado em evidências.

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

        try:
            response = self.client.models.generate_content(
                model=MODELO_GEMINI,
                contents=prompt
            )

            if response and hasattr(response, 'text') and response.text:
                return response.text.strip().replace('"', '')
            return "Erro: Resposta vazia da IA ao gerar tema"
        except Exception as e:
            return f"Erro na API ao gerar tema: {e}"

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

        try:
            response = self.client.models.generate_content(
                model=MODELO_GEMINI,
                contents=prompt
            )

            if response and hasattr(response, 'text') and response.text:
                texto_puro = response.text.strip()
                # Aplica a limpeza e conversão de tags solicitada
                return self._limpar_e_formatar_markdown(texto_puro)
            
            return "Erro: Resposta vazia da IA ao gerar artigo"
        except Exception as e:
            return f"Erro na API ao gerar artigo: {e}"
