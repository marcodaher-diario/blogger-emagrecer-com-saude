# -*- coding: utf-8 -*-

import os
import re
import random
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from configuracoes import (
    BLOG_ID,
    AGENDA_POSTAGENS,
    JANELA_MINUTOS,
    CATEGORIAS_EDITORIAIS,
    ARQUIVO_CONTROLE_AGENDAMENTO,
    ARQUIVO_CONTROLE_TEMAS,
    DIAS_BLOQUEIO_TEMA,
    BLOCO_FIXO_FINAL
)

from gemini_engine import GeminiEngine
from imagem_engine import ImageEngine
from template_blog import obter_esqueleto_html


# ==========================================================
# UTILIDADES DE TEMPO - EMAGRECER
# ==========================================================

def obter_horario_brasilia():
    return datetime.utcnow() - timedelta(hours=3)


def horario_para_minutos(hhmm):
    h, m = map(int, hhmm.split(":"))
    return h * 60 + m


def dentro_da_janela(min_atual, min_agenda):
    return abs(min_atual - min_agenda) <= JANELA_MINUTOS


# ==========================================================
# CONTROLE DE AGENDAMENTO - EMAGRECER
# ==========================================================

def ja_postou(data_str, horario):
    if not os.path.exists(ARQUIVO_CONTROLE_AGENDAMENTO):
        return False

    with open(ARQUIVO_CONTROLE_AGENDAMENTO, "r", encoding="utf-8") as f:
        for linha in f:
            data, hora = linha.strip().split("|")
            if data == data_str and hora == horario:
                return True
    return False


def registrar_postagem(data_str, horario):
    with open(ARQUIVO_CONTROLE_AGENDAMENTO, "a", encoding="utf-8") as f:
        f.write(f"{data_str}|{horario}\n")


# ==========================================================
# CONTROLE DE TEMA - EMAGRECER
# ==========================================================

def tema_usado_recentemente(titulo):

    if not os.path.exists(ARQUIVO_CONTROLE_TEMAS):
        return False

    hoje = datetime.utcnow()

    with open(ARQUIVO_CONTROLE_TEMAS, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if "|" not in linha:
                continue

            data_str, titulo_salvo = linha.split("|")

            try:
                data_tema = datetime.strptime(data_str, "%Y-%m-%d")
            except:
                continue

            if titulo_salvo.lower() == titulo.lower() and (hoje - data_tema).days < DIAS_BLOQUEIO_TEMA:
                return True

    return False


def registrar_tema(titulo):
    hoje = datetime.utcnow().strftime("%Y-%m-%d")

    with open(ARQUIVO_CONTROLE_TEMAS, "a", encoding="utf-8") as f:
        f.write(f"{hoje}|{titulo}\n")


# ==========================================================
# GERAR TAGS SEO - SISTEMA DE CLUSTERS
# ==========================================================

def gerar_tags_seo(titulo, texto):

    stopwords = [
        "com","como","para","porque","sobre","entre","de","do","da",
        "dos","das","em","um","uma","os","as","que","no","na","ao",
        "aos","por","mais","menos","ser","estar","ter","se","sua",
        "seu","suas","seus","também","muito","muitos","muitas"
    ]

    # ======================================================
    # CLUSTERS PRINCIPAIS DO BLOG
    # ======================================================

    clusters = {
        "emagrecimento": [
            "emagrecer","emagrecimento","perder peso","gordura","calorias"
        ],
        "metabolismo": [
            "metabolismo","termogênese","termogenese","metabólico","metabolico"
        ],
        "nutrição": [
            "nutrição","nutricao","proteína","proteina","vitaminas","nutrientes"
        ],
        "exercícios": [
            "exercício","exercicio","atividade","treino","movimentos"
        ],
        "dietas": [
            "dieta","dietas","jejum","jejum intermitente","alimentação"
        ],
        "saúde metabólica": [
            "insulina","diabetes","colesterol","pressão","pressao"
        ]
    }

    # ======================================================
    # ENTIDADES IMPORTANTES DO NICHO
    # ======================================================

    entidades_saude = {
        "metabolismo": "Metabolismo",
        "calorias": "Calorias",
        "insulina": "Insulina",
        "diabetes": "Diabetes",
        "colesterol": "Colesterol",
        "pressão": "Pressão Arterial",
        "pressao": "Pressão Arterial",
        "sedentarismo": "Sedentarismo",
        "termogênese": "Termogênese",
        "termogenese": "Termogênese"
    }

    # ======================================================
    # PALAVRAS DO TÍTULO
    # ======================================================

    palavras_titulo = re.findall(r'\b[a-zà-ÿ]{4,}\b', titulo.lower())

    # ======================================================
    # PALAVRAS DO TEXTO
    # ======================================================

    conteudo = f"{titulo} {texto[:200]}"
    palavras_texto = re.findall(r'\b[a-zà-ÿ]{4,}\b', conteudo.lower())

    texto_total = conteudo.lower()

    tags = []

    # ======================================================
    # TAGS DO TÍTULO (PRIORIDADE)
    # ======================================================

    for p in palavras_titulo:
        if p not in stopwords and p.capitalize() not in tags:
            tags.append(p.capitalize())

    # ======================================================
    # TAGS DO TEXTO
    # ======================================================

    for p in palavras_texto:
        if p not in stopwords and p.capitalize() not in tags:
            tags.append(p.capitalize())

    # ======================================================
    # DETECÇÃO DE ENTIDADES
    # ======================================================

    for chave, entidade in entidades_saude.items():
        if chave in texto_total and entidade not in tags:
            tags.append(entidade)

    # ======================================================
    # DETECÇÃO DE CLUSTERS
    # ======================================================

    for cluster, palavras in clusters.items():
        for palavra in palavras:
            if palavra in texto_total:
                cluster_formatado = cluster.capitalize()
                if cluster_formatado not in tags:
                    tags.append(cluster_formatado)
                break

    # ======================================================
    # TAGS FIXAS DO BLOG
    # ======================================================

    tags_fixas = [
        "Emagrecimento",
        "Saúde"
    ]

    for tf in tags_fixas:
        if tf not in tags:
            tags.append(tf)

   # ======================================================
    # LIMITADOR DE 200 CARACTERES
    # ======================================================
    
    resultado = []
    tamanho_atual = 0
    
    for tag in tags:
    
        # evita palavras muito curtas ou ruins
        if len(tag) < 4:
            continue
    
        tamanho_tag = len(tag)
    
        if tamanho_atual + tamanho_tag + 2 <= 200:
            resultado.append(tag)
            tamanho_atual += tamanho_tag + 2
        else:
            break
    
    # limite adicional de segurança
    resultado = resultado[:15]
    
    return resultado

# ==========================================================
# MODO TESTE - EMAGRECER
# ==========================================================

if __name__ == "__main__":

    # MODO TESTE
    if os.getenv("TEST_MODE") == "true":

        print("=== MODO TESTE ATIVADO ===")

        categoria = random.choice(CATEGORIAS_EDITORIAIS)

        gemini = GeminiEngine()
        imagem_engine = ImageEngine()

        titulo = gemini.gerar_tema(categoria)
        texto = gemini.gerar_artigo(titulo, categoria)
        imagem = imagem_engine.obter_imagem(titulo)

        html = obter_esqueleto_html({
            "titulo": titulo,
            "imagem": imagem,
            "texto_completo": texto,
            "assinatura": BLOCO_FIXO_FINAL
        })

        service = Credentials.from_authorized_user_file("token.json")
        service = build("blogger", "v3", credentials=service)

        service.posts().insert(
            blogId=BLOG_ID,
            body={
                "title": titulo,
                "content": html,
                "labels": gerar_tags_seo(titulo, texto)
            },
            isDraft=True
        ).execute()

        registrar_tema(titulo)
        
        print("Post de teste criado como rascunho.")
        exit()
        
# ==========================================================
# EXECUÇÃO PRINCIPAL - EMAGRECER
# ==========================================================
    
    agora = obter_horario_brasilia()
    min_atual = agora.hour * 60 + agora.minute
    data_hoje = agora.strftime("%Y-%m-%d")

    horario_escolhido = None

    for horario_agenda in AGENDA_POSTAGENS:

        min_agenda = horario_para_minutos(horario_agenda)

        if dentro_da_janela(min_atual, min_agenda):
            if not ja_postou(data_hoje, horario_agenda):
                horario_escolhido = horario_agenda
                break

        if not horario_escolhido:

            if os.getenv("FORCAR_POSTAGEM") == "true":
                print("Fora da janela, mas FORÇANDO postagem...")
                horario_escolhido = "FORCADO"
            else:
                print("Fora da janela de postagem. Nenhuma ação realizada.")
                exit()

    gemini = GeminiEngine()
    imagem_engine = ImageEngine()

    # Rotação inteligente de categoria
    categoria = random.choice(CATEGORIAS_EDITORIAIS)

    # Geração com bloqueio de repetição
    titulo = None

    for _ in range(5):
        tentativa = gemini.gerar_tema(categoria)
        if not tema_usado_recentemente(tentativa):
            titulo = tentativa
            break
    
    if not titulo:
        print("Nenhum tema novo encontrado, abortando para evitar repetição.")
        exit()
        
    texto = gemini.gerar_artigo(titulo, categoria)
    imagem = imagem_engine.obter_imagem(titulo)

    html = obter_esqueleto_html({
        "titulo": titulo,
        "imagem": imagem,
        "texto_completo": texto,
        "assinatura": BLOCO_FIXO_FINAL
    })

    service = Credentials.from_authorized_user_file("token.json")
    service = build("blogger", "v3", credentials=service)

    service.posts().insert(
        blogId=BLOG_ID,
        body={
            "title": titulo,
            "content": html,
            "labels": gerar_tags_seo(titulo, texto)
        },
        isDraft=False
    ).execute()

    registrar_postagem(data_hoje, horario_escolhido)
    registrar_tema(titulo)

    print("Post publicado com sucesso.")
