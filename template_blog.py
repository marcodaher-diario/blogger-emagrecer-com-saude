def obter_esqueleto_html(dados):
    cor_base = "#003366"
    return f"""
    <div style='font-family:Arial; color:{cor_base};'>
        <h1 style='text-align:center; font-size:x-large; font-weight:bold;'>{dados['titulo'].upper()}</h1>
        <div style='text-align:center; margin:20px 0;'><img src='{dados['img_topo']}' style='width:100%; aspect-ratio:16/9; object-fit:cover; border-radius:10px;'/></div>
        <div style='font-size:medium; text-align:justify;'>{dados['intro']}</div>
        <p style='font-size:large; font-weight:bold; text-align:left; margin-top:25px;'>{dados['sub1']}</p>
        <div style='font-size:medium; text-align:justify;'>{dados['texto1']}</div>
        <div style='text-align:center; margin:30px 0;'><img src='{dados['img_meio']}' style='width:100%; aspect-ratio:16/9; object-fit:cover; border-radius:10px;'/></div>
        <p style='font-size:large; font-weight:bold; text-align:left; margin-top:25px;'>{dados['sub2']}</p>
        <div style='font-size:medium; text-align:justify;'>{dados['texto2']}</div>
        <p style='font-size:large; font-weight:bold; text-align:left; margin-top:25px;'>{dados['sub3']}</p>
        <div style='font-size:medium; text-align:justify;'>{dados['texto3']}</div>
        <p style='font-size:large; font-weight:bold; text-align:left; margin-top:25px;'>CONSIDERAÇÕES FINAIS</p>
        <div style='font-size:medium; text-align:justify;'>{dados['texto_conclusao']}</div>
        <div style='margin-top:20px; border-top:1px solid #eee; padding-top:10px;'>{dados['assinatura']}</div>
    </div>
    """
