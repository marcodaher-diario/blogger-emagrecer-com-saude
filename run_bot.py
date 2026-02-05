import os
import random
import requests
from google import genai
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

# Inicialização do Cliente Gemini
client_gemini = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

PROMPT_SISTEMA = """
Você é o redator oficial do blog 'Emagrecer com Saúde'. 
Missão: Ajudar pessoas a emagrecer com saúde e hábitos sustentáveis.
Tom de voz: Educativo, Acolhedor, Claro, Sem alarmismo.
Regra de Ouro: 'Orientar com responsabilidade, não vender ilusão'.
ESTRUTURA OBRIGATÓRIA:
1. Introdução empática.
2. Desenvolvimento com subtítulos H2.
3. Aplicação prática no dia a dia.
4. Erros comuns e orientações seguras.
5. Conclusão motivadora.
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
    if not os.path.exists(caminho_temas):
        print("Erro: temas.txt não encontrado."); return
    with open(caminho_temas, "r", encoding="utf-8") as f:
        temas = [l.strip() for l in f.readlines() if l.strip()]
    if not temas:
        print("Erro: temas.txt vazio."); return
    
    tema_escolhido = random.choice(temas)
    print(f"🚀 Iniciando processo para o tema: {tema_escolhido}")

    # 2. Geração de Conteúdo (Tratamento de erro 404)
    texto_gerado = None
    modelos = ["gemini-1.5-flash", "models/gemini-1.5-flash"]
    
    for mod in modelos:
        try:
            print(f"Tentando gerar texto com {mod}...")
            response = client_gemini.models.generate_content(
                model=mod,
                contents=f"{PROMPT_SISTEMA}\n\nEscreva um artigo detalhado sobre: {tema_escolhido}"
            )
            texto_gerado = response.text
            if texto_gerado: break
        except Exception as e:
            print(f"Falha no modelo {mod}: {e}")

    if not texto_gerado:
        print("❌ Não foi possível gerar o conteúdo."); return

    # 3. Validação de Tamanho
    contagem = len(texto_gerado.split())
    print(f"Texto gerado com {contagem} palavras.")
    if not (600 <= contagem <= 900):
        print("⚠️ Fora do limite (600-900). Abortando publicação."); return

    # 4. Imagens e HTML
    img1 = buscar_imagem_pexels(f"{tema_escolhido} health")
    img2 = buscar_imagem_pexels("wellness lifestyle")

    corpo_html = ""
    for p in texto_gerado.split('\n'):
        if p.strip():
            # Formatação de H2 e Parágrafos em Arial Justificado
            if (len(p) < 80 and not p.endswith('.')) or p.startswith('#'):
                corpo_html += f"<h2 style='font-family:Arial; font-size:large; text-align:left; color:#2c3e50; margin-top:20px;'>{p.replace('#','')}</h2>"
            else:
                corpo_html += f"<p style='font-family:Arial; font-size:medium; text-align:justify; line-height:1.6;'>{p}</p>"

    html_final = f"""
    <h1 style='font-family:Arial; font-size:x-large; text-align:center; color:#111;'>{tema_escolhido.upper()}</h1>
    <div style='text-align:center; margin:20px 0;'><img src='{img1}' style='width:100%; aspect-ratio:16/9; object-fit:cover; border-radius:8px;'/></div>
    {corpo_html}
    <div style='text-align:center; margin:20px 0;'><img src='{img2}' style='width:100%; aspect-ratio:16/9; object-fit:cover; border-radius:8px;'/></div>
    {BLOCO_FIXO_FINAL}
    """

    # 5. Publicação no Blogger
    try:
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        service = build("blogger", "v3", credentials=creds)
        service.posts().insert(
            blogId=BLOG_ID,
            body={"title": tema_escolhido.title(), "content": html_final, "labels": ["Saúde", "Bem-Estar"], "status": "LIVE"}
        ).execute()
        print(f"✅ SUCESSO! Post '{tema_escolhido}' publicado no blog.")
    except Exception as e:
        print(f"Erro na publicação: {e}")

if __name__ == "__main__":
    executar()
