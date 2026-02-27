# -*- coding: utf-8 -*-

def obter_esqueleto_html(dados):

    titulo = dados.get("titulo", "")
    imagem = dados.get("imagem", "")
    texto_completo = dados.get("texto_completo", "")
    assinatura = dados.get("assinatura", "")

    # Tratamento fora da f-string (evita erro de backslash)
    texto_formatado = texto_completo.replace("\n", "<br><br>")

    FONTE_GERAL = "Arial, sans-serif"
    COR_MD = "rgb(7, 55, 99)"

    html = f"""
<style>
    h3.post-title, .post-title {{ display: none !important; visibility: hidden !important; }}
</style>

<div style="max-width:900px; margin:auto; font-family:{FONTE_GERAL}; color:{COR_MD}; line-height:1.7; text-align:justify;">

    <h1 style="text-align:center; font-size:28px; font-weight:bold; margin-bottom:20px; text-transform:uppercase;">
        {titulo}
    </h1>

    <div style="text-align:center; margin-bottom:25px;">
        <img src="{imagem}" style="width:100%; border-radius:10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); aspect-ratio:16/9; object-fit:cover;">
    </div>

    <div style="font-size:18px;">
        {texto_formatado}
    </div>

    <div style="margin-top:40px;">
        {assinatura}
    </div>

</div>
"""
    return html
