# =============================================================
# RUN_BOT.PY — BLOGGER BOT (EMAGRECER COM SAÚDE)
# VERSÃO GEMINI 1.5 FLASH
# =============================================================

import feedparser
import re
import os
import time
import random
from datetime import datetime, timedelta
import google.generativeai as genai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# =============================
# CONFIGURAÇÕES GERAIS
# =============================

BLOG_ID = "5251820458826857223"  # EMAGRECER COM SAÚDE
SCOPES = ["https://www.googleapis.com/auth/blogger"]

# --- CONFIGURAÇÃO GEMINI ---
# Substitua pela sua chave ou configure a variável de ambiente
GEMINI_API_KEY = "SUA_API_KEY_AQUI" 
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# RSS APENAS COMO GATILHO
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
# AUTENTICAÇÃO BLOGGER
# =============================

def autenticar_blogger():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    return build("blogger", "v3", credentials=creds)

# =============================
# CONTROLE DE DUPLICAÇÃO
# =============================

def ja_publicado(link):
    if not os.path.exists(ARQUIVO_LOG):
        return False
    with open(ARQUIVO_LOG, "r", encoding="utf-8") as f:
        return link in f.read()

def registrar_publicacao(link):
    with open(ARQUIVO_LOG, "a", encoding="utf-8") as f:
        f.write(link + "\n")

# =============================
# TAGS — LIMITE 200 CARACTERES
# =============================

def gerar_tags_blogger(texto, limite=200):
    palavras = re.findall(r'\w+', texto.lower())
    ignorar = {
        "a","o","as","os","um","uma","de","do","da","dos","das",
        "em","no","na","nos","nas","para","com","e","ou","que"
    }

    tags = []
    total = 0

    for p in palavras:
        if p in ignorar or len(p) < 3 or p in tags:
            continue
        if total + len(p) + 2 > limite:
            break
        tags.append(p.capitalize())
        total += len(p) + 2

    return tags

# =============================
# EXTRAÇÃO DE IMAGEM
# =============================

def extrair_imagem(entry):
    if hasattr(entry, "media_content"):
        return entry.media_content[0].get("url")
    if hasattr(entry, "media_thumbnail"):
        return entry.media_thumbnail[0].get("url")

    resumo = entry.get("summary", "")
    match = re.search(r'<img[^>]+src="([^">]+)"', resumo)
    return match.group(1) if match else None

# =============================
# TEXTO VIA GEMINI (CONTEÚDO FINAL)
# =============================

def gerar_texto_ia(titulo):
    prompt = (
        "Você é um redator especializado em saúde e emagrecimento. "
        "Escreva um artigo educativo, responsável, claro e profissional, "
        f"com no mínimo 600 e no máximo 900 palavras sobre o tema: {titulo}. "
        "Não use Markdown excessivo, mantenha o foco em parágrafos bem estruturados."
    )
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Erro ao gerar texto com Gemini: {e}")
        return None

# =============================
# FORMATAÇÃO HTML
# =============================

def formatar_texto(texto):
    if not texto: return ""
    # Divide o texto em blocos de frases para criar parágrafos
    frases = re.split(r'(?<=[.!?])\s+', texto)
    blocos = []
    temp = []
    
    for frase in frases:
        temp.append(frase)
        if len(temp) >= 2:
            blocos.append(" ".join(temp))
            temp = []

    if temp:
        blocos.append(" ".join(temp))

    return "".join(
        f"<p style='text-align:justify; font-size: medium; line-height:1.6;'>{b}</p>"
        for b in blocos
    )

# =============================
# ASSINATURA (INTACTA)
# =============================

def gerar_assinatura():
    return """<hr />
<p style="text-align:center; font-weight:bold;">
O conhecimento é o combustível para o Sucesso. Não pesa e não ocupa espaço.
</p>
<p style="text-align:right; font-size:12px;">
Por: Marco Daher<br/>
© Marco Daher 2026
</p>
"""

# =============================
# BUSCA DE NOTÍCIAS (GATILHO)
# =============================

def noticia_recente(entry, horas=72):
    data = entry.get("published_parsed") or entry.get("updated_parsed")
    if not data:
        return False
    return datetime.fromtimestamp(time.mktime(data)) >= datetime.now() - timedelta(hours=horas)

def buscar_gatilho():
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            titulo = entry.get("title", "").strip()
            link = entry.get("link", "").strip()

            if not titulo or not link or ja_publicado(link):
                continue

            if noticia_recente(entry):
                # Tenta pegar a imagem do RSS se disponível
                imagem_rss = extrair_imagem(entry)
                return titulo, link, imagem_rss

    return None, None, None

# =============================
# GERAÇÃO DO HTML FINAL
# =============================

def gerar_html(titulo, texto, imagem):
    return f"""
<h2 style="text-align:center;">{titulo}</h2>

<div style="text-align:center; margin:20px 0;">
<img src="{imagem}" style="max-width:100%; border-radius: 8px;" />
</div>

{formatar_texto(texto)}

{gerar_assinatura()}
"""

# =============================
# EXECUÇÃO
# =============================

def executar():
    service = autenticar_blogger()

    titulo, link, imagem_rss = buscar_gatilho()
    if not titulo:
        print("Nenhum gatilho novo encontrado.")
        return

    print("PUBLICANDO NO BLOG_ID:", BLOG_ID)

    texto = gerar_texto_ia(titulo)
    if not texto:
        print("Falha ao gerar conteúdo.")
        return

    # Usa a imagem do RSS, se não tiver, usa o Fallback
    imagem = imagem_rss if imagem_rss else IMAGEM_FALLBACK

    html = gerar_html(titulo, texto, imagem)

    service.posts().insert(
        blogId=BLOG_ID,
        body={
            "title": titulo,
            "content": html,
            "labels": gerar_tags_blogger(titulo),
            "status": "LIVE"
        }
    ).execute()

    registrar_publicacao(link)
    print("✅ Publicado com sucesso:", titulo)

if __name__ == "__main__":
    executar()
