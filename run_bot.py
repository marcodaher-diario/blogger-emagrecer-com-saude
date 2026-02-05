import os
import random
import requests
from google import genai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# IMPORTAÇÃO DA ASSINATURA OFICIAL DO SEU ARQUIVO DE CONFIGURAÇÕES
try:
    from configuracoes import BLOCO_FIXO_FINAL
except ImportError:
    BLOCO_FIXO_FINAL = "<p>Assinatura não encontrada no arquivo configuracoes.py</p>"

# CONFIGURAÇÕES DE IDENTIFICAÇÃO E CHAVES
BLOG_ID = "5251820458826857223"
SCOPES = ["https://www.googleapis.com/auth/blogger"]
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

client_gemini = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# DIRETRIZES EDITORIAIS (REGRAS GLOBAIS)
PROMPT_SISTEMA = """
Você é o redator oficial do blog 'Emagrecer com Saúde'.
Sua missão: Ajudar pessoas a emagrecer com saúde, informação confiável e hábitos sustentáveis.
Tom de voz: Educativo, Acolhedor, Claro, Sem alarmismo.
Regra de Ouro: 'Orientar com responsabilidade, não vender ilusão'.

ESTRUTURA OBRIGATÓRIA:
1. Introdução empática.
2. Desenvolvimento com subtítulos claros (H2).
3. Aplicação prática no dia a dia.
4. Erros comuns e orientações seguras.
5. Conclusão motivadora (sem promessas).

REQUISITO TÉCNICO: O texto deve ter entre 600 e 900 palavras.
"""

def buscar_imagem_pexels(query):
    """Busca imagens horizontais (16:9) no Pexels."""
    if not PEXELS_API_KEY:
        return "https://images.pexels.com/photos/1103970/pexels-photo-1103970.jpeg"
    
    url = f"https://api.pexels.com/v1/search?query={query}&orientation=landscape&per_page=5"
    headers = {"Authorization": PEXELS_API_KEY}
    
    try:
        response = requests.get(url, headers=headers).json()
        if response.get('photos'):
            # Retorna a versão 'large2x' para garantir qualidade no Blogger
            return response['photos'][0]['src']['large2x']
    except Exception as e:
        print(f"Erro na busca de imagem: {e}")
    
    return "https://images.pexels.com/photos/1103970/pexels-photo-1103970.jpeg"

def executar():
    # 1. LEITURA DOS TEMAS (VALIDAÇÃO DE ARQUIVO VAZIO)
    caminho_temas = "temas.txt"
    if not os.path.exists(caminho_temas):
        print("Erro: arquivo temas.txt não encontrado."); return
    
    with open(caminho_temas, "r", encoding="utf-8") as f:
        temas = [linha.strip() for linha in f.readlines() if linha.strip()]
    
    if not temas:
        print("Erro: O arquivo temas.txt está vazio."); return
    
    tema_escolhido = random.choice(temas)
    print(f"Assunto selecionado: {tema_escolhido}")

    # 2. GERAÇÃO DO CONTEÚDO VIA IA
    prompt_final = f"{PROMPT_SISTEMA}\n\nEscreva um artigo completo sobre: {tema_escolhido}"
    try:
        response = client_gemini.models.generate_content(
            model="gemini-1.5-flash", 
            contents=prompt_final
        )
        texto_gerado = response.text
    except Exception as e:
        print(f"Erro ao gerar texto: {e}"); return

    # 3. VALIDAÇÃO RIGOROSA: 600-900 PALAVRAS
    contagem_palavras = len(texto_gerado.split())
    if not (600 <= contagem_palavras <= 900):
        print(f"Post REJEITADO: {contagem_palavras} palavras. Fora do limite 600-900."); return

    # 4. BUSCA DE IMAGENS RELACIONADAS (16:9)
    img_topo = buscar_imagem_pexels(f"{tema_escolhido} healthy lifestyle")
    img_meio = buscar_imagem_pexels("nutrition wellness")

    # 5. MONTAGEM DO HTML COM TIPOGRAFIA ARIAL E JUSTIFICADA
    corpo_html = ""
    # Processa cada parágrafo para aplicar o estilo solicitado
    for paragrafo in texto_gerado.split('\n'):
        paragrafo = paragrafo.strip()
        if not paragrafo: continue
        
        # Identifica se é um título (geralmente linhas curtas sem ponto final)
        if (len(paragrafo) < 80 and not paragrafo.endswith('.')) or paragrafo.startswith('#'):
            clean_h2 = paragrafo.replace('#', '').strip()
            corpo_html += f"<h2 style='font-family:Arial; font-size:large; text-align:left; color:#2c3e50; margin-top:20px;'>{clean_h2}</h2>"
        else:
            corpo_html += f"<p style='font-family:Arial; font-size:medium; text-align:justify; line-height:1.6;'>{paragrafo}</p>"

    # MONTAGEM FINAL DO ESQUELETO HTML
    html_final = f"""
    <h1 style='font-family:Arial; font-size:x-large; text-align:center; color:#111;'>{tema_escolhido.upper()}</h1>
    
    <div style='text-align:center; margin:20px 0;'>
        <img src='{img_topo}' style='width:100%; aspect-ratio:16/9; object-fit:cover; border-radius:8px;' />
    </div>

    {corpo_html}

    <div style='text-align:center; margin:20px 0;'>
        <img src='{img_meio}' style='width:100%; aspect-ratio:16/9; object-fit:cover; border-radius:8px;' />
    </div>

    {BLOCO_FIXO_FINAL}
    """

    # 6. PUBLICAÇÃO NO BLOGGER
    try:
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        service = build("blogger", "v3", credentials=creds)
        
        service.posts().insert(
            blogId=BLOG_ID,
            body={
                "title": tema_escolhido.title(),
                "content": html_final,
                "labels": ["Saúde", "Emagrecimento"],
                "status": "LIVE"
            }
        ).execute()
        print(f"✅ Sucesso: '{tema_escolhido}' publicado com {contagem_palavras} palavras e assinatura oficial.")
    except Exception as e:
        print(f"Erro ao publicar no Blogger: {e}")

if __name__ == "__main__":
    executar()
