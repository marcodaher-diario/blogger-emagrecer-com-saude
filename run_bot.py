import os
import random
import requests
import json
from google import genai
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

# INICIALIZAÇÃO CORRETA: Versão definida na criação do cliente
client_gemini = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options={'api_version': 'v1'}
)

def renovar_token():
    """Usa o Refresh Token para validar o acesso expirado de 2024."""
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
    # Lê seus 14 temas salvos no GitHub
    with open("temas.txt", "r", encoding="utf-8") as f:
        temas = [l.strip() for l in f.readlines() if l.strip()]
    
    tema = random.choice(temas)
    print(f"🤖 Preparando postagem sobre: {tema}")

    # GERAÇÃO SIMPLIFICADA (Sem inputs extras proibidos)
    texto_corpo = ""
    try:
        # Tentativa direta com Flash
        response = client_gemini.models.generate_content(
            model='gemini-1.5-flash', 
            contents=f"Escreva um artigo de 700 palavras sobre {tema} para o blog Emagrecer com Saúde. Use Arial e subtítulos H2."
        )
        texto_corpo = response.text.replace('\n', '<br/>')
    except Exception as e:
        print(f"Tentando alternativa Pro: {e}")
        try:
            # Alternativa com Pro
            response = client_gemini.models.generate_content(
                model='gemini-1.5-pro', 
                contents=f"Escreva um artigo de 700 palavras sobre {tema} para o blog Emagrecer com Saúde. Use Arial e subtítulos H2."
            )
            texto_corpo = response.text.replace('\n', '<br/>')
        except Exception as e2:
            print(f"❌ Falha total: {e2}")
            return

    img = buscar_foto(tema)
    html_final = f"<div style='font-family:Arial; text-align:justify;'><h1 style='text-align:center;'>{tema.upper()}</h1><img src='{img}' style='width:100%; aspect-ratio:16/9; border-radius:10px;'/><br/>{texto_corpo}<br/>{BLOCO_FIXO_FINAL}</div>"

    try:
        creds = renovar_token()
        service = build("blogger", "v3", credentials=creds)
        service.posts().insert(blogId=BLOG_ID, body={"title": tema.title(), "content": html_final, "status": "LIVE"}).execute()
        print(f"✅ SUCESSO! Post sobre '{tema}' publicado.")
    except Exception as e:
        print(f"❌ Erro ao publicar: {e}")

if __name__ == "__main__":
    executar()
