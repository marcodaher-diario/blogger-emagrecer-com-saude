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
        creds.refresh(Request())
        with open("token.json", "w") as f:
            f.write(creds.to_json())
    return creds

def buscar_fotos(tema, quantidade=2):
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
    print(f"🚀 Postagem de Design Final: {tema}")

    try:
        prompt_editorial = (
            f"Escreva um artigo de 800 palavras sobre {tema} para o blog 'Emagrecer com Saúde'.\n"
            "ESTRUTURA: Use obrigatoriamente a palavra 'SUBTÍTULO:' no início de cada subtítulo.\n"
            "REGRAS: Sem símbolos '#', sem introduções, comece direto no título."
        )
        
        response = client.models.generate_content(
            model="gemini-3-flash-preview", 
            contents=prompt_editorial
        )
        texto_raw = response.text
    except Exception as e:
        print(f"Erro na IA: {e}")
        return

    # 4. MONTAGEM DO HTML COM ESTILOS RÍGIDOS (#003366)
    cor_base = "#003366"
    fotos = buscar_fotos(tema)
    
    # Processamento linha a linha para garantir formatação em TODOS os subtítulos
    linhas = [l.strip() for l in texto_raw.split('\n') if l.strip()]
    paragrafos_html = []
    
    for linha in linhas:
        # Verifica se é um subtítulo (pela tag ou se está em caixa alta)
        if "SUBTÍTULO:" in linha.upper() or (len(linha) < 60 and linha.isupper()):
            texto_limpo = linha.replace("SUBTÍTULO:", "").replace("Subtítulo:", "").strip()
            paragrafos_html.append(f"<p style='color:{cor_base}; font-size:large; font-weight:bold; text-align:left; margin:25px 0 5px 0;'>{texto_limpo}</p>")
        else:
            paragrafos_html.append(f"<p style='color:{cor_base}; font-size:medium; text-align:justify; margin:10px 0;'>{linha}</p>")

    # Divisão para as duas imagens
    meio = len(paragrafos_html) // 2
    imagem_1 = f"<div style='text-align:center; margin-bottom:20px;'><img src='{fotos[0]}' style='width:100%; aspect-ratio:16/9; object-fit:cover; border-radius:10px;'/></div>"
    imagem_2 = f"<div style='text-align:center; margin:30px 0;'><img src='{fotos[1]}' style='width:100%; aspect-ratio:16/9; object-fit:cover; border-radius:10px;'/></div>"

    html_final = f"""
    <div style='font-family:Arial; color:{cor_base};'>
        <h1 style='text-align:center; font-size:x-large; font-weight:bold; margin-bottom:20px;'>{tema.upper()}</h1>
        {imagem_1}
        {"".join(paragrafos_html[:meio])}
        {imagem_2}
        {"".join(paragrafos_html[meio:])}
        <div style='margin-top:20px;'>{BLOCO_FIXO_FINAL}</div>
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
        print(f"✅ SUCESSO! Postagem '{tema}' publicada com formatação 100% corrigida.")
    except Exception as e:
        print(f"❌ Erro ao publicar: {e}")

if __name__ == "__main__":
    executar()
