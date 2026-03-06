# -*- coding: utf-8 -*-

def formatar_texto(texto):
    linhas = [l.strip() for l in texto.split("\n") if l.strip()]
    html_final = ""
    
    COR_MD = "rgb(7, 55, 99)"
    TAMANHO_H2 = "24px"
    TAMANHO_TEXTO = "18px"

    for linha in linhas:
        e_titulo = linha.startswith("#")
        linha_limpa = linha.strip("#* ").strip()

        if e_titulo or (len(linha_limpa.split()) <= 18 and not linha_limpa.endswith(".")):

            html_final += f"""
            <h2 style="text-align:left !important; font-family:Arial !important; color:{COR_MD} !important; 
                       font-size:{TAMANHO_H2} !important; font-weight:bold !important; 
                       margin-top:30px !important; margin-bottom:10px !important;">
                {linha_limpa}
            </h2>
            """
        else:
            html_final += f"""
            <p style="text-align:justify !important; font-family:Arial !important; color:{COR_MD} !important; 
                      font-size:{TAMANHO_TEXTO} !important; margin-bottom:15px !important; 
                      line-height:1.7 !important;">
                {linha_limpa}
            </p>
            """

    return html_final


def obter_esqueleto_html(dados):

    titulo = dados.get("titulo", "")
    imagem = dados.get("imagem", "")
    texto_completo = dados.get("texto_completo", "")
    assinatura = dados.get("assinatura", "")

    conteudo_formatado = formatar_texto(texto_completo)

    html = f"""
<style>
    /* 1. ESTILIZA O H3 NATIVO PARA PARECER O SEU H1 */
    h3.post-title, .post-title, .entry-title {{
        display: block !important;
        visibility: visible !important;
        text-align: center !important;
        margin-bottom: 20px !important;
    }}

    /* 2. ESTILIZA O LINK DENTRO DO H3 */
    h3.post-title a, .post-title a, .entry-title a {{
        color: rgb(7, 55, 99) !important;
        text-decoration: none !important;
        font-size: 28px !important;
        font-weight: bold !important;
        text-transform: uppercase !important;
        font-family: Arial !important;
    }}

    /* 3. EVITA QUE O LINK MUDE DE COR AO SER CLICADO OU AO PASSAR O MOUSE */
    h3.post-title a:visited, .post-title a:hover, .post-title a:active {{
        color: rgb(7, 55, 99) !important;
        text-decoration: none !important;
    }}
</style>

<div style="max-width:900px !important; margin:auto !important; font-family:Arial, sans-serif !important; 
            color:rgb(7, 55, 99) !important; line-height:1.7 !important; text-align:justify !important;">

    <div style="text-align:center !important; margin-bottom:25px !important;">
        <img src="{imagem}" 
             style="width:100% !important; border-radius:8px !important; 
                    box-shadow:0 4px 8px rgba(0,0,0,0.1) !important; 
                    aspect-ratio:16/9 !important; object-fit:cover !important;">
    </div>

    <div>
        {conteudo_formatado}
    </div>

    <div style="margin-top:40px !important; padding-top:20px !important; 
                border-top:1px solid #ddd !important; font-size:15px !important; 
                font-style:italic !important;">
        {assinatura}
    </div>

</div>
"""
    return html
