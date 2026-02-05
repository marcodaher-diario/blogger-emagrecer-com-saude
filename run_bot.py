import os
import random
import requests
import json
from google import genai
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# 1. PRESERVADO: Sua assinatura oficial
try:
    from configuracoes import BLOCO_FIXO_FINAL
except ImportError:
    BLOCO_FIXO_FINAL = ""

# 2. CONFIGURAÇÕES
BLOG_ID = "5251820458826857223"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

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

def buscar_fotos(tema, quantidade=2):
    """Busca imagens no Pexels para o tema."""
    url = f"https://api.pexels.com/v1/search?query={tema}&orientation=landscape&per_page={quantidade}"
    headers = {"Authorization": PEXELS_API_KEY}
    fotos = []
    try:
        r = requests.get(url, headers=headers).json()
        for foto in r.get('photos', []):
            fotos.append(foto['src']['large2x'])
    except:
        pass
    while len(fotos) < quantidade:
        fotos.append("https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg")
    return fotos

def executar():
    with open("temas.txt", "r", encoding="utf-8") as f:
        temas = [l.strip() for l in f.readlines() if l.strip()]
    
    tema = random.choice(temas)
    print(f"🚀 Postagem Editorial para: {tema}")

    # 3. GERAÇÃO DE CONTEÚDO (Prompt com diretrizes editoriais e sem '#' )
    try:
        prompt_editorial = (
            f"Escreva um artigo original de 800 palavras sobre {tema} para o blog 'Emagrecer com Saúde'.\n"
            "PERFIL EDITORIAL: Educativo, linguagem acessível, orientação prática, sem promessas milagrosas e sem plágio.\n"
            "REGRAS DE FORMATAÇÃO:\n"
            "1. NÃO use o símbolo '#' para títulos ou listas. Use apenas numeração (1., 2., etc).\n"
            "2. Divida o texto em duas partes de aproximadamente 400 palavras cada.\n"
            "3. O texto deve começar direto no título.\n"
            "4. NÃO inclua saudações ou comentários sobre a IA."
        )
        
        response = client.models.generate_content(
            model="gemini-3-flash-preview", 
            contents=prompt_editorial
        )
        texto_gerado = response.text
    except Exception as e:
        print(f"Erro na IA: {e}")
        return

    # Processamento para dividir o texto e inserir a segunda imagem
    paragrafos = texto_gerado.split('\n\n')
    meio = len(paragrafos) // 2
    fotos = buscar_fotos(tema)
    
    # 4. MONTAGEM DO HTML (Cores RGB 7, 55, 99 e Tamanhos de Fonte)
    estilo_cor = "color: rgb(7, 55, 99);"
    
    html_corpo_1 = "<br/>".join(paragrafos[:meio]).replace('\n', '<br/>')
    html_corpo_2 = "<br/>".join(paragrafos[meio:]).replace('\n', '<br/>')

    html_final = f"""
    <div style='font-family:Arial; {estilo_cor} text-align:justify; font-size: medium;'>
        <h1 style='text-align:center; font-size: x-large; font-weight: bold;'>{tema.upper()}</h1>
        
        <div style='text-align:center; margin: 20px 0;'>
            <img src='{fotos[0]}' style='width:100%; aspect-ratio:16/9; object-fit:cover; border-radius:10px;'/>
        </div>

        {html_corpo_1}

        <div style='text-align:center; margin: 30px 0;'>
            <img src='{fotos[1]}' style='width:100%; aspect-ratio:16/9; object-fit:cover; border-radius:10px;'/>
        </div>

        {html_corpo_2}
        
        <br/><br/>
        {BLOCO_FIXO_FINAL}
    </div>
    """
    
    # Ajuste de estilo para Subtítulos (Simulando <h2> via replace para aplicar seu estilo)
    html_final = html_final.replace("<h2>", f"<h2 style='text-align: left; font-size: large; font-weight: bold; {estilo_cor}'>")

    # 5. PUBLICAÇÃO
    try:
        creds = renovar_token()
        service = build("blogger", "v3", credentials=creds)
        service.posts().insert(
            blogId=BLOG_ID, 
            body={{"title": tema.title(), "content": html_final, "status": "LIVE"}}
        ).execute()
        print(f"✅ SUCESSO! Postagem '{tema}' publicada no novo padrão visual.")
    except Exception as e:
        print(f"❌ Erro ao publicar: {e}")

if __name__ == "__main__":
    executar()
