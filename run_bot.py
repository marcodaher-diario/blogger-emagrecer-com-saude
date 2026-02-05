import os
import random
import requests
from google import genai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Importa sua assinatura oficial
try:
    from configuracoes import BLOCO_FIXO_FINAL
except:
    BLOCO_FIXO_FINAL = ""

# Configurações fixas do Blog de Emagrecimento
BLOG_ID = "5251820458826857223"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

# Inicialização usando a SDK mais estável
client = genai.Client(api_key=GEMINI_API_KEY)

def buscar_foto(tema):
    url = f"https://api.pexels.com/v1/search?query={tema}&orientation=landscape&per_page=1"
    headers = {"Authorization": PEXELS_API_KEY}
    try:
        r = requests.get(url, headers=headers).json()
        return r['photos'][0]['src']['large2x']
    except:
        return "https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg"

def executar():
    # Carrega seus 14 temas estrategicamente definidos
    with open("temas.txt", "r", encoding="utf-8") as f:
        temas = [l.strip() for l in f.readlines() if l.strip()]
    
    tema = random.choice(temas)
    print(f"🤖 Gerando conteúdo para: {tema}")

    try:
        # Usando o modelo que está ativo no seu gráfico de sucesso
        response = client.models.generate_content(
            model='gemini-1.5-flash', 
            contents=f"Escreva um artigo de 750 palavras para o blog Emagrecer com Saúde sobre: {tema}. Use tom motivador e Arial."
        )
        texto_limpo = response.text.replace('\n', '<br/>')
    except Exception as e:
        print(f"Erro na geração: {e}")
        return

    img = buscar_foto(tema)
    
    # Montagem do HTML com sua assinatura oficial
    html = f"""
    <div style='font-family:Arial; text-align:justify;'>
        <h1 style='text-align:center;'>{tema.upper()}</h1>
        <img src='{img}' style='width:100%; aspect-ratio:16/9; object-fit:cover; border-radius:10px;'/>
        <p>{texto_limpo}</p>
        <br/>
        {BLOCO_FIXO_FINAL}
    </div>
    """

    # Publicação via Blogger API
    creds = Credentials.from_authorized_user_file("token.json", ["https://www.googleapis.com/auth/blogger"])
    service = build("blogger", "v3", credentials=creds)
    
    service.posts().insert(
        blogId=BLOG_ID, 
        body={"title": tema.title(), "content": html, "status": "LIVE"}
    ).execute()
    
    print(f"✅ Sucesso! Artigo sobre '{tema}' publicado com a chave do Diário de Notícias.")

if __name__ == "__main__":
    executar()
