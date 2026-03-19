# -*- coding: utf-8 -*-
import re

def formatar_conteudo_otimizado(texto_bruto, titulo_principal):
    if not texto_bruto: return ""
    
    # Processamento em lote para ser mais rápido e limpo
    linhas = [l.strip() for l in texto_bruto.split("\n") if l.strip()]
    html_final = []
    titulo_norm = titulo_principal.strip().lower()
    lista_aberta = False

    for linha in linhas:
        # 1. Negritos Simples (Ocupa menos bytes que estilos inline)
        l_proc = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", linha)
        l_limpa = l_proc.strip("#* ").strip()
        
        if l_limpa.lower() == titulo_norm or not l_limpa:
            continue

        # 2. Listas (Compactas)
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

        # 3. Identificação de H2 vs P (Nomes de classe curtos para economizar bytes)
        palavras = re.sub(r"<.*?>", "", l_limpa).split()
        is_h2 = len(palavras) <= 20 and not l_limpa.endswith((".", ":")) and l_limpa[0].isupper()

        if is_h2:
            html_final.append(f'<h2 class="sub">{l_limpa}</h2>')
        else:
            html_final.append(f'<p class="txt">{l_limpa}</p>')

    if lista_aberta: html_final.append('</ul>')
    return "\n".join(html_final)

def obter_esqueleto_html(dados):
    # Pega os dados e limpa
    t = dados.get("titulo", "").strip()
    img = dados.get("imagem", "").strip()
    txt = dados.get("texto_completo", "")
    ass = dados.get("assinatura", "")
    
    cor = "rgb(7,55,99)"
    conteudo = formatar_conteudo_otimizado(txt, t)

    # Estilo concentrado no topo: o Blogger lê uma vez e aplica a tudo
    return f"""
<style>
.post-corpo {{ max-width:900px; margin:auto; font-family: 'Open Sans', Arial, sans-serif; color:{cor}; }}
.post-title, .entry-title {{ text-align:center!important; font-size:28px!important; text-transform:uppercase!important; font-weight:bold!important; margin:10px 0 25px 0!important; color:{cor}!important; }}
.img-c {{ text-align:center; margin-bottom:25px; }}
.img-p {{ width:100%; height:auto; aspect-ratio:16/9; object-fit:cover; border-radius:8px; }}
.sub {{ font-size:22px!important; text-transform:uppercase!important; font-weight:bold!important; margin-top:25px!important; margin-bottom:10px!important; text-align:left!important; color:{cor}!important; }}
.txt {{ font-size:18px!important; text-align:justify!important; line-height:1.6!important; margin-bottom:15px!important; color:{cor}!important; }}
.lst {{ margin-bottom:20px; padding-left:25px; }}
.lst li {{ font-size:18px!important; margin-bottom:8px; }}
</style>

<div class="post-corpo">
    <div class="img-c"><img src="{img}" alt="{t}" class="img-p" loading="lazy"></div>
    <div class="artigo">{conteudo}</div>
    <div style="margin-top:30px; border-top:1px solid #eee; padding-top:20px;">{ass}</div>
</div>
"""
