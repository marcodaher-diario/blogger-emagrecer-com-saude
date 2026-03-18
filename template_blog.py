# -*- coding: utf-8 -*-
import re

def formatar_conteudo_final(texto_bruto, titulo_principal):
    if not texto_bruto: return ""
    
    linhas = [l.strip() for l in texto_bruto.split("\n") if l.strip()]
    html_final = []
    # Normalização rigorosa para o filtro de repetição
    t_ref = re.sub(r"[^\w]", "", titulo_principal.lower())
    
    lista_aberta = False

    for linha in linhas:
        # 1. Limpeza e Formatação
        l_proc = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", linha)
        l_limpa = l_proc.lstrip("#* ").strip()
        
        # 2. FILTRO ANTI-REPETIÇÃO (Comparação de caracteres alfanuméricos apenas)
        l_ref = re.sub(r"[^\w]", "", l_limpa.lower())
        if l_ref == t_ref or not l_limpa:
            continue

        # 3. Listas
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

        # 4. Detecção de Títulos (Critério do Diário de Notícias)
        # Se for curto e não terminar com ponto, tratamos como subtítulo
        palavras = re.sub(r"<.*?>", "", l_limpa).split()
        is_heading = (linha.startswith("#") or (len(palavras) <= 18 and not l_limpa.endswith(".")))

        if is_heading:
            # Se for nível 3 (###)
            if linha.startswith("###"):
                html_final.append(f'<h3 class="t3">{l_limpa}</h3>')
            else:
                # Todo o resto vira H2 (Padrão Ouro)
                html_final.append(f'<h2 class="t2">{l_limpa}</h2>')
        else:
            html_final.append(f'<p class="txt">{l_limpa}</p>')

    if lista_aberta: html_final.append('</ul>')
    return "\n".join(html_final)

def obter_esqueleto_html(dados):
    t = dados.get("titulo", "").strip()
    img = dados.get("imagem", "").strip()
    txt = dados.get("texto_completo", "")
    ass = dados.get("assinatura", "")
    cor = "rgb(7, 55, 99)"

    return f"""
<style>
/* CSS Reset para blindar contra o tema do Blogger */
.post-master {{ max-width:900px; margin:auto; font-family:sans-serif!important; color:{cor}!important; }}
.post-title, .entry-title {{ text-align:center!important; font-size:28px!important; text-transform:uppercase!important; font-weight:bold!important; margin:10px 0 25px 0!important; color:{cor}!important; display:block!important; }}
.img-c {{ text-align:center; margin-bottom:25px; }}
.img-p {{ width:100%; height:auto; aspect-ratio:16/9; object-fit:cover; border-radius:8px; }}

/* Subtítulos H2 (O impacto do Diário de Notícias) */
.t2 {{ 
    font-size:20px!important; font-weight:bold!important; text-align:left!important; 
    margin:30px 0 12px 0!important; text-transform:uppercase!important; 
    color:{cor}!important; display:block!important; line-height:1.3!important;
}}

/* Subtítulos H3 (Hierarquia menor) */
.t3 {{ 
    font-size:18px!important; font-weight:bold!important; text-align:left!important; 
    margin:25px 0 10px 0!important; color:{cor}!important; display:block!important; 
}}

/* Texto e Listas */
.txt {{ font-size:18px!important; text-align:justify!important; line-height:1.6!important; margin-bottom:15px!important; color:{cor}!important; display:block!important; }}
.lst {{ margin-bottom:20px; padding-left:25px; color:{cor}!important; }}
.lst li {{ font-size:18px!important; margin-bottom:8px; }}
.sig {{ margin-top:35px; border-top:1px solid #eee; padding-top:20px; font-style:italic; }}
</style>

<div class="post-master">
    <div class="img-c"><img src="{img}" alt="{t}" class="img-p"></div>
    <div class="artigo">
        {formatar_conteudo_final(txt, t)}
    </div>
    <div class="sig">{ass}</div>
</div>
"""
