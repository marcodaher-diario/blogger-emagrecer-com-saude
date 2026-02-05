import os
import random
import requests
from google import genai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# CONFIGURAÇÕES
BLOG_ID = "5251820458826857223"
SCOPES = ["https://www.googleapis.com/auth/blogger"]
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

client_gemini = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# PROMPT EDITORIAL
PROMPT_SISTEMA = """
Você é o redator oficial do blog 'Emagrecer com Saúde'.
Sua missão: Ajudar pessoas a emagrecer com saúde e hábitos sustentáveis.
Tom de voz: Educativo, Acolhedor, Claro, Sem alarmismo.
Regra de Ouro: 'Orientar com responsabilidade, não vender ilusão'.
ESTRUTURA: Introdução empática, H2 para desenvolvimento, Dicas práticas, Conclusão motivadora.
META: Entre 600 e 900 palavras. Fonte Arial.
"""

def buscar_imagem_pexels(query):
    if not PEXELS_API_KEY: return None
    url = f"https://api.pexels.com/v1/search?query={query}&orientation=landscape&per_page=5"
    headers = {"Authorization": PEXELS_API_KEY}
    try:
        response = requests.get(url, headers=headers).json()
        if response.get('photos'):
            return response['photos'][0]['src']['large2x']
    except: pass
    return "https://images.pexels.com/photos/1103970/pexels-photo-1103970.jpeg"

def executar():
    # 1. Escolhe o tema com validação
    caminho = "temas.txt"
    if not os.path.exists(caminho):
        print("ERRO: Arquivo temas.txt não encontrado!"); return

    with open(caminho, "r", encoding="utf-8") as f:
        temas = [l.strip() for l in f.readlines() if l.strip()]

    if not temas:
        print("ERRO: O arquivo temas.txt está vazio. Adicione temas lá!"); return

    tema_escolhido = random.choice(temas)
    print(f"🚀 Iniciando post sobre: {tema_escolhido}")

    # 2. Geração de Conteúdo
    try:
        response = client_gemini.models.generate_content(
            model="gemini-1.5-flash", 
            contents=f"{PROMPT_SISTEMA}\nEscreva sobre: {tema_escolhido}"
        )
        texto = response.text
    except Exception as e:
        print(f"Erro Gemini: {e}"); return

    # 3. Validação de Tamanho
    contagem = len(texto.split())
    if not (600 <= contagem <= 900):
        print(f"⚠️ Rejeitado: {contagem} palavras. Tentando novamente no próximo ciclo."); return

    # 4. Imagens e HTML
    img1 = buscar_imagem_pexels(f"{tema_escolhido} wellness")
    img2 = buscar_imagem_pexels("healthy lifestyle")

    corpo_html = ""
    for p in texto.split('\n'):
        if p.strip():
            if len(p) < 70 and not p.endswith('.'):
                corpo_html += f"<h2 style='font-family:Arial; font-size:large; text-align:left; color:#2c3e50; margin-top:20px;'>{p}</h2>"
            else:
                corpo_html += f"<p style='font-family:Arial; font-size:medium; text-align:justify; line-height:1.6;'>{p}</p>"

    html_final = f"""
    <h1 style='font-family:Arial; font-size:x-large; text-align:center;'>{tema_escolhido.upper()}</h1>
    <div style='text-align:center; margin:20px 0;'><img src='{img1}' style='width:100%; aspect-ratio:16/9; object-fit:cover; border-radius:8px;'/></div>
    {corpo_html}
    <div style='text-align:center; margin:20px 0;'><img src='{img2}' style='width:100%; aspect-ratio:16/9; object-fit:cover; border-radius:8px;'/></div>
    <hr /><p style='text-align:center; font-family:Arial; font-weight:bold;'>O conhecimento é o combustível para o Sucesso.</p>
    <p style='text-align:right; font-family:Arial; font-size:12px;'>Por: Marco Daher<br/>© Marco Daher 2026</p>
    """

    # 5. Publicação
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    service = build("blogger", "v3", credentials=creds)
    service.posts().insert(
        blogId=BLOG_ID,
        body={"title": tema_escolhido.title(), "content": html_final, "labels": ["Saúde", "Emagrecimento"], "status": "LIVE"}
    ).execute()
    print(f"✅ Sucesso! Post '{tema_escolhido}' publicado.")

if __name__ == "__main__":
    executar()
