import os
import random
import requests
import google.generativeai as google_ia # Mudança para a biblioteca estável
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# IMPORTAÇÃO DA ASSINATURA OFICIAL
try:
    from configuracoes import BLOCO_FIXO_FINAL
except ImportError:
    BLOCO_FIXO_FINAL = "<p style='text-align:center;'>© Marco Daher 2026</p>"

# CONFIGURAÇÕES
BLOG_ID = "5251820458826857223"
SCOPES = ["https://www.googleapis.com/auth/blogger"]
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

# Inicialização da IA (Versão Estável)
google_ia.configure(api_key=GEMINI_API_KEY)

PROMPT_SISTEMA = """
Você é o redator oficial do blog 'Emagrecer com Saúde'. 
Sua missão: Ajudar pessoas a emagrecer com saúde, informação confiável e hábitos sustentáveis.
Tom de voz: Educativo, Acolhedor, Claro, Sem alarmismo.
Regra de Ouro: 'Orientar com responsabilidade, não vender ilusão'.
ESTRUTURA OBRIGATÓRIA: Introdução empática, Subtítulos H2, Aplicação prática e Conclusão motivadora.
REQUISITO TÉCNICO: Mínimo 600 e máximo 900 palavras. Tipografia: Arial.
"""

def buscar_imagem_pexels(query):
    if not PEXELS_API_KEY: return "https://images.pexels.com/photos/1103970/pexels-photo-1103970.jpeg"
    url = f"https://api.pexels.com/v1/search?query={query}&orientation=landscape&per_page=5"
    headers = {"Authorization": PEXELS_API_KEY}
    try:
        response = requests.get(url, headers=headers).json()
        if response.get('photos'):
            return response['photos'][0]['src']['large2x']
    except: pass
    return "https://images.pexels.com/photos/1103970/pexels-photo-1103970.jpeg"

def executar():
    # 1. Sorteio do Tema
    caminho_temas = "temas.txt"
    if not os.path.exists(caminho_temas): return
    with open(caminho_temas, "r", encoding="utf-8") as f:
        temas = [l.strip() for l in f.readlines() if l.strip()]
    
    tema_escolhido = random.choice(temas)
    print(f"🚀 Iniciando processo para o tema: {tema_escolhido}")

    # 2. Geração de Conteúdo (Usando GenerativeModel estável)
    try:
        model = google_ia.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(f"{PROMPT_SISTEMA}\n\nEscreva sobre: {tema_escolhido}")
        texto_gerado = response.text
    except Exception as e:
        print(f"Erro na IA: {e}")
        return

    # 3. Validação de Tamanho
    contagem = len(texto_gerado.split())
    print(f"Texto gerado com {contagem} palavras.")
    if not (600 <= contagem <= 900):
        print("⚠️ Fora do limite. Abortando."); return

    # 4. Imagens e HTML
    img1 = buscar_imagem_pexels(f"{tema_escolhido} health")
    img2 = buscar_imagem_pexels("wellness lifestyle")

    corpo_html = ""
    for p in texto_gerado.split('\n'):
        if p.strip():
            if (len(p) < 80 and not p.endswith('.')) or p.startswith('#'):
                corpo_html += f"<h2 style='font-family:Arial; font-size:large; text-align:left; color:#2c3e50; margin-top:20px;'>{p.replace('#','')}</h2>"
            else:
                corpo_html += f"<p style='font-family:Arial; font-size:medium; text-align:justify; line-height:1.6;'>{p}</p>"

    html_final = f"""
    <h1 style='font-family:Arial; font-size:x-large; text-align:center;'>{tema_escolhido.upper()}</h1>
    <div style='text-align:center; margin:20px 0;'><img src='{img1}' style='width:100%; aspect-ratio:16/9; object-fit:cover; border-radius:8px;'/></div>
    {corpo_html}
    <div style='text-align:center; margin:20px 0;'><img src='{img2}' style='width:100%; aspect-ratio:16/9; object-fit:cover; border-radius:8px;'/></div>
    {BLOCO_FIXO_FINAL}
    """

    # 5. Publicação
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    service = build("blogger", "v3", credentials=creds)
    service.posts().insert(
        blogId=BLOG_ID,
        body={"title": tema_escolhido.title(), "content": html_final, "labels": ["Saúde", "Bem-Estar"], "status": "LIVE"}
    ).execute()
    print("✅ SUCESSO! Post publicado.")

if __name__ == "__main__":
    executar()
