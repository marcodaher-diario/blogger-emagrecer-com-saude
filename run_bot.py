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
try:
    from template_blog import obter_esqueleto_html
except ImportError:
    print("❌ Erro: Arquivo template_blog.py não encontrado!")
    
try:
    from configuracoes import BLOCO_FIXO_FINAL
except ImportError:
    BLOCO_FIXO_FINAL = ""

# CONFIGURAÇÕES DE IDENTIFICAÇÃO
BLOG_ID = "5251820458826857223"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

def gerar_tags_seo(titulo, texto_completo):
    """Gera labels inteligentes para o Blogger e insere a marca Marco Daher."""
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
    """Valida o acesso ao Blogger usando o Refresh Token."""
    with open("token.json", "r") as f:
        info = json.load(f)
    creds = Credentials.from_authorized_user_info(info, ["https://www.googleapis.com/auth/blogger"])
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open("token.json", "w") as f:
            f.write(creds.to_json())
    return creds

def buscar_fotos_aleatorias(tema, quantidade=2):
    """Pool de 15 fotos para evitar repetições próximas."""
    url = f"https://api.pexels.com/v1/search?query={tema}&orientation=landscape&per_page=15"
    headers = {"Authorization": PEXELS_API_KEY}
    pool_fotos = []
    try:
        r = requests.get(url, headers=headers).json()
        for foto in r.get('photos', []):
            pool_fotos.append(foto['src']['large2x'])
    except: pass
    
    # CORREÇÃO: random.sample usa o argumento 'k' e não 'quantity'
    if len(pool_fotos) >= quantidade:
        return random.sample(pool_fotos, k=quantidade)
    return ["https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg"] * quantidade

def executar():
    with open("temas.txt", "r", encoding="utf-8") as f:
        temas = [l.strip() for l in f.readlines() if l.strip()]
    
    tema = random.choice(temas)
    print(f"🚀 Produzindo Artigo Longo e SEO: {tema}")

    prompt_json = (
        f"Aja como um redator especialista. Escreva um artigo PROFUNDO de 800 palavras sobre {tema}.\n"
        "Responda EXCLUSIVAMENTE em formato JSON com estas chaves:\n"
        "'intro', 'sub1', 'texto1', 'sub2', 'texto2', 'sub3', 'texto3', 'texto_conclusao'.\n"
        "Não use Markdown, não use '#', use tom educativo e profissional."
    )

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview", 
            contents=prompt_json,
            config={'response_mime_type': 'application/json'}
        )
        
        # Garante que 'conteudo' seja um dicionário, mesmo que venha em lista
        res_data = json.loads(response.text)
        conteudo = res_data[0] if isinstance(res_data, list) else res_data

    except Exception as e:
        print(f"Erro na geração ou leitura do JSON: {e}")
        return

    # Geração de SEO e Busca de Imagens
    texto_total = f"{conteudo.get('intro','')} {conteudo.get('texto1','')} {conteudo.get('texto2','')}"
    tags_geradas = gerar_tags_seo(tema, texto_total)
    fotos = buscar_fotos_aleatorias(tema)

    # Organização dos dados para o Template_blog.py
    dados_post = {
        'titulo': tema,
        'img_topo': fotos[0],
        'img_meio': fotos[1],
        'intro': conteudo.get('intro', '').replace('\n', '<br/>'),
        'sub1': conteudo.get('sub1', 'Destaque'),
        'texto1': conteudo.get('texto1', '').replace('\n', '<br/>'),
        'sub2': conteudo.get('sub2', 'Saiba Mais'),
        'texto2': conteudo.get('texto2', '').replace('\n', '<br/>'),
        'sub3': conteudo.get('sub3', 'Dica Prática'),
        'texto3': conteudo.get('texto3', '').replace('\n', '<br/>'),
        'texto_conclusao': conteudo.get('texto_conclusao', '').replace('\n', '<br/>'),
        'assinatura': BLOCO_FIXO_FINAL
    }

    html_final = obter_esqueleto_html(dados_post)

    # PUBLICAÇÃO NO BLOGGER
    try:
        creds = renovar_token()
        service = build("blogger", "v3", credentials=creds)
        
        corpo_post = {
            "kind": "blogger#post",
            "title": tema.title(),
            "content": html_final,
            "labels": tags_geradas,
            "status": "LIVE"
        }
        
        service.posts().insert(blogId=BLOG_ID, body=corpo_post).execute()
        print(f"✅ SUCESSO! Post publicado com {len(tags_geradas)} labels.")
    except Exception as e:
        print(f"❌ Erro ao publicar no Blogger: {e}")

if __name__ == "__main__":
    executar()
