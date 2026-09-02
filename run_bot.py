# -*- coding: utf-8 -*-

import os
import re
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

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
# CONFIGURAÇÕES LOCAIS
# ==========================================================

FUSO_BRASILIA = ZoneInfo("America/Sao_Paulo")

# Aumenta a janela de postagem.
#
# Pode ser alterada pelo GitHub Actions através da variável:
#
# JANELA_POSTAGEM_MINUTOS
#
# Exemplo:
# JANELA_POSTAGEM_MINUTOS = 90
#
# Se não existir, usamos 90 minutos como padrão.
#
# O valor configurado no ambiente terá prioridade.
#
try:
    JANELA_POSTAGEM = int(
        os.getenv(
            "JANELA_POSTAGEM_MINUTOS",
            str(max(JANELA_MINUTOS, 90))
        )
    )
except ValueError:
    JANELA_POSTAGEM = max(JANELA_MINUTOS, 90)


# ==========================================================
# UTILIDADES DE TEMPO
# ==========================================================

def obter_horario_brasilia():
    """
    Retorna data e hora atuais no horário de Brasília.
    """
    return datetime.now(FUSO_BRASILIA)


def horario_para_minutos(hhmm):
    """
    Converte HH:MM para minutos desde meia-noite.
    """
    h, m = map(int, hhmm.split(":"))
    return h * 60 + m


def diferenca_circular_minutos(min_atual, min_agenda):
    """
    Calcula a menor distância entre dois horários considerando
    a virada da meia-noite.

    Exemplo:

    23:50 -> 00:10 = 20 minutos

    em vez de considerar 23h40 de diferença.
    """

    diferenca = abs(min_atual - min_agenda)

    return min(
        diferenca,
        1440 - diferenca
    )


def dentro_da_janela(min_atual, min_agenda):
    """
    Verifica se o horário atual está dentro da janela permitida.
    """
    return (
        diferenca_circular_minutos(
            min_atual,
            min_agenda
        )
        <= JANELA_POSTAGEM
    )


# ==========================================================
# CONTROLE DE AGENDAMENTO
# ==========================================================

def ja_postou(data_str, horario):
    """
    Verifica se determinado horário já foi utilizado naquele dia.
    """

    if not os.path.exists(ARQUIVO_CONTROLE_AGENDAMENTO):
        return False

    with open(
        ARQUIVO_CONTROLE_AGENDAMENTO,
        "r",
        encoding="utf-8"
    ) as f:

        for linha in f:

            linha = linha.strip()

            if "|" not in linha:
                continue

            partes = linha.split("|", 1)

            if len(partes) != 2:
                continue

            data, hora = partes

            if data == data_str and hora == horario:
                return True

    return False


def registrar_postagem(data_str, horario):
    """
    Registra a postagem realizada.
    """

    with open(
        ARQUIVO_CONTROLE_AGENDAMENTO,
        "a",
        encoding="utf-8"
    ) as f:

        f.write(
            f"{data_str}|{horario}\n"
        )


# ==========================================================
# LOCALIZAR HORÁRIO DE POSTAGEM
# ==========================================================

def encontrar_horario_disponivel(agora):
    """
    Procura todos os horários da agenda que estejam dentro
    da janela de postagem.

    Em vez de parar no primeiro horário fora da janela,
    verifica toda a agenda e escolhe o horário mais próximo.
    """

    min_atual = agora.hour * 60 + agora.minute
    data_hoje = agora.strftime("%Y-%m-%d")

    horarios_validos = []

    for horario_agenda in AGENDA_POSTAGENS:

        try:
            min_agenda = horario_para_minutos(
                horario_agenda
            )
        except (ValueError, TypeError):
            print(
                f"Horário inválido ignorado: {horario_agenda}"
            )
            continue

        if ja_postou(
            data_hoje,
            horario_agenda
        ):
            continue

        distancia = diferenca_circular_minutos(
            min_atual,
            min_agenda
        )

        if distancia <= JANELA_POSTAGEM:

            horarios_validos.append(
                (
                    distancia,
                    horario_agenda
                )
            )

    if not horarios_validos:
        return None

    horarios_validos.sort(
        key=lambda item: item[0]
    )

    return horarios_validos[0][1]


# ==========================================================
# CONTROLE DE TEMA
# ==========================================================

def tema_usado_recentemente(titulo):

    if not os.path.exists(
        ARQUIVO_CONTROLE_TEMAS
    ):
        return False

    agora = obter_horario_brasilia()

    with open(
        ARQUIVO_CONTROLE_TEMAS,
        "r",
        encoding="utf-8"
    ) as f:

        for linha in f:

            linha = linha.strip()

            if "|" not in linha:
                continue

            partes = linha.split("|", 1)

            if len(partes) != 2:
                continue

            data_str, titulo_salvo = partes

            try:
                data_tema = datetime.strptime(
                    data_str,
                    "%Y-%m-%d"
                ).replace(
                    tzinfo=FUSO_BRASILIA
                )

            except ValueError:
                continue

            diferenca_dias = (
                agora - data_tema
            ).days

            if (
                titulo_salvo.strip().lower()
                == titulo.strip().lower()
                and
                diferenca_dias < DIAS_BLOQUEIO_TEMA
            ):
                return True

    return False


def registrar_tema(titulo):

    hoje = obter_horario_brasilia().strftime(
        "%Y-%m-%d"
    )

    with open(
        ARQUIVO_CONTROLE_TEMAS,
        "a",
        encoding="utf-8"
    ) as f:

        f.write(
            f"{hoje}|{titulo}\n"
        )


# ==========================================================
# NORMALIZAÇÃO DE TEXTO
# ==========================================================

def normalizar_texto(texto):
    """
    Normaliza espaços e coloca o texto em minúsculas.
    Mantém acentos para facilitar identificação de termos
    em português.
    """

    if not texto:
        return ""

    texto = texto.lower()

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()


def adicionar_tag(tags, tag):
    """
    Adiciona uma tag sem duplicação.
    """

    if not tag:
        return

    tag = tag.strip()

    if len(tag) < 4:
        return

    tags_normalizadas = {
        normalizar_texto(t)
        for t in tags
    }

    if normalizar_texto(tag) not in tags_normalizadas:
        tags.append(tag)


# ==========================================================
# GERAR TAGS SEO
# ==========================================================

def gerar_tags_seo(titulo, texto):

    stopwords = {
        "com",
        "como",
        "para",
        "porque",
        "porquê",
        "sobre",
        "entre",
        "de",
        "do",
        "da",
        "dos",
        "das",
        "em",
        "um",
        "uma",
        "uns",
        "umas",
        "os",
        "as",
        "que",
        "no",
        "na",
        "nos",
        "nas",
        "ao",
        "aos",
        "por",
        "mais",
        "menos",
        "ser",
        "estar",
        "ter",
        "se",
        "sua",
        "seu",
        "suas",
        "seus",
        "também",
        "muito",
        "muitos",
        "muitas",
        "esse",
        "essa",
        "isso",
        "isso",
        "este",
        "esta",
        "estes",
        "estas"
    }


    # ======================================================
    # CLUSTERS PRINCIPAIS
    # ======================================================

    clusters = {

        "Emagrecimento": [
            "emagrecer",
            "emagrecimento",
            "perder peso",
            "perda de peso",
            "perder gordura",
            "queimar gordura",
            "gordura corporal",
            "redução de gordura",
            "peso saudável",
            "peso ideal",
            "controle do peso",
            "manter o peso",
            "efeito sanfona",
            "obesidade",
            "sobrepeso",
            "composição corporal",
            "massa corporal",
            "imc",
            "índice de massa corporal"
        ],

        "Metabolismo": [
            "metabolismo",
            "metabolismo lento",
            "metabolismo acelerado",
            "taxa metabólica",
            "taxa metabólica basal",
            "gasto energético",
            "gasto calórico",
            "termogênese",
            "termogenese",
            "efeito térmico dos alimentos",
            "metabolismo energético",
            "saúde metabólica",
            "flexibilidade metabólica",
            "resistência à insulina"
        ],

        "Nutrição": [
            "nutrição",
            "nutricao",
            "alimentação",
            "alimentação saudável",
            "nutrientes",
            "macronutrientes",
            "micronutrientes",
            "proteína",
            "proteina",
            "carboidratos",
            "gorduras",
            "fibras",
            "vitaminas",
            "minerais",
            "antioxidantes",
            "probióticos",
            "prebióticos",
            "hidratação",
            "água",
            "deficiência nutricional"
        ],

        "Dietas": [
            "dieta",
            "dietas",
            "plano alimentar",
            "reeducação alimentar",
            "alimentação equilibrada",
            "dieta para emagrecer",
            "dieta saudável",
            "dieta mediterrânea",
            "dieta mediterranea",
            "dieta low carb",
            "low carb",
            "dieta cetogênica",
            "dieta cetogenica",
            "dieta paleo",
            "dieta vegetariana",
            "dieta vegana",
            "jejum",
            "jejum intermitente",
            "janela alimentar",
            "restrição calórica",
            "restricao calorica",
            "déficit calórico",
            "deficit calorico"
        ],

        "Calorias": [
            "calorias",
            "caloria",
            "calorias dos alimentos",
            "contagem de calorias",
            "contar calorias",
            "déficit calórico",
            "deficit calorico",
            "gasto calórico",
            "consumo calórico",
            "necessidade calórica",
            "balanço energético",
            "valor energético"
        ],

        "Alimentos": [
            "alimentos saudáveis",
            "alimentos para emagrecer",
            "alimentos que emagrecem",
            "alimentos ricos em proteína",
            "alimentos ricos em fibras",
            "alimentos com poucas calorias",
            "alimentos nutritivos",
            "frutas",
            "verduras",
            "legumes",
            "grãos",
            "cereais",
            "sementes",
            "castanhas",
            "ovos",
            "peixes",
            "carnes magras",
            "laticínios",
            "leguminosas",
            "feijão",
            "aveia"
        ],

        "Receitas": [
            "receitas saudáveis",
            "receitas para emagrecer",
            "receitas fitness",
            "receitas low carb",
            "receitas com poucas calorias",
            "receitas proteicas",
            "receitas ricas em fibras",
            "café da manhã saudável",
            "almoço saudável",
            "jantar saudável",
            "lanche saudável",
            "sobremesa saudável",
            "suco saudável",
            "salada",
            "sopa saudável",
            "marmita saudável"
        ],

        "Exercícios": [
            "exercício",
            "exercicio",
            "atividade física",
            "atividade fisica",
            "treino",
            "treinos",
            "movimentos",
            "caminhada",
            "correr",
            "corrida",
            "musculação",
            "treinamento de força",
            "exercício aeróbico",
            "exercicio aerobico",
            "cardio",
            "alongamento",
            "mobilidade",
            "calistenia",
            "exercícios em casa",
            "exercícios para iniciantes",
            "treino para emagrecer"
        ],

        "Saúde Metabólica": [
            "insulina",
            "resistência à insulina",
            "resistencia a insulina",
            "glicose",
            "açúcar no sangue",
            "acucar no sangue",
            "diabetes",
            "pré-diabetes",
            "pre-diabetes",
            "colesterol",
            "colesterol alto",
            "triglicerídeos",
            "triglicerideos",
            "pressão arterial",
            "pressao arterial",
            "hipertensão",
            "hipertensao",
            "síndrome metabólica",
            "sindrome metabolica",
            "gordura no fígado",
            "esteatose hepática",
            "saúde cardiovascular"
        ],

        "Saúde e Bem-estar": [
            "saúde",
            "saude",
            "bem-estar",
            "bem estar",
            "qualidade de vida",
            "hábitos saudáveis",
            "hábitos de saúde",
            "estilo de vida saudável",
            "prevenção",
            "longevidade",
            "envelhecimento saudável",
            "saúde física",
            "saúde mental",
            "energia",
            "disposição",
            "vitalidade"
        ],

        "Sono": [
            "sono",
            "dormir",
            "qualidade do sono",
            "insônia",
            "insonia",
            "privação de sono",
            "horas de sono",
            "higiene do sono",
            "sono e emagrecimento",
            "sono e metabolismo"
        ],

        "Estresse": [
            "estresse",
            "stress",
            "ansiedade",
            "estresse e emagrecimento",
            "estresse e alimentação",
            "comer por ansiedade",
            "fome emocional",
            "alimentação emocional",
            "controle emocional",
            "relaxamento",
            "meditação",
            "meditacao",
            "respiração",
            "mindfulness"
        ],

        "Sedentarismo": [
            "sedentarismo",
            "sedentário",
            "sedentaria",
            "ficar sentado",
            "tempo sentado",
            "falta de atividade física",
            "inatividade física",
            "inatividade fisica",
            "movimentação",
            "passos por dia",
            "caminhar mais"
        ],

        "Fome e Apetite": [
            "fome",
            "fome excessiva",
            "apetite",
            "controle do apetite",
            "saciedade",
            "fome emocional",
            "compulsão alimentar",
            "compulsao alimentar",
            "vontade de comer",
            "fome noturna",
            "beliscar",
            "comer demais"
        ],

        "Saúde Digestiva": [
            "digestão",
            "digestao",
            "sistema digestivo",
            "intestino",
            "saúde intestinal",
            "flora intestinal",
            "microbiota intestinal",
            "prisão de ventre",
            "constipação",
            "constipacao",
            "inchaço abdominal",
            "gases",
            "azia",
            "refluxo",
            "fibras e intestino"
        ],

        "Hormônios": [
            "hormônios",
            "hormonios",
            "hormônios e emagrecimento",
            "hormonios e emagrecimento",
            "insulina",
            "leptina",
            "grelina",
            "cortisol",
            "hormônios da fome",
            "hormonios da fome",
            "tireoide",
            "hormônios da tireoide",
            "menopausa e peso"
        ],

        "Suplementos": [
            "suplementos",
            "suplementação",
            "suplementacao",
            "vitaminas",
            "minerais",
            "proteína em pó",
            "whey protein",
            "creatina",
            "ômega 3",
            "omega 3",
            "fibras",
            "probióticos",
            "prebióticos"
        ],

        "Hábitos": [
            "hábitos saudáveis",
            "hábitos para emagrecer",
            "hábitos alimentares",
            "rotina saudável",
            "mudança de hábitos",
            "reeducação alimentar",
            "planejamento alimentar",
            "organização alimentar",
            "preparação de refeições",
            "meal prep",
            "controle de porções",
            "alimentação consciente"
        ]
    }


    # ======================================================
    # ENTIDADES IMPORTANTES
    # ======================================================

    entidades_saude = {

        "metabolismo": "Metabolismo",
        "calorias": "Calorias",
        "termogênese": "Termogênese",
        "termogenese": "Termogênese",
        "gasto energético": "Gasto Energético",
        "taxa metabólica": "Taxa Metabólica",

        "emagrecimento": "Emagrecimento",
        "obesidade": "Obesidade",
        "sobrepeso": "Sobrepeso",
        "imc": "Índice de Massa Corporal",

        "insulina": "Insulina",
        "glicose": "Glicose",
        "diabetes": "Diabetes",
        "pré-diabetes": "Pré-diabetes",
        "pre-diabetes": "Pré-diabetes",
        "colesterol": "Colesterol",
        "triglicerídeos": "Triglicerídeos",
        "triglicerideos": "Triglicerídeos",
        "pressão": "Pressão Arterial",
        "pressao": "Pressão Arterial",
        "pressão arterial": "Pressão Arterial",
        "pressao arterial": "Pressão Arterial",
        "hipertensão": "Hipertensão",
        "hipertensao": "Hipertensão",
        "síndrome metabólica": "Síndrome Metabólica",
        "sindrome metabolica": "Síndrome Metabólica",

        "proteína": "Proteína",
        "proteina": "Proteína",
        "carboidratos": "Carboidratos",
        "gorduras": "Gorduras",
        "fibras": "Fibras",
        "vitaminas": "Vitaminas",
        "minerais": "Minerais",
        "antioxidantes": "Antioxidantes",
        "probióticos": "Probióticos",
        "prebióticos": "Prebióticos",

        "exercício": "Exercício",
        "exercicio": "Exercício",
        "atividade física": "Atividade Física",
        "atividade fisica": "Atividade Física",
        "musculação": "Musculação",
        "caminhada": "Caminhada",
        "sedentarismo": "Sedentarismo",

        "sono": "Sono",
        "insônia": "Insônia",
        "insonia": "Insônia",
        "estresse": "Estresse",
        "ansiedade": "Ansiedade",
        "meditação": "Meditação",
        "meditacao": "Meditação",

        "intestino": "Intestino",
        "microbiota": "Microbiota Intestinal",
        "microbiota intestinal": "Microbiota Intestinal",
        "digestão": "Digestão",
        "digestao": "Digestão",
        "constipação": "Constipação",
        "constipacao": "Constipação",
        "refluxo": "Refluxo",

        "jejum": "Jejum Intermitente",
        "jejum intermitente": "Jejum Intermitente",
        "low carb": "Dieta Low Carb",
        "dieta mediterrânea": "Dieta Mediterrânea",
        "dieta mediterranea": "Dieta Mediterrânea",
        "dieta cetogênica": "Dieta Cetogênica",
        "dieta cetogenica": "Dieta Cetogênica",

        "cortisol": "Cortisol",
        "leptina": "Leptina",
        "grelina": "Grelina",
        "tireoide": "Tireoide",

        "whey protein": "Whey Protein",
        "creatina": "Creatina",
        "ômega 3": "Ômega 3",
        "omega 3": "Ômega 3"
    }


    # ======================================================
    # TEXTO ANALISADO
    # ======================================================

    titulo_normalizado = normalizar_texto(titulo)

    texto_normalizado = normalizar_texto(
        texto
    )

    # Utilizamos uma quantidade maior do texto do artigo
    # para identificar melhor o assunto.
    conteudo = (
        titulo_normalizado
        + " "
        + texto_normalizado[:5000]
    )

    tags = []


    # ======================================================
    # 1. EXPRESSÕES DOS CLUSTERS
    # ======================================================

    # Expressões compostas têm prioridade porque são
    # semanticamente mais fortes que palavras isoladas.

    for cluster, palavras in clusters.items():

        encontrou = False

        for palavra in palavras:

            if normalizar_texto(palavra) in conteudo:

                adicionar_tag(
                    tags,
                    cluster
                )

                encontrou = True
                break

        if encontrou:
            continue


    # ======================================================
    # 2. ENTIDADES DE SAÚDE
    # ======================================================

    entidades_encontradas = []

    for chave, entidade in entidades_saude.items():

        chave_normalizada = normalizar_texto(
            chave
        )

        if chave_normalizada in conteudo:

            if entidade not in entidades_encontradas:

                entidades_encontradas.append(
                    entidade
                )

    for entidade in entidades_encontradas:

        adicionar_tag(
            tags,
            entidade
        )


    # ======================================================
    # 3. EXPRESSÕES RELEVANTES DO TÍTULO
    # ======================================================

    # Primeiro procuramos combinações de 2 e 3 palavras.

    palavras_titulo = re.findall(
        r"\b[a-zà-ÿ]{4,}\b",
        titulo_normalizado
    )

    palavras_titulo_filtradas = [
        palavra
        for palavra in palavras_titulo
        if palavra not in stopwords
    ]


    # Bigramas
    for i in range(
        len(palavras_titulo_filtradas) - 1
    ):

        frase = (
            palavras_titulo_filtradas[i]
            + " "
            + palavras_titulo_filtradas[i + 1]
        )

        if len(frase) >= 8:
            adicionar_tag(
                tags,
                frase.title()
            )


    # Trigramas
    for i in range(
        len(palavras_titulo_filtradas) - 2
    ):

        frase = (
            palavras_titulo_filtradas[i]
            + " "
            + palavras_titulo_filtradas[i + 1]
            + " "
            + palavras_titulo_filtradas[i + 2]
        )

        if len(frase) >= 12:
            adicionar_tag(
                tags,
                frase.title()
            )


    # ======================================================
    # 4. PALAVRAS IMPORTANTES DO TÍTULO
    # ======================================================

    for palavra in palavras_titulo_filtradas:

        if len(palavra) < 4:
            continue

        adicionar_tag(
            tags,
            palavra.capitalize()
        )


    # ======================================================
    # 5. TAGS FIXAS DO BLOG
    # ======================================================

    tags_fixas = [
        "Emagrecimento",
        "Saúde",
        "Bem-estar"
    ]

    for tag_fixa in tags_fixas:

        adicionar_tag(
            tags,
            tag_fixa
        )


    # ======================================================
    # 6. LIMITE DE 200 CARACTERES
    # ======================================================

    resultado = []

    tamanho_atual = 0

    for tag in tags:

        tag = tag.strip()

        if len(tag) < 4:
            continue

        tamanho_tag = len(tag)

        # Blogger separa labels com vírgula.
        # Reservamos espaço para ", ".

        novo_tamanho = (
            tamanho_atual
            + tamanho_tag
            + (2 if resultado else 0)
        )

        if novo_tamanho <= 200:

            resultado.append(tag)

            tamanho_atual = novo_tamanho

        else:
            break


    # Segurança adicional.
    resultado = resultado[:15]

    return resultado


# ==========================================================
# CONSTRUIR SERVIÇO BLOGGER
# ==========================================================

def obter_servico_blogger():

    credenciais = (
        Credentials.from_authorized_user_file(
            "token.json"
        )
    )

    return build(
        "blogger",
        "v3",
        credentials=credenciais
    )


# ==========================================================
# MODO TESTE
# ==========================================================

if __name__ == "__main__":

    if os.getenv("TEST_MODE") == "true":

        print(
            "=== MODO TESTE ATIVADO ==="
        )

        categoria = random.choice(
            CATEGORIAS_EDITORIAIS
        )

        gemini = GeminiEngine()
        imagem_engine = ImageEngine()

        titulo = gemini.gerar_tema(
            categoria
        )

        texto = gemini.gerar_artigo(
            titulo,
            categoria
        )

        imagem = imagem_engine.obter_imagem(
            titulo
        )

        html = obter_esqueleto_html({
            "titulo": titulo,
            "imagem": imagem,
            "texto_completo": texto,
            "assinatura": BLOCO_FIXO_FINAL
        })

        service = obter_servico_blogger()

        labels = gerar_tags_seo(
            titulo,
            texto
        )

        print(
            f"Título: {titulo}"
        )

        print(
            f"Tags: {labels}"
        )

        service.posts().insert(
            blogId=BLOG_ID,
            body={
                "title": titulo,
                "content": html,
                "labels": labels
            },
            isDraft=True
        ).execute()

        registrar_tema(
            titulo
        )

        print(
            "Post de teste criado como rascunho."
        )

        raise SystemExit


# ==========================================================
# EXECUÇÃO PRINCIPAL
# ==========================================================

agora = obter_horario_brasilia()

data_hoje = agora.strftime(
    "%Y-%m-%d"
)

horario_escolhido = encontrar_horario_disponivel(
    agora
)


# ==========================================================
# FORÇAR POSTAGEM
# ==========================================================

if horario_escolhido is None:

    if os.getenv("FORCAR_POSTAGEM") == "true":

        print(
            "Fora da janela, mas FORÇANDO postagem..."
        )

        horario_escolhido = (
            f"FORCADO-{agora.strftime('%H:%M')}"
        )

    else:

        print(
            "Fora da janela de postagem."
        )

        print(
            f"Horário atual: "
            f"{agora.strftime('%H:%M')}"
        )

        print(
            f"Janela utilizada: "
            f"{JANELA_POSTAGEM} minutos"
        )

        print(
            "Nenhuma ação realizada."
        )

        raise SystemExit


# ==========================================================
# INFORMAÇÕES DE EXECUÇÃO
# ==========================================================

print(
    "=== EXECUÇÃO DO BLOG ==="
)

print(
    f"Horário Brasília: "
    f"{agora.strftime('%d/%m/%Y %H:%M')}"
)

print(
    f"Janela de postagem: "
    f"{JANELA_POSTAGEM} minutos"
)

print(
    f"Horário selecionado: "
    f"{horario_escolhido}"
)


# ==========================================================
# INICIALIZAÇÃO DOS ENGINES
# ==========================================================

gemini = GeminiEngine()

imagem_engine = ImageEngine()


# ==========================================================
# ROTAÇÃO DE CATEGORIA
# ==========================================================

categoria = random.choice(
    CATEGORIAS_EDITORIAIS
)

print(
    f"Categoria selecionada: "
    f"{categoria}"
)


# ==========================================================
# GERAÇÃO DE TEMA
# ==========================================================

titulo = None

for tentativa_numero in range(5):

    tentativa = gemini.gerar_tema(
        categoria
    )

    if not tentativa:
        continue

    tentativa = tentativa.strip()

    if not tema_usado_recentemente(
        tentativa
    ):

        titulo = tentativa

        break


if not titulo:

    print(
        "Nenhum tema novo encontrado."
    )

    print(
        "Postagem abortada para evitar repetição."
    )

    raise SystemExit


print(
    f"Tema escolhido: {titulo}"
)


# ==========================================================
# GERAÇÃO DO ARTIGO
# ==========================================================

texto = gemini.gerar_artigo(
    titulo,
    categoria
)


if not texto:

    print(
        "O Gemini não retornou conteúdo."
    )

    raise SystemExit


# ==========================================================
# GERAÇÃO DA IMAGEM
# ==========================================================

imagem = imagem_engine.obter_imagem(
    titulo
)


# ==========================================================
# GERAÇÃO DO HTML
# ==========================================================

html = obter_esqueleto_html({
    "titulo": titulo,
    "imagem": imagem,
    "texto_completo": texto,
    "assinatura": BLOCO_FIXO_FINAL
})


# ==========================================================
# TAGS SEO
# ==========================================================

labels = gerar_tags_seo(
    titulo,
    texto
)

print(
    f"Tags SEO: {labels}"
)


# ==========================================================
# CONEXÃO COM BLOGGER
# ==========================================================

service = obter_servico_blogger()


# ==========================================================
# PUBLICAÇÃO
# ==========================================================

service.posts().insert(
    blogId=BLOG_ID,
    body={
        "title": titulo,
        "content": html,
        "labels": labels
    },
    isDraft=False
).execute()


# ==========================================================
# REGISTROS
# ==========================================================

registrar_postagem(
    data_hoje,
    horario_escolhido
)

registrar_tema(
    titulo
)


# ==========================================================
# FINALIZAÇÃO
# ==========================================================

print(
    "=========================================="
)

print(
    "Post publicado com sucesso."
)

print(
    f"Título: {titulo}"
)

print(
    f"Categoria: {categoria}"
)

print(
    f"Horário: {horario_escolhido}"
)

print(
    f"Tags: {labels}"
)

print(
    "=========================================="
)
