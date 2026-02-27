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
            <h2 style="text-align:left; font-family:Arial; color:{COR_MD}; 
                       font-size:{TAMANHO_H2}; font-weight:bold; 
                       margin-top:30px; margin-bottom:10px;">
                {linha_limpa}
            </h2>
            """
        else:
            html_final += f"""
            <p style="text-align:justify; font-family:Arial; color:{COR_MD}; 
                      font-size:{TAMANHO_TEXTO}; margin-bottom:15px; 
                      line-height:1.7;">
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
    h3.post-title, .post-title {{ display: none !important; }}
</style>

<div style="max-width:900px; margin:auto; font-family:Arial, sans-serif; 
            color:rgb(7, 55, 99); line-height:1.7; text-align:justify;">

    <h1 style="text-align:center; font-size:28px; font-weight:bold; 
               margin-bottom:20px; text-transform:uppercase;">
        {titulo}
    </h1>

    <div style="text-align:center; margin-bottom:25px;">
        <img src="{imagem}" 
             style="width:100%; border-radius:8px; 
                    box-shadow:0 4px 8px rgba(0,0,0,0.1); 
                    aspect-ratio:16/9; object-fit:cover;">
    </div>

    <div>
        {conteudo_formatado}
    </div>

    <div style="margin-top:40px; padding-top:20px; 
                border-top:1px solid #ddd; font-size:15px; 
                font-style:italic;">
        {assinatura}
    </div>

</div>
"""
    return html
