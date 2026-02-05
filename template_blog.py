def obter_esqueleto_html(dados):
    cor_base = "#003366"  # Azul Marinho MD
    link_wa = f"https://api.whatsapp.com/send?text=Olha que artigo interessante que li no blog do Marco Daher: {dados['titulo']} - Confira aqui!"
    
    html = f"""
    <div style="color: {cor_base}; font-family: Arial, sans-serif; line-height: 1.6;">
        <h1 style="font-weight: bold; margin-bottom: 20px; text-align: center;"><span style="font-size: x-large;">
            {dados['titulo'].upper()}
        </span></h1>

        <div style="margin-bottom: 20px; text-align: center;">
            <img img_topo="" src="{dados[" style="aspect-ratio: 16 / 9; border-radius: 10px; box-shadow: rgba(0, 0, 0, 0.1) 0px 4px 8px; object-fit: cover; width: 100%;" />
        </div>

        <div style="margin: 10px 0px; text-align: justify;"><span style="font-size: medium;">
            {dados['intro']}
        </span></div>

        <p style="font-weight: bold; margin: 25px 0px 5px; text-align: left;"><span style="font-size: large;">
            {dados['sub1']}
        </span></p>
        <div style="margin: 10px 0px; text-align: justify;"><span style="font-size: medium;">
            {dados['texto1']}
        </span></div>

        <div style="margin: 30px 0px; text-align: center;">
            <img img_meio="" src="{dados[" style="aspect-ratio: 16 / 9; border-radius: 10px; box-shadow: rgba(0, 0, 0, 0.1) 0px 4px 8px; object-fit: cover; width: 100%;" />
        </div>

        <p style="font-weight: bold; margin: 25px 0px 5px; text-align: left;"><span style="font-size: large;">
            {dados['sub2']}
        </span></p>
        <div style="margin: 10px 0px; text-align: justify;"><span style="font-size: medium;">
            {dados['texto2']}
        </span></div>

        <p style="font-weight: bold; margin: 25px 0px 5px; text-align: left;"><span style="font-size: large;">
            {dados['sub3']}
        </span></p>
        <div style="margin: 10px 0px; text-align: justify;"><span style="font-size: medium;">
            {dados['texto3']}
        </span></div>

        <p style="font-weight: bold; margin: 25px 0px 5px; text-align: left;"><span style="font-size: large;">
            CONSIDERAÇÕES FINAIS
        </span></p>
        <div style="margin: 10px 0px; text-align: justify;"><span style="font-size: medium;">
            {dados['texto_conclusao']}
        </span></div>

        <div style="background-color: #f0f4f8; border-radius: 10px; border: 1px dashed {cor_base}; margin: 30px 0px; padding: 20px; text-align: center;">
            <p style="font-weight: bold; margin-bottom: 15px;">🚀 Gostou deste conteúdo? Não guarde só para você!</p>
            
            <a href="{link_wa}" style="background-color: #25d366; border-radius: 5px; color: white; display: inline-block; font-weight: bold; margin-bottom: 10px; padding: 10px 20px; text-decoration: none;" target="_blank">
                Compartilhar no WhatsApp
            </a>
            
            <p style="font-size: small; margin-top: 10px;">
                Acompanhe mais dicas e novidades em nossa <b>Rede de Conhecimento MD</b> logo abaixo.
            </p>
        </div>
        <div style="border-top: 1px solid rgb(238, 238, 238); margin-top: 20px; padding-top: 10px;">
            {dados['assinatura']}
        </div>
    </div>
    """
    return html
