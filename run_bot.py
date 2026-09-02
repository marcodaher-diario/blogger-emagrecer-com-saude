import os
import re
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from configuracoes import (
    BLOG_ID,
    AGENDA_POSTAGENS,
    JANELA_MINUTOS,
    CATEGORIAS_EDITORIAIS,
    ARQUIVO_CONTROLE_AGENDAMENTO,
    ARQUIVO_CONTROLE_TEMAS,
    DIAS_BLOQUEIO_TEMA,
    BLOCO_FIXO_FINAL,
)


# ============================================================
# CONFIGURAÇÃO DE EXECUÇÃO
# ============================================================

# true  = TESTE / publicação forçada imediatamente
# false = funcionamento normal conforme a agenda
FORCAR_POSTAGEM = os.getenv("FORCAR_POSTAGEM", "false").lower()


# ============================================================
# FUSO HORÁRIO
# ============================================================

FUSO_BRASILIA = ZoneInfo("America/Sao_Paulo")


def obter_horario_brasilia():
    """
    Retorna a data/hora atual no horário de Brasília.
    """
    return datetime.now(FUSO_BRASILIA)


# ============================================================
# CONVERSÃO DE HORÁRIO
# ============================================================

def horario_para_minutos(horario):
    """
    Converte HH:MM para quantidade de minutos desde 00:00.
    """
    hora, minuto = map(int, horario.split(":"))
    return hora * 60 + minuto


def diferenca_minutos(min1, min2):
    """
    Retorna a diferença absoluta entre dois horários em minutos.
    """
    return abs(min1 - min2)


# ============================================================
# CONTROLE DA AGENDA
# ============================================================

def dentro_da_janela(min_atual, min_agenda):
    """
    Verifica se o horário atual está dentro da janela
    permitida em relação ao horário agendado.
    """
    return diferenca_minutos(min_atual, min_agenda) <= JANELA_MINUTOS


def ja_postou(data, horario):
    """
    Verifica se determinado horário da agenda já foi utilizado.
    """
    if not os.path.exists(ARQUIVO_CONTROLE_AGENDAMENTO):
        return False

    try:
        with open(
            ARQUIVO_CONTROLE_AGENDAMENTO,
            "r",
            encoding="utf-8"
        ) as arquivo:

            for linha in arquivo:
                linha = linha.strip()

                if not linha:
                    continue

                partes = linha.split("|", 1)

                if len(partes) < 2:
                    continue

                data_registrada = partes[0].strip()
                horario_registrado = partes[1].strip()

                if (
                    data_registrada == data
                    and horario_registrado == horario
                ):
                    return True

    except Exception as e:
        print(f"Erro ao verificar controle de agendamento: {e}")

    return False


def registrar_postagem(data, horario):
    """
    Registra uma publicação realizada.
    """
    try:
        with open(
            ARQUIVO_CONTROLE_AGENDAMENTO,
            "a",
            encoding="utf-8"
        ) as arquivo:

            arquivo.write(f"{data}|{horario}\n")

    except Exception as e:
        print(f"Erro ao registrar postagem: {e}")


def encontrar_horario_agenda():
    """
    Procura um horário da agenda que esteja dentro da janela
    de publicação e ainda não tenha sido utilizado hoje.

    Retorna:
        horario_agenda
        ou None
    """

    agora = obter_horario_brasilia()

    data_hoje = agora.strftime("%Y-%m-%d")
    min_atual = agora.hour * 60 + agora.minute

    horarios_validos = []

    for horario_agenda in AGENDA_POSTAGENS:

        min_agenda = horario_para_minutos(horario_agenda)

        if dentro_da_janela(min_atual, min_agenda):

            if not ja_postou(data_hoje, horario_agenda):

                diferenca = diferenca_minutos(
                    min_atual,
                    min_agenda
                )

                horarios_validos.append(
                    (diferenca, horario_agenda)
                )

    if not horarios_validos:
        return None

    horarios_validos.sort(key=lambda x: x[0])

    return horarios_validos[0][1]


# ============================================================
# RECUPERAÇÃO DE PUBLICAÇÃO PERDIDA
# ============================================================

def encontrar_horario_atrasado():
    """
    Verifica se existe algum horário da agenda de hoje que
    já passou e ainda não foi publicado.

    Retorna o horário mais recente que foi perdido.

    Isso permite que uma execução atrasada do GitHub Actions
    ainda consiga realizar a publicação.
    """

    agora = obter_horario_brasilia()

    data_hoje = agora.strftime("%Y-%m-%d")
    min_atual = agora.hour * 60 + agora.minute

    horarios_perdidos = []

    for horario_agenda in AGENDA_POSTAGENS:

        min_agenda = horario_para_minutos(horario_agenda)

        # Só considera horários que já passaram
        if min_agenda < min_atual:

            if not ja_postou(data_hoje, horario_agenda):

                atraso = min_atual - min_agenda

                horarios_perdidos.append(
                    (atraso, horario_agenda)
                )

    if not horarios_perdidos:
        return None

    # O mais recente horário perdido vem primeiro
    horarios_perdidos.sort(key=lambda x: x[0])

    return horarios_perdidos[0][1]


# ============================================================
# CONTROLE DE TEMAS
# ============================================================

def tema_usado_recentemente(tema):
    """
    Verifica se o tema já foi utilizado dentro do período
    de bloqueio definido em DIAS_BLOQUEIO_TEMA.
    """

    if not os.path.exists(ARQUIVO_CONTROLE_TEMAS):
        return False

    agora = obter_horario_brasilia().replace(tzinfo=None)
    limite = agora - timedelta(days=DIAS_BLOQUEIO_TEMA)

    tema_normalizado = tema.strip().lower()

    try:
        with open(
            ARQUIVO_CONTROLE_TEMAS,
            "r",
            encoding="utf-8"
        ) as arquivo:

            for linha in arquivo:

                linha = linha.strip()

                if not linha:
                    continue

                partes = linha.split("|", 1)

                if len(partes) != 2:
                    continue

                data_texto = partes[0].strip()
                tema_registrado = partes[1].strip()

                try:
                    data_registro = datetime.strptime(
                        data_texto,
                        "%Y-%m-%d %H:%M:%S"
                    )

                except ValueError:
                    continue

                if data_registro < limite:
                    continue

                if tema_registrado.lower() == tema_normalizado:
                    return True

    except Exception as e:
        print(f"Erro ao verificar temas usados: {e}")

    return False


def registrar_tema(tema):
    """
    Registra o tema utilizado.
    """

    agora = obter_horario_brasilia().replace(tzinfo=None)

    try:
        with open(
            ARQUIVO_CONTROLE_TEMAS,
            "a",
            encoding="utf-8"
        ) as arquivo:

            arquivo.write(
                f"{agora.strftime('%Y-%m-%d %H:%M:%S')}|{tema}\n"
            )

    except Exception as e:
        print(f"Erro ao registrar tema: {e}")


# ============================================================
# TAGS SEO
# ============================================================

def gerar_tags_seo(titulo, texto, categoria):
    """
    Gera tags SEO combinando:
    - palavras do título
    - expressões compostas
    - entidades
    - clusters editoriais
    - categoria
    - tags fixas

    Limite:
    - 15 tags
    - 200 caracteres
    """

    clusters = {

        "emagrecimento": [
            "emagrecimento",
            "emagrecer",
            "perder peso",
            "perda de peso",
            "gordura corporal",
            "gordura abdominal",
            "controle do peso",
            "peso saudável"
        ],

        "metabolismo": [
            "metabolismo",
            "metabolismo acelerado",
            "metabolismo lento",
            "taxa metabólica",
            "metabólico",
            "metabolica"
        ],

        "nutrição": [
            "nutrição",
            "nutricao",
            "alimentação saudável",
            "alimentação",
            "nutrientes",
            "proteína",
            "proteina",
            "fibras",
            "vitaminas",
            "minerais"
        ],

        "dietas": [
            "dieta",
            "dietas",
            "dieta saudável",
            "dieta para emagrecer",
            "low carb",
            "dieta mediterrânea",
            "jejum",
            "jejum intermitente"
        ],

        "calorias": [
            "calorias",
            "déficit calórico",
            "deficit calorico",
            "gasto calórico",
            "calorias para emagrecer"
        ],

        "alimentos": [
            "alimentos saudáveis",
            "alimentos para emagrecer",
            "alimentos nutritivos",
            "comida saudável",
            "ingredientes saudáveis"
        ],

        "receitas": [
            "receitas saudáveis",
            "receitas funcionais",
            "receita saudável",
            "receita para emagrecer",
            "receitas para emagrecer"
        ],

        "exercícios": [
            "exercício",
            "exercicio",
            "exercícios",
            "atividade física",
            "atividade",
            "treino",
            "treino para emagrecer",
            "exercícios para emagrecer",
            "movimentos"
        ],

        "saúde metabólica": [
            "saúde metabólica",
            "insulina",
            "resistência à insulina",
            "diabetes",
            "colesterol",
            "triglicerídeos",
            "pressão arterial",
            "glicemia"
        ],

        "saúde e bem-estar": [
            "saúde",
            "saúde e bem-estar",
            "bem-estar",
            "qualidade de vida",
            "vida saudável",
            "hábitos saudáveis"
        ],

        "sono": [
            "sono",
            "qualidade do sono",
            "dormir bem",
            "privação de sono",
            "sono e emagrecimento"
        ],

        "estresse": [
            "estresse",
            "stress",
            "estresse e emagrecimento",
            "ansiedade alimentar",
            "comer emocional"
        ],

        "sedentarismo": [
            "sedentarismo",
            "sedentário",
            "ficar muito tempo sentado",
            "atividade física",
            "movimentação"
        ],

        "fome e apetite": [
            "fome",
            "apetite",
            "controle do apetite",
            "saciedade",
            "fome emocional"
        ],

        "saúde digestiva": [
            "saúde digestiva",
            "digestão",
            "intestino",
            "flora intestinal",
            "microbiota",
            "constipação"
        ],

        "hormônios": [
            "hormônios",
            "hormônios do apetite",
            "leptina",
            "grelina",
            "cortisol",
            "insulina"
        ],

        "suplementos": [
            "suplementos",
            "suplementação",
            "suplementos para emagrecer",
            "vitaminas",
            "minerais"
        ],

        "hábitos": [
            "hábitos saudáveis",
            "mudança de hábitos",
            "rotina saudável",
            "estilo de vida",
            "qualidade de vida"
        ]
    }

    entidades = [
        "metabolismo",
        "calorias",
        "insulina",
        "diabetes",
        "colesterol",
        "pressão",
        "pressao",
        "sedentarismo",
        "termogênese",
        "termogenese",
        "fome",
        "saciedade",
        "microbiota",
        "intestino",
        "sono",
        "estresse",
        "cortisol",
        "leptina",
        "grelina",
        "proteína",
        "proteina",
        "fibras",
        "vitaminas",
        "minerais"
    ]

    tags = []

    def adicionar_tag(tag):
        tag = tag.strip()

        if not tag:
            return

        tag_normalizada = tag.lower()

        if tag_normalizada not in [
            t.lower() for t in tags
        ]:
            tags.append(tag)

    # --------------------------------------------------------
    # Texto para análise
    # --------------------------------------------------------

    titulo_limpo = re.sub(
        r"[^\wÀ-ÿ\s]",
        " ",
        titulo,
        flags=re.UNICODE
    )

    texto_inicio = texto[:500]

    texto_analise = (
        titulo_limpo + " " + texto_inicio
    ).lower()

    # --------------------------------------------------------
    # Categoria
    # --------------------------------------------------------

    adicionar_tag(categoria)

    # --------------------------------------------------------
    # Clusters
    # --------------------------------------------------------

    for nome_cluster, termos in clusters.items():

        encontrou = False

        for termo in termos:

            if termo.lower() in texto_analise:
                encontrou = True
                break

        if encontrou:

            # adiciona os termos mais relevantes
            for termo in termos[:4]:

                if termo.lower() in texto_analise:
                    adicionar_tag(termo)

    # --------------------------------------------------------
    # Entidades
    # --------------------------------------------------------

    for entidade in entidades:

        if entidade.lower() in texto_analise:
            adicionar_tag(entidade)

    # --------------------------------------------------------
    # Palavras compostas do título
    # --------------------------------------------------------

    palavras = titulo_limpo.split()

    palavras_filtradas = [
        p for p in palavras
        if len(p) >= 4
    ]

    stopwords = {
        "para",
        "como",
        "qual",
        "quais",
        "esse",
        "essa",
        "isso",
        "quando",
        "onde",
        "porque",
        "você",
        "voce",
        "mais",
        "menos",
        "muito",
        "muita",
        "pode",
        "podem",
        "está",
        "esta",
        "estão",
        "estao"
    }

    palavras_filtradas = [
        p for p in palavras_filtradas
        if p.lower() not in stopwords
    ]

    # Bigrams
    for i in range(len(palavras_filtradas) - 1):

        expressao = (
            f"{palavras_filtradas[i]} "
            f"{palavras_filtradas[i + 1]}"
        )

        adicionar_tag(expressao)

    # Trigrams
    for i in range(len(palavras_filtradas) - 2):

        expressao = (
            f"{palavras_filtradas[i]} "
            f"{palavras_filtradas[i + 1]} "
            f"{palavras_filtradas[i + 2]}"
        )

        adicionar_tag(expressao)

    # Palavras individuais do título
    for palavra in palavras_filtradas:
        adicionar_tag(palavra)

    # --------------------------------------------------------
    # Tags fixas
    # --------------------------------------------------------

    adicionar_tag("Emagrecimento")
    adicionar_tag("Saúde")

    # --------------------------------------------------------
    # Limpeza
    # --------------------------------------------------------

    tags_finais = []

    tamanho_atual = 0

    for tag in tags:

        if len(tags_finais) >= 15:
            break

        nova_tag = tag

        if tags_finais:
            tamanho_adicional = len(nova_tag) + 1
        else:
            tamanho_adicional = len(nova_tag)

        if tamanho_atual + tamanho_adicional <= 200:

            tags_finais.append(nova_tag)
            tamanho_atual += tamanho_adicional

    return tags_finais


# ============================================================
# BLOGGER
# ============================================================

SCOPES = [
    "https://www.googleapis.com/auth/blogger"
]


def obter_servico_blogger():
    """
    Autentica no Google e retorna o serviço Blogger.
    """

    creds = None

    if os.path.exists("token.json"):

        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:

            creds.refresh(Request())

        else:

            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )

            creds = flow.run_local_server(
                port=0
            )

        with open(
            "token.json",
            "w",
            encoding="utf-8"
        ) as token:

            token.write(creds.to_json())

    return build(
        "blogger",
        "v3",
        credentials=creds
    )


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

if __name__ == "__main__":

    agora = obter_horario_brasilia()

    data_hoje = agora.strftime("%Y-%m-%d")

    hora_atual = agora.strftime("%H:%M")

    min_atual = (
        agora.hour * 60
        + agora.minute
    )

    print("=" * 60)
    print("BOT BLOGGER")
    print("=" * 60)
    print(
        f"Data/hora Brasília: "
        f"{agora.strftime('%d/%m/%Y %H:%M:%S')}"
    )

    print(
        f"Modo forçado/teste: "
        f"{FORCAR_POSTAGEM}"
    )

    print(
        f"Janela normal: "
        f"{JANELA_MINUTOS} minutos"
    )

    print(
        f"Agenda: "
        f"{', '.join(AGENDA_POSTAGENS.keys())}"
    )

    print("=" * 60)

    # ========================================================
    # DEFINIÇÃO DO HORÁRIO DA PUBLICAÇÃO
    # ========================================================

    horario_escolhido = None

    # --------------------------------------------------------
    # 1. TESTE / FORÇADO
    # --------------------------------------------------------

    if FORCAR_POSTAGEM == "true":

        print()
        print(">>> MODO TESTE/FORÇADO ATIVADO <<<")
        print(
            f"Publicação será realizada imediatamente "
            f"às {hora_atual}."
        )
        print(
            "A agenda de publicação será ignorada."
        )

        # Importante:
        # O teste NÃO consome o horário real da agenda.
        horario_escolhido = (
            f"TESTE-{hora_atual}"
        )

    # --------------------------------------------------------
    # 2. MODO NORMAL
    # --------------------------------------------------------

    else:

        horario_escolhido = encontrar_horario_agenda()

        if horario_escolhido:

            print()
            print(
                "Horário de agenda encontrado:"
            )

            print(
                f"Horário programado: "
                f"{horario_escolhido}"
            )

            print(
                f"Horário atual: "
                f"{hora_atual}"
            )

        else:

            # ------------------------------------------------
            # 3. TENTAR RECUPERAR HORÁRIO PERDIDO
            # ------------------------------------------------

            horario_atrasado = encontrar_horario_atrasado()

            if horario_atrasado:

                horario_escolhido = horario_atrasado

                print()
                print(
                    ">>> PUBLICAÇÃO ATRASADA DETECTADA <<<"
                )

                print(
                    f"Horário original: "
                    f"{horario_atrasado}"
                )

                print(
                    f"Horário atual: "
                    f"{hora_atual}"
                )

                print(
                    "A publicação será recuperada agora."
                )

            else:

                print()
                print(
                    "Fora da janela de publicação."
                )

                print(
                    f"Horário atual: {hora_atual}"
                )

                print(
                    f"Janela normal: "
                    f"{JANELA_MINUTOS} minutos"
                )

                print(
                    "Nenhuma ação realizada."
                )

                raise SystemExit

    # ========================================================
    # GERAÇÃO DO CONTEÚDO
    # ========================================================

    print()
    print("=" * 60)
    print("GERANDO CONTEÚDO")
    print("=" * 60)

    # --------------------------------------------------------
    # Categoria
    # --------------------------------------------------------

    categoria = random.choice(
        CATEGORIAS_EDITORIAIS
    )

    print(
        f"Categoria escolhida: {categoria}"
    )

    # --------------------------------------------------------
    # Geração do tema
    # --------------------------------------------------------

    tema = None

    for tentativa in range(1, 6):

        print(
            f"Gerando tema "
            f"(tentativa {tentativa}/5)..."
        )

        # ====================================================
        # IMPORTANTE:
        # MANTENHA AQUI A SUA FUNÇÃO ORIGINAL DE GERAÇÃO
        # DE TEMA, CASO ELA ESTEJA DEFINIDA NO SEU ARQUIVO.
        # ====================================================

        try:

            tema = gerar_tema(categoria)

        except NameError:

            print(
                "ERRO: a função gerar_tema() "
                "não está definida neste arquivo."
            )

            raise

        if tema:

            tema = tema.strip()

            if not tema_usado_recentemente(tema):

                break

            print(
                "Tema já utilizado recentemente. "
                "Gerando outro..."
            )

            tema = None

    if not tema:

        print(
            "Não foi possível obter um tema novo."
        )

        raise SystemExit

    print(
        f"Tema escolhido: {tema}"
    )

    # ========================================================
    # ARTIGO
    # ========================================================

    print()
    print("Gerando artigo...")

    try:

        artigo = gerar_artigo(
            tema,
            categoria
        )

    except NameError:

        print(
            "ERRO: a função gerar_artigo() "
            "não está definida neste arquivo."
        )

        raise

    if not artigo:

        print(
            "Não foi possível gerar o artigo."
        )

        raise SystemExit

    # ========================================================
    # IMAGEM
    # ========================================================

    print()
    print("Gerando imagem...")

    try:

        imagem = gerar_imagem(
            tema
        )

    except NameError:

        print(
            "ERRO: a função gerar_imagem() "
            "não está definida neste arquivo."
        )

        raise

    # ========================================================
    # TAGS
    # ========================================================

    tags = gerar_tags_seo(
        tema,
        artigo,
        categoria
    )

    print()
    print(
        "Tags SEO:"
    )

    print(
        ", ".join(tags)
    )

    # ========================================================
    # HTML
    # ========================================================

    print()
    print("Montando HTML...")

    try:

        html = montar_html(
            titulo=tema,
            artigo=artigo,
            imagem=imagem,
            categoria=categoria,
            tags=tags,
            bloco_final=BLOCO_FIXO_FINAL
        )

    except NameError:

        print(
            "ERRO: a função montar_html() "
            "não está definida neste arquivo."
        )

        raise

    # ========================================================
    # BLOGGER
    # ========================================================

    print()
    print(
        "Conectando ao Blogger..."
    )

    service = obter_servico_blogger()

    print(
        "Publicando artigo..."
    )

    postagem = {

        "kind": "blogger#post",

        "title": tema,

        "content": html,

        "labels": tags
    }

    resultado = service.posts().insert(

        blogId=BLOG_ID,

        body=postagem,

        isDraft=False

    ).execute()

    # ========================================================
    # RESULTADO
    # ========================================================

    print()
    print("=" * 60)
    print("PUBLICAÇÃO CONCLUÍDA")
    print("=" * 60)

    print(
        f"Título: {tema}"
    )

    print(
        f"Categoria: {categoria}"
    )

    print(
        f"Modo: "
        f"{'TESTE/FORÇADO' if FORCAR_POSTAGEM == 'true' else 'NORMAL'}"
    )

    print(
        f"Horário registrado: "
        f"{horario_escolhido}"
    )

    print(
        f"ID da postagem: "
        f"{resultado.get('id')}"
    )

    print(
        f"URL: "
        f"{resultado.get('url')}"
    )

    # ========================================================
    # REGISTRO
    # ========================================================

    # No modo normal:
    # registra o horário REAL da agenda.
    #
    # No modo teste:
    # registra TESTE-HH:MM e NÃO consome 15:00.

    registrar_postagem(
        data_hoje,
        horario_escolhido
    )

    registrar_tema(
        tema
    )

    print()
    print(
        "Controles atualizados."
    )

    print("=" * 60)
