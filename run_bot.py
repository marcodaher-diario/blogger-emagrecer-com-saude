# =============================================================
# RUN_BOT.PY — BLOGGER BOT (EMAGRECER COM SAÚDE)
# VERSÃO ATUALIZADA 2026 - GEMINI API
# =============================================================

import os
import feedparser
import re
import time
from datetime import datetime, timedelta

# Importação da nova biblioteca do Google
try:
    from google import genai
except ImportError:
    print("ERRO: A biblioteca 'google-genai' não está instalada.")

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# =============================
# CONFIGURAÇÕES GERAIS
# =============================

BLOG_ID = "5251820458826857223"
SCOPES = ["https://www.googleapis.com/auth/blogger"]

# BUSCA A CHAVE QUE VOCÊ CADASTROU NO GITHUB SECRETS
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Inicializa o cliente do Gemini
client_gemini = None
if GEMINI_API_KEY:
    client_gemini = genai.Client(api_key=GEMINI_API_KEY)
else:
    print("AVISO: Variável GEMINI_API_KEY não encontrada. Verifique os Secrets do GitHub.")

# Canais de notícias para monitorar
RSS_FEEDS = [
    "https://g1.globo.com/bemestar/rss/g1/",
    "https://saude.abril.com.br/feed/",
    "https://www.tuasaude.com/feed/",
    "https://www.minhavida.com.br/rss",
    "https://www.bbc.com/portuguese/topics/cyx5krnw38vt/rss.xml"
]

IMAGEM_FALLBACK = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/News_icon.svg/800px-News_icon.svg.png"
ARQUIVO_LOG = "posts_publicados.txt"

# =============================
# AUTENTICAÇÃO E CONTROLE
# =============================

def autenticar_blogger():
    # Carrega o token.json que você já possui no repositório
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    return build("blogger", "v3", credentials=creds)

def ja_publicado(link):
    if not os.path.exists(ARQUIVO_LOG):
        return False
    with open(ARQUIVO_LOG, "r", encoding="utf-8") as f:
        return link in f.read()

def registrar_publicacao(link):
    with open(ARQUIVO_LOG, "a", encoding="utf-8") as f:
        f.write(link + "\n")

# =============================
# GERAÇÃO DE CONTEÚDO (IA)
# =============================

def gerar_texto_ia(titulo):
    if not client_gemini:
        print("Erro: Cliente Gemini não configurado.")
        return None
    
    # Prompt otimizado para posts de blog
    prompt = (
        "Você é um redator especializado em saúde e emagrecimento. "
        f"Escreva um artigo educativo e profissional sobre: {titulo}. "
        "O texto deve ter entre 600 e 900 palavras. "
        "Use parágrafos claros e uma linguagem motivadora."
    )
    
    try:
        # Chamada oficial da biblioteca moderna
        response = client_gemini.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"Erro ao gerar texto com a IA: {e}")
        return None

# =============================
# FORMATAÇÃO E IMAGENS
# =============================

def extrair_imagem(entry):
    if hasattr(entry, "media_content"):
        return entry.media_content[0].get("url")
    if hasattr(entry, "media_thumbnail"):
        return entry.media_thumbnail[0].get("url")
    resumo = entry.get("summary", "")
    match = re.search(r'<img[^>]+src="([^">]+)"', resumo)
    return match.group(1) if match else None

def formatar_texto_html(texto):
    if not texto: return ""
    # Transforma quebras de linha em parágrafos HTML justificativos
    paragrafos = texto.split('\n')
    html_final = ""
    for p in paragrafos:
        if p.strip():
            html_final += f"<p style='text-align:justify; font-size: medium; line-height:1.6;'>{p.strip()}</p>"
    return html_final

def gerar_assinatura():
    return """<hr /><p style="text-align:center; font-weight:bold;">
    O conhecimento é o combustível para o Sucesso. Não pesa e não ocupa espaço.</p>
    <p style="text-align:right; font-size:12px;">Por: Marco Daher<br/>© Marco Daher 2026</p>"""

# =============================
# BUSCA DE GATILHOS (NOTÍCIAS)
# =============================

def noticia_recente(entry, horas=72):
    data = entry.get("published_parsed") or entry.get("updated_parsed")
    if not data: return False
    return datetime.fromtimestamp(time.mktime(data)) >= datetime.now() - timedelta(hours=horas)

def buscar_novo_tema():
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            titulo = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            if not titulo or not link or ja_publicado(link):
                continue
            if noticia_recente(entry):
                return titulo, link, extrair_imagem(entry)
    return None, None, None

# =============================
# FUNÇÃO PRINCIPAL
# =============================

def executar():
    print("Iniciando Bot Emagrecer com Saúde...")
    
    # 1. Autentica no Blogger
    try:
        service = autenticar_blogger()
    except Exception as e:
        print(f"Erro na autenticação do Blogger: {e}")
        return

    # 2. Busca nova notícia como tema
    titulo, link, imagem_rss = buscar_novo_tema()
    if not titulo:
        print("Nenhuma notícia nova encontrada nos feeds.")
        return

    print(f"Novo tema encontrado: {titulo}")

    # 3. Gera o texto com o Gemini
    texto_artigo = gerar_texto_ia(titulo)
    if not texto_artigo:
        print("Falha ao gerar o conteúdo do post.")
        return

    # 4. Monta o HTML final
    imagem_final = imagem_rss if imagem_rss else IMAGEM_FALLBACK
    conteudo_html = f"""
    <h2 style="text-align:center;">{titulo}</h2>
    <div style="text-align:center; margin:20px 0;">
        <img src="{imagem_final}" style="max-width:100%; border-radius: 8px;" />
    </div>
    {formatar_texto_html(texto_artigo)}
    {gerar_assinatura()}
    """

    # 5. Publica no Blogger
    try:
        service.posts().insert(
            blogId=BLOG_ID,
            body={
                "title": titulo,
                "content": conteudo_html,
                "labels": ["Saúde", "Bem Estar", "Emagrecimento"],
                "status": "LIVE"
            }
        ).execute()
        
        registrar_publicacao(link)
        print(f"✅ Post publicado com sucesso: {titulo}")
    except Exception as e:
        print(f"Erro ao publicar no Blogger: {e}")

if __name__ == "__main__":
    executar()
