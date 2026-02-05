# template_blog.py - Identidade Visual Única para a Rede de Blogs MD
# Criado em: 05/02/2026

def obter_esqueleto_html(dados):
    """
    Estrutura HTML com Identidade Visual Fixa:
    - Cor: #003366 (Azul Marinho)
    - Fontes: Título (x-large), Subtítulos (large), Corpo (medium)
    - Imagens: 16:9 Centralizadas
    """
    
    cor_base = "#003366"  # Identidade Visual Fixa
    
    html = f"""
    <div style='font-family:Arial; color:{cor_base};'>
        <h1 style='text-align:center; font-size:x-large; font-weight:bold; margin-bottom:20px;'>
            {dados['titulo'].upper()}
        </h1>

        <div style='text-align:center; margin-bottom:20px;'>
            <img src='{dados['img_topo']}' style='width:100%; aspect-ratio:16/9; object-fit:cover; border-radius:10px;'/>
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
            <img src='{dados['img_meio']}' style='width:100%; aspect-ratio:16/9; object-fit:cover; border-radius:10px;'/>
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

        <div style='margin-top:20px; color:{cor_base}; border-top: 1px solid #eee; padding-top: 10px;'>
            {dados['assinatura']}
        </div>
    </div>
    """
    return html
