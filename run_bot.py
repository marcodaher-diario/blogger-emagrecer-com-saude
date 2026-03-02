# -*- coding: utf-8 -*-

import os
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
# GERAR TAGS SEO - GERAL
# ==========================================================

def gerar_tags_seo(titulo, texto):
    stopwords = ["com", "de", "do", "da", "em", "para", "um", "uma", "os", "as", "que", "no", "na", "ao", "aos"]
    conteudo = f"{titulo} {texto[:100]}"
    palavras = re.findall(r'\b\w{4,}\b', conteudo.lower())
    tags = []

    for p in palavras:
        if p not in stopwords and p not in tags:
            tags.append(p.capitalize())
    
    tags_fixas = ["Finanças", "Investimentos", "Marco Daher"]

    for tf in tags_fixas:
        if tf not in tags:
            tags.append(tf)

    resultado = []
    tamanho_atual = 0

    for tag in tags:
        if tamanho_atual + len(tag) + 2 <= 200:
            resultado.append(tag)
            tamanho_atual += len(tag) + 2
        else:
            break

    return resultado


# ==========================================================
# EXECUÇÃO PRINCIPAL - EMAGRECER
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
                "labels": gerar_tags_seo(titulo)
            },
            isDraft=True
        ).execute()

        print("Post de teste criado como rascunho.")
        exit()

    # EXECUÇÃO NORMAL
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
        exit()

    gemini = GeminiEngine()
    imagem_engine = ImageEngine()

    # Rotação inteligente de categoria
    categoria = random.choice(CATEGORIAS_EDITORIAIS)

    # Geração com bloqueio de repetição
    for _ in range(5):
        titulo = gemini.gerar_tema(categoria)
        if not tema_usado_recentemente(titulo):
            break

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
            "labels": gerar_tags_seo(titulo)
        },
        isDraft=False
    ).execute()

    registrar_postagem(data_hoje, horario_escolhido)
    registrar_tema(titulo)

    print("Post publicado com sucesso.")
