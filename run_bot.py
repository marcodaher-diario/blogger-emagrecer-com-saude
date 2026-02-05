import os
import random
import requests
import json
from google import genai
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# 1. PRESERVADO: Sua assinatura oficial do arquivo configuracoes.py
try:
    from configuracoes import BLOCO_FIXO_FINAL
except ImportError:
    BLOCO_FIXO_FINAL = ""

# 2. CONFIGURAÇÕES (Lendo a nova chave ...tRBY do GitHub)
BLOG_ID = "5251820458826857223"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

# Inicialização com a biblioteca google-genai (Padrão 2026)
client = genai.Client(api_key=GEMINI_API_KEY)

def renovar_token():
    """Usa o Refresh Token para validar o acesso ao Blogger automaticamente."""
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
    """Busca imagem no Pexels e retorna o link da foto."""
    url = f"https://api.pexels.com/v1/search?query={tema}&orientation=landscape&per_page=1"
    headers = {"Authorization": PEXELS_API_KEY}
    try:
        r = requests.get(url, headers=headers).json()
        if r.get('photos'):
            return r['photos'][0]['src']['large2x']
    except:
        pass
    # Link reserva caso a busca falhe
    return "https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg"

def executar():
    # Lê seus 14 temas originais do arquivo temas.txt
    with open("temas.txt", "r", encoding="utf-8") as f:
        temas = [l.strip() for l in f.readlines() if l.strip()]
    
    tema = random.choice(temas)
    print(f"🚀 Iniciando postagem limpa sobre: {tema}")

    # 3. GERAÇÃO DE CONTEÚDO (Prompt ajustado para evitar poluição visual)
    try:
        prompt_limpo = (
            f"Escreva um artigo profissional de 700 palavras sobre {tema} para o blog Emagrecer com Saúde. "
            "REGRAS OBRIGATÓRIAS: "
            "1. NÃO inclua introduções como 'Aqui está o seu artigo' ou 'Espero que ajude'. "
            "2. NÃO mencione nomes de fontes como 'Arial' ou instruções de formatação. "
            "3. Comece o texto DIRETAMENTE pelo título. "
            "4. Use HTML básico: <h2> para subtítulos e <p> para parágrafos."
        )
        
        response = client.models.generate_content(
            model="gemini-3-flash-preview", 
            contents=prompt_limpo
        )
        texto_gerado = response.text
    except Exception as e:
        print(f"Erro na IA (Modelo 3 Flash): {e}")
        return

    # Formatação do texto para o Blogger
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

    # 5. PUBLICAÇÃO NO BLOGGER
    try:
        creds = renovar_token()
        service = build("blogger", "v3", credentials=creds)
        service.posts().insert(
            blogId=BLOG_ID, 
            body={"title": tema.title(), "content": html_final, "status": "LIVE"}
        ).execute()
        print(f"✅ SUCESSO! Artigo '{tema}' publicado sem ruídos.")
    except Exception as e:
        print(f"❌ Erro ao publicar no Blogger: {e}")

if __name__ == "__main__":
    executar()
