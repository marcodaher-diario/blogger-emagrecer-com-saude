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

# Inicialização do Cliente
client_gemini = genai.Client(api_key=GEMINI_API_KEY)

PROMPT_SISTEMA = """
Você é o redator oficial do blog 'Emagrecer com Saúde'. 
Missão: Ajudar pessoas a emagrecer com saúde. Texto entre 600 e 900 palavras. Arial.
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
    
    tema_escolhido = random.choice(temas)
    print(f"🚀 Iniciando processo para o tema: {tema_escolhido}")

    # 2. GERAÇÃO EM CASCATA (Testa vários nomes de modelos)
    texto_gerado = None
    # Lista de modelos por ordem de probabilidade de funcionamento
    modelos_disponiveis = [
        "gemini-1.5-flash", 
        "gemini-1.5-flash-001",
        "gemini-1.5-pro",
        "gemini-pro"
    ]

    for nome_modelo in modelos_disponiveis:
        try:
            print(f"Tentando modelo: {nome_modelo}...")
            response = client_gemini.models.generate_content(
                model=nome_modelo, 
                contents=f"{PROMPT_SISTEMA}\n\nEscreva um artigo completo sobre: {tema_escolhido}"
            )
            texto_gerado = response.text
            if texto_gerado:
                print(f"✅ Sucesso com o modelo: {nome_modelo}")
                break
        except Exception as e:
            print(f"❌ Falha no {nome_modelo}: {e}")

    if not texto_gerado:
        print("🛑 Todos os modelos falharam. Verifique sua cota ou região no Google AI Studio."); return

    # 3. Validação de Tamanho
    contagem = len(texto_gerado.split())
    print(f"Texto gerado com {contagem} palavras.")
    if not (600 <= contagem <= 900):
        print("⚠️ Fora do limite. Abortando."); return

    # 4. Imagens e HTML
    img1 = buscar_imagem_pexels(f"{tema_escolhido} health")
    img2 = buscar_imagem_pexels("wellness")

    corpo_html = ""
    for p in texto_gerado.split('\n'):
        if p.strip():
            if (len(p) < 80 and not p.endswith('.')) or p.startswith('#'):
                corpo_html += f"<h2 style='font-family:Arial; font-size:large; text-align:left; color:#2c3e50; margin-top:20px;'>{p.replace('#','')}</h2>"
            else:
                corpo_html += f"<p style='font-family:Arial; font-size:medium; text-align:justify; line-height:1.6;'>{p}</p>"

    html_final = f"<h1>{tema_escolhido.upper()}</h1><img src='{img1}' style='width:100%; aspect-ratio:16/9;'/><br/>{corpo_html}<br/><img src='{img2}' style='width:100%; aspect-ratio:16/9;'/><br/>{BLOCO_FIXO_FINAL}"

    # 5. Publicação
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    service = build("blogger", "v3", credentials=creds)
    service.posts().insert(
        blogId=BLOG_ID,
        body={"title": tema_escolhido.title(), "content": html_final, "labels": ["Saúde"], "status": "LIVE"}
    ).execute()
    print("✅ PUBLICADO COM SUCESSO!")

if __name__ == "__main__":
    executar()
