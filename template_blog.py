def obter_esqueleto_html(dados):
    cor_base = "#003366"  # Azul Marinho MD
    link_wa = f"https://api.whatsapp.com/send?text=Olha que artigo interessante que li no blog do Marco Daher: {dados['titulo']} - Confira aqui!"
    
   html = f"""
<div style="color: {cor_base}; font-family: Arial, sans-serif; line-height: 1.6;">

    <h1 style="font-size: x-large; font-weight: bold; margin-bottom: 20px; text-align: center;">
        {dados['titulo'].upper()}
    </h1>

    <div style="margin-bottom: 20px; text-align: center;">
        <img src="{dados['img_topo']}"
             style="aspect-ratio: 16 / 9; border-radius: 10px; box-shadow: rgba(0,0,0,0.1) 0px 4px 8px; object-fit: cover; width: 100%;" />
    </div>

    <div style="font-size: medium; margin: 10px 0; text-align: justify;">
        {dados['intro']}
    </div>

    <p style="font-size: large; font-weight: bold; margin: 25px 0 5px;">
        {dados['sub1']}
    </p>
    <div style="font-size: medium; margin: 10px 0; text-align: justify;">
        {dados['texto1']}
    </div>

    <div style="margin: 30px 0; text-align: center;">
        <img src="{dados['img_meio']}"
             style="aspect-ratio: 16 / 9; border-radius: 10px; box-shadow: rgba(0,0,0,0.1) 0px 4px 8px; object-fit: cover; width: 100%;" />
    </div>

    <p style="font-size: large; font-weight: bold; margin: 25px 0 5px;">
        {dados['sub2']}
    </p>
    <div style="font-size: medium; margin: 10px 0; text-align: justify;">
        {dados['texto2']}
    </div>

    <p style="font-size: large; font-weight: bold; margin: 25px 0 5px;">
        {dados['sub3']}
    </p>
    <div style="font-size: medium; margin: 10px 0; text-align: justify;">
        {dados['texto3']}
    </div>

    <p style="font-size: large; font-weight: bold; margin: 25px 0 5px;">
        CONSIDERAÇÕES FINAIS
    </p>
    <div style="font-size: medium; margin: 10px 0; text-align: justify;">
        {dados['texto_conclusao']}
    </div>

    <div style="background-color: #f0f4f8; border-radius: 10px; padding: 20px; margin: 30px 0; text-align: center; border: 1px dashed {cor_base};">
        <p style="font-weight: bold; margin-bottom: 15px;">
            🚀 Gostou deste conteúdo? Não guarde só para você!
        </p>

        <a href="{link_wa}" target="_blank"
           style="background-color: #25D366; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block; margin-bottom: 10px;">
            Compartilhar no WhatsApp
        </a>

        <p style="font-size: small; margin-top: 10px;">
            Acompanhe mais dicas e novidades em nossa <b>Rede de Conhecimento MD</b>.
        </p>
    </div>

    <div>
        {dados['assinatura']}
    </div>

</div>
"""
return html
