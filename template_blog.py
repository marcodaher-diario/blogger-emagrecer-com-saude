def obter_esqueleto_html(dados):
    cor_base = "#003366"  # Azul Marinho MD
    link_wa = f"https://api.whatsapp.com/send?text=Olha que artigo interessante que li no blog do Marco Daher: {dados['titulo']} - Confira aqui!"
    
    html = f"""
    <div style='font-family:Arial, sans-serif; color:{cor_base}; line-height: 1.6;'>
        <h1 style='text-align:center; font-size:x-large; font-weight:bold; margin-bottom:20px;'>
            {dados['titulo'].upper()}
        </h1>

        <div style='text-align:center; margin-bottom:20px;'>
            <img src='{dados['img_topo']}' style='width:100%; aspect-ratio:16/9; object-fit:cover; border-radius:10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);'/>
        </div>

        <div style='font-size:medium; text-align:justify; margin:10px 0;'>
            {dados['intro']}
        </div>

        <p style='font-size:large; font-weight:bold; text-align:left; margin:25px 0 5px 0;'>
            {dados['sub1']}
        </p>
        <div style='font-size:medium; text-align:justify; margin:10px 0;'>
            {dados['texto1']}
        </div>

        <div style='text-align:center; margin:30px 0;'>
            <img src='{dados['img_meio']}' style='width:100%; aspect-ratio:16/9; object-fit:cover; border-radius:10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);'/>
        </div>

        <p style='font-size:large; font-weight:bold; text-align:left; margin:25px 0 5px 0;'>
            {dados['sub2']}
        </p>
        <div style='font-size:medium; text-align:justify; margin:10px 0;'>
            {dados['texto2']}
        </div>

        <p style='font-size:large; font-weight:bold; text-align:left; margin:25px 0 5px 0;'>
            {dados['sub3']}
        </p>
        <div style='font-size:medium; text-align:justify; margin:10px 0;'>
            {dados['texto3']}
        </div>

        <p style='font-size:large; font-weight:bold; text-align:left; margin:25px 0 5px 0;'>
            CONSIDERAÇÕES FINAIS
        </p>
        <div style='font-size:medium; text-align:justify; margin:10px 0;'>
            {dados['texto_conclusao']}
        </div>

        <div style='background-color: #f0f4f8; border-radius: 10px; padding: 20px; margin: 30px 0; text-align: center; border: 1px dashed {cor_base};'>
            <p style='font-weight: bold; margin-bottom: 15px;'>🚀 Gostou deste conteúdo? Não guarde só para você!</p>
            
            <a href='{link_wa}' target='_blank' style='background-color: #25D366; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block; margin-bottom: 10px;'>
                Compartilhar no WhatsApp
            </a>
            
            <p style='font-size: small; margin-top: 10px;'>
                Acompanhe mais dicas e novidades em nossa <b>Rede de Conhecimento MD</b> logo abaixo.
            </p>
        </div>
        <div style='margin-top:20px; border-top: 1px solid #eee; padding-top: 10px;'>
            {dados['assinatura']}
        </div>
    </div>
    """
    return html
