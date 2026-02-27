# ==========================================
# CONFIGURAÇÕES GERAIS DO BLOG
# ==========================================

BLOG_ID = "5251820458826857223"

# ==========================================
# AGENDA DE PUBLICAÇÃO (Horário Brasil)
# ==========================================

AGENDA_POSTAGENS = {
    "15:00": "auto"  # Terça, Quinta e Sábado (controlado pelo workflow)
}

JANELA_MINUTOS = 10

# ==========================================
# CATEGORIAS EDITORIAIS
# ==========================================

CATEGORIAS_EDITORIAIS = [
    "emagrecimento saudável",
    "metabolismo",
    "nutrição",
    "exercícios",
    "vida saudável",
    "receitas funcionais",
    "novidades e técnicas atuais"
]

# ==========================================
# CONFIGURAÇÃO DE CONTROLE
# ==========================================

ARQUIVO_CONTROLE_AGENDAMENTO = "controle_agendamentos.txt"
ARQUIVO_CONTROLE_TEMAS = "controle_temas_usados.txt"
ARQUIVO_CONTROLE_IMAGENS = "controle_imagens.txt"

DIAS_BLOQUEIO_TEMA = 20
DIAS_BLOQUEIO_IMAGEM = 30

# ==========================================
# CONFIGURAÇÃO GEMINI
# ==========================================

MODELO_GEMINI = "models/gemini-2.5-flash"

MIN_PALAVRAS = 800
MAX_PALAVRAS = 1000

# ==========================================
# BLOCO FIXO FINAL - ASSINATURA
# ==========================================

BLOCO_FIXO_FINAL = """
<div class="footer-marco-daher" style="background-color: #e1f5fe; border-radius: 15px; border: 1px solid rgb(179, 229, 252); color: #073763; font-family: Arial, Helvetica, sans-serif; line-height: 1.4; margin-top: 10px; padding: 25px; text-align: center;">
  
  <p style="font-size: x-small; font-weight: bold; margin-top: 0px; text-align: right;">
    <i>Por: Marco Daher<br />Todos os Direitos Reservados<br />©MarcoDaher2026</i>
  </p>

  <div style="margin-bottom: 20px; text-align: center;">
    <p style="font-weight: bold; margin-bottom: 10px;">🚀 Gostou deste conteúdo? Compartilhe!</p>
    <a href="https://api.whatsapp.com/send?text=Confira este artigo incrível no blog Emagrecer com Saúde!" 
       style="background-color: #25d366; border-radius: 5px; color: white; display: inline-block; font-weight: bold; padding: 10px 20px; text-decoration: none;" 
       target="_blank">
        Compartilhar no WhatsApp
    </a>
  </div>

  <p style="font-size: 16px; font-weight: bold; margin-bottom: 20px;">
    O conhecimento é o combustível para o Sucesso.
  </p>

  <hr style="margin: 20px 0px;" />

  <p style="font-size: 14px; font-weight: bold;">
    Caso queira contribuir com o meu Trabalho, use a CHAVE PIX abaixo:
  </p>

  <button onclick="navigator.clipboard.writeText('marco.caixa104@gmail.com'); alert('Chave PIX copiada!');"
          style="background-color: #0288d1; border-radius: 8px; border: none; color: white; cursor: pointer; font-size: 14px; font-weight: bold; padding: 12px 20px;">
    Copiar Chave PIX: marco.caixa104@gmail.com
  </button>
</div>
"""
