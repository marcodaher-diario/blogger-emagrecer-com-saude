# -*- coding: utf-8 -*-

import os
import re
import time
from google import genai
from google.api_core import exceptions
from configuracoes import MODELO_GEMINI, MIN_PALAVRAS, MAX_PALAVRAS


class GeminiEngine:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        # Estratégia de Fallback solicitada: 3 Modelos em 3 Ciclos
        self.modelos_fallback = [
            "gemini-3-flash-preview",
            "gemini-2.5-pro", 
            "gemini-2.5-flash"
        ]

    def _limpar_e_formatar_markdown(self, texto):
        """
        Mantido EXATAMENTE como no seu original:
        Transforma negritos Markdown em HTML <strong> e remove marcadores de título e lista.
        """
        if not texto:
            return ""
            
        # 1. Transforma **texto** em <strong>texto</strong>
        texto = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', texto)
        
        # 2. Suprime os marcadores de título #, ##, ###, etc.
        texto = re.sub(r'#+\s?', '', texto)
        
        # 3. Suprime asteriscos isolados (marcadores de lista ou itálico simples)
        texto = re.sub(r'^\s*\*\s?', '', texto, flags=re.MULTILINE)
        texto = texto.replace('*', '')
        
        return texto.strip()

    def _executar_com_resiliencia(self, prompt):
        """
        Nova lógica de 9 tentativas (3 ciclos x 3 modelos) 
        sem alterar os prompts originais.
        """
        tentativa_total = 1
        for ciclo in range(1, 4):  # 3 passagens completas
            for modelo in self.modelos_fallback:
                try:
                    print(f"Tentativa {tentativa_total}/9 | Ciclo {ciclo} | Usando: {modelo}")
                    
                    response = self.client.models.generate_content(
                        model=modelo,
                        contents=prompt
                    )

                    if response and hasattr(response, 'text') and response.text:
                        return response.text
                
                except Exception as e:
                    erro_msg = str(e).upper()
                    # Identifica se o erro é de "Lotado" (503), "Timeout" ou "Cota"
                    if any(x in erro_msg for x in ["503", "UNAVAILABLE", "DEADLINE", "429", "QUOTA"]):
                        print(f"⚠️ Modelo {modelo} indisponível ou lotado. Pulando para o próximo...")
                        time.sleep(5) # Pausa curta antes da próxima tentativa
                    else:
                        print(f"❌ Erro crítico no modelo {modelo}: {e}")
                        # Mesmo em erro crítico, tentamos o próximo modelo do ciclo
                
                tentativa_total += 1
        
        return None

    # ==========================================================
    # GERAR TEMA DINÂMICO BASEADO NA CATEGORIA
    # ==========================================================

    def gerar_tema(self, categoria):
        # Prompt ORIGINAL mantido na íntegra
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
        resultado = self._executar_com_resiliencia(prompt)
        
        if resultado:
            return resultado.strip().replace('"', '')
        return "Erro: Falha total da API após 9 tentativas ao gerar tema"

    # ==========================================================
    # GERAR ARTIGO COMPLETO
    # ==========================================================

    def gerar_artigo(self, titulo, categoria):
        # Prompt ORIGINAL mantido na íntegra
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
        resultado = self._executar_com_resiliencia(prompt)

        if resultado:
            texto_puro = resultado.strip()
            # Aplica a limpeza e conversão de tags ORIGINAL
            return self._limpar_e_formatar_markdown(texto_puro)
        
        return "Erro: Falha total da API após 9 tentativas ao gerar artigo"
