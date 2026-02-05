import os
import random
import requests
import json
import re
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

# CONFIGURAÇÕES (MD Emagreca ...tRBY)
BLOG_ID = "5251820458826857223"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

def gerar_tags_seo(titulo, texto_completo):
    """Gera tags inteligentes e insere a marca Marco Daher."""
    stopwords = ["com", "de", "do", "da", "em", "para", "um", "uma", "os", "as", "que", "no", "na", "ao", "aos", "o", "a", "e"]
    conteudo = f"{titulo} {texto_completo[:300]}"
    palavras = re.findall(r'\b\w{4,}\b', conteudo.lower())
    tags = []
    for p in palavras:
        if p not in stopwords and p not in tags:
            tags.append(p.capitalize())
    
    tags_fixas = ["Emagrecer", "Saúde", "Marco Daher"]
    for tf in tags_fixas:
        if tf not in tags: tags.append(tf)
    
    resultado = []
    tamanho_atual = 0
    for tag in tags:
        if tamanho_atual + len(tag) + 2 <= 200:
            resultado.append(tag)
            tamanho_atual += len(tag) + 2
        else: break
    return resultado

def renovar_token():
    with open("token.json", "r") as f:
        info = json.load(f)
    creds = Credentials.from_authorized_user_info(info, ["https://www.googleapis.com/auth/blogger"])
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open("token.json", "w") as f:
            f.write(creds.to_json())
    return creds

def buscar_fotos_aleatórias(tema, quantidade=2):
    """Pool de 15 fotos para evitar repetições próximas."""
    url = f"https://api.pexels.com/v1/search?query={tema}&orientation=landscape&per_page=15"
    headers = {"Authorization": PEXELS_API_KEY}
    pool_fotos = []
    try:
        r = requests.get(url, headers=headers).json()
        for foto in r.get('photos', []):
            pool_fotos.append(foto['src']['large2x'])
    except: pass
    if len(pool_fotos) >= quantidade:
        return random.sample(pool_fotos, quantidade)
    return ["https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg"] * quantidade

def executar():
    with open("temas.txt", "r", encoding="utf-8") as f:
        temas = [l.strip() for l in f.readlines() if l.strip()]
    
    tema = random.choice(temas)
    print(f"🚀 Produzindo Artigo Longo (800+ palavras): {tema}")

    # PROMPT MODULAR PARA TEXTO LONGO
    prompt_json = (
        f"Aja como um redator especialista. Escreva um artigo PROFUNDO de 800 palavras sobre {tema}.\n"
        "Responda EXCLUSIVAMENTE em formato JSON com estas chaves e tamanhos:\n"
        "- 'intro': 2 parágrafos detalhados (150 palavras).\n"
        "- 'sub1', 'sub2', 'sub3': Títulos impactantes.\n"
        "- 'texto1', 'texto2', 'texto3': 3 parágrafos robustos por bloco (200 palavras cada).\n"
        "- 'texto_conclusao': Fechamento inspirador (100 palavras).\n"
        "REGRAS: Tom educativo, sem Markdown (#), foco em vida saudável."
    )

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview", 
            contents=prompt_json,
            config={'response_mime_type': 'application/json'}
        )
        conteudo = json.loads(response.text)
    except Exception as e:
        print(f"Erro na geração: {e}")
        return

    # Processamento de SEO e Imagens
    texto_total = f"{conteudo['intro']} {conteudo['texto1']} {conteudo['texto2']} {conteudo['texto3']}"
    tags_geradas = gerar_tags_seo(tema, texto_total)
    fotos = buscar_fotos_aleatórias(tema)

    # Preparação para o Template
    dados_post = {
        'titulo': tema,
        'img_topo': fotos[0],
        'img_meio': fotos[1],
        'intro': conteudo['intro'].replace('\n', '<br/>'),
        'sub1': conteudo['sub1'],
        'texto1': conteudo['texto1'].replace('\n', '<br/>'),
        'sub2': conteudo['sub2'],
        'texto2': conteudo['texto2'].replace('\n', '<br/>'),
        'sub3': conteudo['sub3'],
        'texto3': conteudo['texto3'].replace('\n', '<br/>'),
        'texto_conclusao': conteudo['texto_conclusao'].replace('\n', '<br/>'),
        'assinatura': BLOCO_FIXO_FINAL
    }

    html_final = obter_esqueleto_html(dados_post)

    # PUBLICAÇÃO
    try:
        creds = renovar_token()
        service = build("blogger", "v3", credentials=creds)
        service.posts().insert(
            blogId=BLOG_ID, 
            body={
                "title": tema.title(),
                "content": html_final,
                "labels": tags_geradas,
                "status": "LIVE"
            }
        ).execute()
        print(f"✅ SUCESSO! Artigo completo publicado com {len(tags_geradas)} tags.")
    except Exception as e:
        print(f"❌ Erro ao publicar: {e}")

if __name__ == "__main__":
    executar()
