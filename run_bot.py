import os
import random
import requests
import json
import google.generativeai as genai
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# 1. PRESERVADO: Sua assinatura oficial do configuracoes.py
try:
    from configuracoes import BLOCO_FIXO_FINAL
except ImportError:
    BLOCO_FIXO_FINAL = ""

# 2. CONFIGURAÇÕES
BLOG_ID = "5251820458826857223"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

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
        if r.get('photos'):
            return r['photos'][0]['src']['large2x']
    except:
        pass
    return "https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg"

def executar():
    with open("temas.txt", "r", encoding="utf-8") as f:
        temas = [l.strip() for l in f.readlines() if l.strip()]
    
    tema = random.choice(temas)
    print(f"🚀 Preparando postagem sobre: {tema}")

    # 3. GERAÇÃO DE CONTEÚDO
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Escreva um artigo de 700 palavras sobre {tema} para o blog Emagrecer com Saúde. Use tom motivador, fonte Arial e subtítulos H2."
        response = model.generate_content(prompt)
        texto_gerado = response.text
    except Exception as e:
        print(f"Erro na IA: {e}")
        return

    # CORREÇÃO DO ERRO DE SINTAXE: Formatamos o texto antes de entrar no HTML
    texto_formatado = texto_gerado.replace('\n', '<br/>')
    img = buscar_foto(tema)
    
    # 4. MONTAGEM DO HTML (Regra 16:9 e Assinatura Preservada)
    html_final = f"""
    <div style='font-family:Arial; text-align:justify;'>
        <h1 style='text-align:center;'>{tema.upper()}</h1>
        <div style='text-align:center; margin:20px 0;'>
            <img src='{img}' style='width:100%; aspect-ratio:16/9; object-fit:cover; border-radius:10px;'/>
        </div>
        {texto_formatado}
        <br/><br/>
        {BLOCO_FIXO_FINAL}
    </div>
    """

    # 5. PUBLICAÇÃO
    try:
        creds = renovar_token()
        service = build("blogger", "v3", credentials=creds)
        service.posts().insert(
            blogId=BLOG_ID, 
            body={"title": tema.title(), "content": html_final, "status": "LIVE"}
        ).execute()
        print(f"✅ SUCESSO! Artigo '{tema}' publicado.")
    except Exception as e:
        print(f"❌ Erro ao publicar: {e}")

if __name__ == "__main__":
    executar()
