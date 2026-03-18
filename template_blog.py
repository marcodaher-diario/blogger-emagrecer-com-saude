# -*- coding: utf-8 -*-
import re

def formatar_conteudo_supremo(texto_bruto, titulo_principal):
    """
    Formata o conteúdo em HTML de forma hierárquica e inteligente,
    garantindo economia de caracteres e organização visual.
    Inclui o filtro para ignorar o título repetido se ele vier no texto.
    """
    if not texto_bruto: return ""
    
    # 1. Pré-processamento e normalização do título para o filtro
    linhas = [l.strip() for l in texto_bruto.split("\n") if l.strip()]
    html_final = []
    
    # Prepara o título principal para comparação (remove espaços extras e coloca em minúsculas)
    t_normalizado = titulo_principal.strip().lower()
    
    lista_aberta = False

    for linha in linhas:
        # 1. Limpeza Inicial de Markdown (# e *)
        linha_Markdown = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", linha)
        linha_Markdown = re.sub(r"\*(.*?)\*", r"<em>\1</em>", linha_Markdown)
        
        # Limpa espaços e marcadores das pontas, mas preserva a formatação interna
        l_limpa = linha_Markdown.lstrip("#* ").strip()
        
        # 2. FILTRO ANTI-REPETIÇÃO: Compara a linha limpa com o título principal
        # Se for igual, ignora essa linha e continua o loop.
        if l_limpa.lower() == t_normalizado or not l_limpa:
            continue

        # 3. Tratamento de Listas (UL/LI)
        if linha.startswith(("- ", "* ")) or re.match(r"^\d+\.", linha):
            if not lista_aberta:
                html_final.append('<ul class="lst">')
                lista_aberta = True
            item = re.sub(r"^[-*\d. ]+", "", l_limpa)
            html_final.append(f'<li>{item}</li>')
            continue
        else:
            if lista_aberta:
                html_final.append('</ul>')
                lista_aberta = False

        # 4. DETECÇÃO DE HIERARQUIA DE TÍTULOS (H1, H2, H3)
        # Usa critérios de comprimento e pontuação para distinguir de parágrafo.
        texto_puro = re.sub(r"<.*?>", "", l_limpa)
        palavras = texto_puro.split()
        
        # Critério: Linha curta, sem ponto final/dois pontos e começando com letra maiúscula
        e_titulo = (linha.startswith("#") or (len(palavras) <= 15 and not texto_puro.endswith((".", ":", "?", "!")) and texto_puro[0].isupper()))

        if e_titulo:
            # H1 Manual (Se o usuário usar # no texto)
            if linha.startswith("# "):
                html_final.append(f'<h1 class="t1">{l_limpa}</h1>')
            # H2 Padrão (Seções principais)
            elif linha.startswith("## ") or not linha.startswith("### "):
                html_final.append(f'<h2 class="t2">{l_limpa}</h2>')
            # H3 (Subseções secundárias)
            else:
                html_final.append(f'<h3 class="t3">{l_limpa}</h3>')
        else:
            # 5. Parágrafo Padrão (Compacto)
            html_final.append(f'<p class="txt">{l_limpa}</p>')

    # Fecha qualquer lista que tenha ficado aberta
    if lista_aberta: html_final.append('</ul>')
    
    # Une tudo com quebras de linha para economizar caracteres mas manter a legibilidade do código
    return "\n".join(html_final)

def obter_esqueleto_html(dados):
    # Pega os dados brutos e formata o conteúdo
    t = dados.get("titulo", "").strip()
    img = dados.get("imagem", "").strip()
    txt = dados.get("texto_completo", "")
    ass = dados.get("assinatura", "")
    
    # Sua cor padrão "gold"
    cor = "rgb(7, 55, 99)"

    # Passa o título para a função de formatação para o filtro funcionar
    conteudo_formatado = formatar_conteudo_supremo(txt, t)

    return f"""
<style>
/* Container Principal e Reset */
.post-master {{ max-width:900px; margin:auto; font-family:sans-serif; color:{cor}; line-height:1.6; }}

/* Títulos Automáticos do Blogger (Garante o visual independente do tema) */
.post-title, .entry-title, h1.post-title {{
    text-align:center!important; font-size:28px!important; text-transform:uppercase!important; 
    font-weight:bold!important; margin:10px 0 25px 0!important; color:{cor}!important;
}}

/* Imagem Responsiva com Proporção 16:9 */
.img-c {{ text-align:center; margin-bottom:25px; }}
.img-p {{ width:100%; height:auto; aspect-ratio:16/9; object-fit:cover; border-radius:8px; }}

/* Hierarquia de Títulos visíveis no Corpo do Texto */
/* Nomes de classe curtos para economizar caracteres */
.t1 {{ font-size:26px!important; font-weight:bold!important; text-align:center!important; margin:30px 0 15px 0!important; text-transform:uppercase!important; color:{cor}!important; display:block!important; }}
.t2 {{ font-size:22px!important; font-weight:bold!important; text-align:left!important; margin:30px 0 12px 0!important; text-transform:uppercase!important; color:{cor}!important; display:block!important; }}
.t3 {{ font-size:19px!important; font-weight:bold!important; text-align:left!important; margin:25px 0 10px 0!important; color:{cor}!important; display:block!important; }}

/* Parágrafos e Listas (Otimizados em espaço) */
.txt {{ font-size:18px!important; text-align:justify!important; margin-bottom:15px!important; color:{cor}!important; }}
.lst {{ margin-bottom:20px; padding-left:25px; }}
.lst li {{ font-size:18px!important; margin-bottom:8px; color:{cor}!important; }}

/* Assinatura */
.sig {{ margin-top:35px; border-top:1px solid #eee; padding-top:20px; font-style:italic; }}
</style>

<div class="post-master">
    <div class="img-c"><img src="{img}" alt="{t}" class="img-p" loading="lazy"></div>
    <div class="artigo">
        {conteudo_formatado}
    </div>
    <div class="sig">{ass}</div>
</div>
"""
