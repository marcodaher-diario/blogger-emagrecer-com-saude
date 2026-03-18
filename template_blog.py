# -*- coding: utf-8 -*-
import re

def formatar_conteudo_diario(texto_bruto, titulo_principal):
    if not texto_bruto: return ""
    
    linhas = [l.strip() for l in texto_bruto.split("\n") if l.strip()]
    html_final = []
    t_normalizado = titulo_principal.strip().lower()
    lista_aberta = False
    primeira_linha_valida = True # Marcador para identificar o primeiro título após a imagem

    for linha in linhas:
        # 1. Limpeza e Formatação Base
        l_proc = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", linha)
        l_proc = re.sub(r"\*(.*?)\*", r"<em>\1</em>", l_proc)
        l_limpa = l_proc.lstrip("#* ").strip()
        
        # 2. FILTRO ANTI-REPETIÇÃO (Igual ao Diário de Notícias)
        if l_limpa.lower() == t_normalizado or not l_limpa:
            continue

        # 3. Tratamento de Listas
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

        # 4. LÓGICA DE TÍTULO PÓS-IMAGEM (O diferencial do Diário)
        texto_puro = re.sub(r"<.*?>", "", l_limpa)
        palavras = texto_puro.split()
        
        # Se for a primeira linha após os filtros e for curta, vira H2 (t2) obrigatoriamente
        e_titulo = (linha.startswith("#") or (len(palavras) <= 22 and not texto_puro.endswith(".")))

        if e_titulo:
            if primeira_linha_valida or linha.startswith("## "):
                html_final.append(f'<h2 class="t2">{l_limpa}</h2>')
                primeira_linha_valida = False # Já colocamos o primeiro título
            elif linha.startswith("### "):
                html_final.append(f'<h3 class="t3">{l_limpa}</h3>')
            elif linha.startswith("# "):
                html_final.append(f'<h1 class="t1">{l_limpa}</h1>')
            else:
                # Se houver outro título curto depois, ele segue a hierarquia normal
                html_final.append(f'<h2 class="t2">{l_limpa}</h2>')
        else:
            html_final.append(f'<p class="txt">{l_limpa}</p>')
            primeira_linha_valida = False # Se veio um parágrafo, a chance do título de abertura passou

    if lista_aberta: html_final.append('</ul>')
    return "\n".join(html_final)

def obter_esqueleto_html(dados):
    t = dados.get("titulo", "").strip()
    img = dados.get("imagem", "").strip()
    txt = dados.get("texto_completo", "")
    ass = dados.get("assinatura", "")
    
    cor = "rgb(7, 55, 99)"
    conteudo = formatar_conteudo_diario(txt, t)

    return f"""
<style>
.post-master {{ max-width:900px; margin:auto; font-family:sans-serif; color:{cor}; line-height:1.6; }}
.post-title, .entry-title {{ text-align:center!important; font-size:28px!important; text-transform:uppercase!important; font-weight:bold!important; margin:10px 0 25px 0!important; color:{cor}!important; }}
.img-c {{ text-align:center; margin-bottom:25px; }}
.img-p {{ width:100%; height:auto; aspect-ratio:16/9; object-fit:cover; border-radius:8px; }}
.t1 {{ font-size:26px!important; font-weight:bold!important; text-align:center!important; margin:30px 0 15px 0!important; text-transform:uppercase!important; color:{cor}!important; display:block!important; }}
.t2 {{ font-size:20px!important; font-weight:bold!important; text-align:left!important; margin:25px 0 10px 0!important; text-transform:uppercase!important; color:{cor}!important; display:block!important; }}
.t3 {{ font-size:18px!important; font-weight:bold!important; text-align:left!important; margin:20px 0 10px 0!important; color:{cor}!important; display:block!important; }}
.txt {{ font-size:18px!important; text-align:justify!important; margin-bottom:15px!important; color:{cor}!important; }}
.lst {{ margin-bottom:20px; padding-left:25px; }}
.lst li {{ font-size:18px!important; margin-bottom:8px; color:{cor}!important; }}
.sig {{ margin-top:35px; border-top:1px solid #eee; padding-top:20px; font-style:italic; }}
</style>

<div class="post-master">
    <div class="img-c"><img src="{img}" alt="{t}" class="img-p" loading="lazy"></div>
    <div class="artigo">{conteudo}</div>
    <div class="sig">{ass}</div>
</div>
"""
