import os
import random
import requests
from google import genai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# IMPORTAÇÃO DA ASSINATURA OFICIAL
try:
    from configuracoes import BLOCO_FIXO_FINAL
except ImportError:
    BLOCO_FIXO_FINAL = "<p style='text-align:center;'>© Marco Daher 2026</p>"

# CONFIGURAÇÕES
BLOG_ID = "5251820458826857223"
SCOPES = ["https://www.googleapis.com/auth/blogger"]
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

# Inicialização do Cliente Gemini
client_gemini = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

PROMPT_SISTEMA = """
Você é o redator oficial do blog 'Emagrecer com Saúde'. 
Missão: Ajudar pessoas a emagrecer com saúde e hábitos sustentáveis.
Tom de voz: Educativo, Acolhedor, Claro, Sem alarmismo.
Regra de Ouro: 'Orientar com responsabilidade, não vender ilusão'.
ESTRUTURA: Introdução empática, Subtítulos H2, Aplicação prática e Conclusão motivadora.
REQUISITO: Mínimo 600 e máximo 900 palavras. Tipografia: Arial.
"""

def buscar_imagem_pexels(query):
    if not PEXELS_API_KEY: return "https://images.pexels.com/photos/1103970/pexels-photo-1103970.jpeg"
    url = f"https://api.pexels.com/v1/search?query={query}&orientation=landscape&per_page=5"
    headers = {"Authorization": PEXELS_API_KEY}
    try:
        response = requests.get(url, headers=headers).json()
        if response.get('photos'):
            return response['photos'][0]['src']['large2x']
    except: pass
    return "https://images.pexels.com/photos/1103970/pexels-photo-1103970.jpeg"

def executar():
    # 1. Sorteio do Tema
    caminho_temas = "temas.txt"
    if not os.path.exists(caminho_temas): return
    with open(caminho_temas, "r", encoding="utf-8") as f:
        temas = [l.strip() for l in f.readlines() if l.strip()]
    if not temas: return
    
    tema_escolhido = random.choice(temas)
    print(f"Processando: {tema_escolhido}")

    # 2. Geração de Conteúdo (Correção do erro 404)
    texto_gerado = None
    modelos_para_testar = ["gemini-1.5-flash", "models/gemini-1.5-flash"]
    
    for modelo in modelos_para_testar:
        try:
            response = client_gemini.models.generate_content(
                model=modelo,
                contents=f"{PROMPT_SISTEMA}\n\nEscreva sobre: {tema_escolhido}"
            )
            texto_gerado = response.text
            break 
        except Exception as e:
            print(f"Erro com modelo {modelo}: {e}")

    if not texto_gerado:
        print("Falha total na geração do texto."); return

    # 3. Validação de Tamanho (600-900 palavras)
    contagem = len(texto_gerado.split())
    if not (600 <= contagem <= 900):
        print(f"Texto com {contagem} palavras rejeitado."); return

    # 4. Imagens e Formatação HTML
    img1 = buscar_imagem_pexels(f"{tema_escolhido} health")
    img2 = buscar_imagem_pexels("wellness lifestyle")
