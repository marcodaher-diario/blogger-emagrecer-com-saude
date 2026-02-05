import os
import random
import requests
import json
from google import genai
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Importa sua assinatura oficial do configuracoes.py
try:
    from configuracoes import BLOCO_FIXO_FINAL
except:
    BLOCO_FIXO_FINAL = ""

# CONFIGURAÇÕES FIXAS
BLOG_ID = "5251820458826857223"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

def renovar_token():
    """Garante que o token esteja sempre válido usando o Refresh Token."""
    with open("token.json", "r") as f:
        info = json.load(f)
    
    creds = Credentials.from_authorized_user_info(info, ["https://www.googleapis.com/auth/blogger"])
    
    if creds.expired and creds.refresh_token:
        print("🔄 Token expirado. Renovando acesso...")
        creds.refresh(Request())
        # Atualiza o arquivo local para a próxima execução
        with open("token.json", "w") as f:
            f.write(creds.to_json())
    return creds

def buscar_foto(tema):
    url = f"https://api.pexels.com/v1/search?query={tema}&orientation=landscape&per_page=1"
    headers = {"Authorization": PEXELS_API_KEY}
    try:
        r = requests.get(url, headers=headers).json()
        return r['photos'][0]['src']['large2x']
    except:
        return "https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg"

def executar():
    # 1. Carrega os temas do seu temas.txt (14 linhas)
    with open("temas.txt", "r", encoding="utf-8") as f:
        temas = [l.strip() for l in f.readlines() if l.strip()]
    
    tema = random.choice(temas)
    print(f"🤖 Preparando postagem sobre: {tema}")

    # 2. Geração do conteúdo (Forçando o modelo estável v1)
    try:
        # Mudamos de 'gemini-1.5-flash' para o nome técnico completo
        # Isso evita o erro 404 na maioria das regiões
        response = client.models.generate_content(
            model='gemini-1.5-flash', 
            contents=f"Escreva um artigo de 700 palavras sobre {tema} para o blog Emagrecer com Saúde. Use Arial e subtítulos H2.",
            config={'api_version': 'v1'} # FORÇA A VERSÃO ESTÁVEL v1
        )
        texto_corpo = response.text.replace('\n', '<br/>')
    except Exception as e:
        print(f"Tentando alternativa após erro: {e}")
        # SE O ACIMA FALHAR, TESTAMOS O MODELO PRO (Que é mais estável)
        response = client.models.generate_content(
            model='gemini-1.5-pro', 
            contents=f"Escreva um artigo de 700 palavras sobre {tema} para o blog Emagrecer com Saúde. Use Arial e subtítulos H2.",
            config={'api_version': 'v1'}
        )
        texto_corpo = response.text.replace('\n', '<br/>')

    # 3. Busca de imagem 16:9
    img = buscar_foto(tema)
    
    # 4. Montagem do HTML com sua assinatura
    html_final = f"""
    <div style='font-family:Arial; text-align:justify;'>
        <h1 style='text-align:center;'>{tema.upper()}</h1>
        <div style='text-align:center;'><img src='{img}' style='width:100%; aspect-ratio:16/9; object-fit:cover; border-radius:10px;'/></div>
        <br/>
        {texto_corpo}
        <br/><br/>
        {BLOCO_FIXO_FINAL}
    </div>
    """

    # 5. Publicação com Token Renovado
    try:
        creds = renovar_token()
        service = build("blogger", "v3", credentials=creds)
        service.posts().insert(
            blogId=BLOG_ID, 
            body={"title": tema.title(), "content": html_final, "status": "LIVE"}
        ).execute()
        print(f"✅ SUCESSO! Artigo '{tema}' publicado no blog.")
    except Exception as e:
        print(f"❌ Erro ao publicar: {e}")

if __name__ == "__main__":
    executar()
