import os
import random
import requests
import json
import google.generativeai as genai # Voltando para a estável que funciona no seu outro blog
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Importa sua assinatura oficial
try:
    from configuracoes import BLOCO_FIXO_FINAL
except:
    BLOCO_FIXO_FINAL = ""

# CONFIGURAÇÕES
BLOG_ID = "5251820458826857223"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

# INICIALIZAÇÃO ESTÁVEL (Igual ao seu projeto que funciona)
genai.configure(api_key=GEMINI_API_KEY)

def renovar_token():
    with open("token.json", "r") as f:
        info = json.load(f)
    creds = Credentials.from_authorized_user_info(info, ["https://www.googleapis.com/auth/blogger"])
    if creds.expired and creds.refresh_token:
        print("🔄 Renovando acesso ao Blogger...")
        creds.refresh(Request())
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
    # Lê seus 14 temas
    with open("temas.txt", "r", encoding="utf-8") as f:
        temas = [l.strip() for l in f.readlines() if l.strip()]
    
    tema = random.choice(temas)
    print(f"🤖 Preparando postagem sobre: {tema}")

    # GERAÇÃO COM A ESTRUTURA QUE FUNCIONA NO DIÁRIO DE NOTÍCIAS
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            f"Escreva um artigo de 700 palavras sobre {tema} para o blog Emagrecer com Saúde. Use Arial e subtítulos H2."
        )
        texto_corpo = response.text.replace('\n', '<br/>')
    except Exception as e:
        print(f"Erro na IA: {e}")
        return

    img = buscar_foto(tema)
    html_final = f"<div style='font-family:Arial; text-align:justify;'><h1 style='text-align:center;'>{tema.upper()}</h1><img src='{img}' style='width:100%; aspect-ratio:16/9; border-radius:10px;'/><br/>{texto_corpo}<br/>{BLOCO_FIXO_FINAL}</div>"

    try:
        creds = renovar_token()
        service = build("blogger", "v3", credentials=creds)
        service.posts().insert(blogId=BLOG_ID, body={"title": tema.title(), "content": html_final, "status": "LIVE"}).execute()
        print(f"✅ SUCESSO! Artigo sobre '{tema}' publicado.")
    except Exception as e:
        print(f"❌ Erro ao publicar: {e}")

if __name__ == "__main__":
    executar()
