import os
import random
import requests
import json
from google import genai
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Importando sua Identidade Visual e Assinatura
from template_blog import obter_esqueleto_html
try:
    from configuracoes import BLOCO_FIXO_FINAL
except ImportError:
    BLOCO_FIXO_FINAL = ""

# CONFIGURAÇÕES
BLOG_ID = "5251820458826857223"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

def renovar_token():
    with open("token.json", "r") as f:
        info = json.load(f)
    creds = Credentials.from_authorized_user_info(info, ["https://www.googleapis.com/auth/blogger"])
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open("token.json", "w") as f:
            f.write(creds.to_json())
    return creds

def buscar_fotos_aleatorias(tema, quantidade=2):
    url = f"https://api.pexels.com/v1/search?query={tema}&orientation=landscape&per_page=15"
    headers = {"Authorization": PEXELS_API_KEY}
    pool_fotos = []
    try:
        r = requests.get(url, headers=headers).json()
        for foto in r.get('photos', []):
            pool_fotos.append(foto['src']['large2x'])
    except:
        pass
    if len(pool_fotos) >= quantidade:
        return random.sample(pool_fotos, quantidade)
    return ["https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg"] * quantidade

def executar():
    with open("temas.txt", "r", encoding="utf-8") as f:
        temas = [l.strip() for l in f.readlines() if l.strip()]
    
    tema = random.choice(temas)
    print(f"🚀 Gerando Conteúdo Modular para: {tema}")

    # PROMPT MODULAR (Pede JSON para encaixar no template)
    prompt_json = (
        f"Aja como um redator especialista. Escreva sobre {tema} para o blog Emagrecer com Saúde.\n"
        "Responda EXCLUSIVAMENTE em formato JSON com estas chaves:\n"
        "'intro', 'sub1', 'texto1', 'sub2', 'texto2', 'sub3', 'texto3', 'texto_conclusao'.\n"
        "Não use Markdown, não use '#', use tom educativo e profissional."
    )

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview", 
            contents=prompt_json,
            config={'response_mime_type': 'application/json'} # Força a IA a mandar JSON puro
        )
        conteudo = json.loads(response.text)
    except Exception as e:
        print(f"Erro na geração/leitura do JSON: {e}")
        return

    # Busca as imagens para o esqueleto
    fotos = buscar_fotos_aleatorias(tema)

    # Prepara os dados para o template
    dados_post = {
        'titulo': tema,
        'img_topo': fotos[0],
        'img_meio': fotos[1],
        'intro': conteudo['intro'],
        'sub1': conteudo['sub1'],
        'texto1': conteudo['texto1'],
        'sub2': conteudo['sub2'],
        'texto2': conteudo['texto2'],
        'sub3': conteudo['sub3'],
        'texto3': conteudo['texto3'],
        'texto_conclusao': conteudo['texto_conclusao'],
        'assinatura': BLOCO_FIXO_FINAL
    }

    # "Veste" o esqueleto HTML
    html_final = obter_esqueleto_html(dados_post)

    # PUBLICAÇÃO
    try:
        creds = renovar_token()
        service = build("blogger", "v3", credentials=creds)
        service.posts().insert(
            blogId=BLOG_ID, 
            body={"title": tema.title(), "content": html_final, "status": "LIVE"}
        ).execute()
        print(f"✅ SUCESSO! Postagem '{tema}' publicada via Template MD.")
    except Exception as e:
        print(f"❌ Erro ao publicar: {e}")

if __name__ == "__main__":
    executar()
