# -*- coding: utf-8 -*-

import os
import requests
from datetime import datetime
from configuracoes import ARQUIVO_CONTROLE_IMAGENS, DIAS_BLOQUEIO_IMAGEM

PASTA_ASSETS = "assets"

class ImageEngine:

    def __init__(self):
        self.pexels_key = os.getenv("PEXELS_API_KEY")
        self.unsplash_key = os.getenv("UNSPLASH_API_KEY")

    # ==========================================================
    # CONTROLE DE REPETIÇÃO
    # ==========================================================

    def _imagem_usada_recentemente(self, url):
        if not os.path.exists(ARQUIVO_CONTROLE_IMAGENS):
            return False

        hoje = datetime.utcnow()

        with open(ARQUIVO_CONTROLE_IMAGENS, "r", encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if "|" not in linha:
                    continue

                data_str, url_salva = linha.split("|")

                try:
                    data_img = datetime.strptime(data_str, "%Y-%m-%d")
                except:
                    continue

                if url_salva == url and (hoje - data_img).days < DIAS_BLOQUEIO_IMAGEM:
                    return True

        return False

    def _registrar_imagem(self, url):
        hoje = datetime.utcnow().strftime("%Y-%m-%d")
        with open(ARQUIVO_CONTROLE_IMAGENS, "a", encoding="utf-8") as f:
            f.write(f"{hoje}|{url}\n")

    # ==========================================================
    # BUSCA PEXELS (OTIMIZADA)
    # ==========================================================

    def _buscar_pexels(self, query):
        if not self.pexels_key:
            return None

        url = "https://api.pexels.com/v1/search"
        headers = {"Authorization": self.pexels_key}
        params = {
            "query": query,
            "orientation": "landscape",
            "per_page": 15, # Aumentei para ter mais opções de filtro
            "size": "large"
        }

        try:
            r = requests.get(url, headers=headers, params=params, timeout=10)
            if r.status_code != 200:
                return None

            data = r.json()
            for foto in data.get("photos", []):
                img_url = foto["src"]["large2x"] # Versão de alta qualidade

                if not self._imagem_usada_recentemente(img_url):
                    self._registrar_imagem(img_url)
                    return img_url
        except:
            return None

        return None

    # ==========================================================
    # BUSCA UNSPLASH (OTIMIZADA)
    # ==========================================================

    def _buscar_unsplash(self, query):
        if not self.unsplash_key:
            return None

        url = "https://api.unsplash.com/search/photos"
        params = {
            "query": query,
            "orientation": "landscape",
            "per_page": 15,
            "client_id": self.unsplash_key
        }

        try:
            r = requests.get(url, params=params, timeout=10)
            if r.status_code != 200:
                return None

            data = r.json()
            for foto in data.get("results", []):
                img_url = foto["urls"]["regular"]

                if not self._imagem_usada_recentemente(img_url):
                    self._registrar_imagem(img_url)
                    return img_url
        except:
            return None

        return None

    # ==========================================================
    # IMAGEM INSTITUCIONAL (ASSETS)
    # ==========================================================

    def _buscar_institucional(self):
        if not os.path.exists(PASTA_ASSETS):
            return None

        arquivos = sorted([
            f for f in os.listdir(PASTA_ASSETS)
            if f.lower().endswith(".jpg")
        ])

        if not arquivos:
            return None

        ultimo_usado = None
        if os.path.exists(ARQUIVO_CONTROLE_IMAGENS):
            with open(ARQUIVO_CONTROLE_IMAGENS, "r", encoding="utf-8") as f:
                linhas = f.readlines()

            for linha in reversed(linhas):
                linha = linha.strip()
                if "|" not in linha: continue
                _, url_salva = linha.split("|")
                if "assets" in url_salva:
                    ultimo_usado = os.path.basename(url_salva)
                    break

        indice = (arquivos.index(ultimo_usado) + 1) if ultimo_usado in arquivos else 0
        if indice >= len(arquivos): indice = 0

        proximo = arquivos[indice]
        caminho = f"{PASTA_ASSETS}/{proximo}"
        self._registrar_imagem(caminho)
        return caminho

    # ==========================================================
    # FUNÇÃO PRINCIPAL (FOCO EM QUALIDADE VISUAL)
    # ==========================================================

    def obter_imagem(self, titulo):
        """
        Monta uma query profissional e busca nos bancos de imagens gratuitos.
        """
        # Adicionando termos de estilo para evitar fotos com cara de "amadoras"
        estilo_visual = "minimalist, professional photography, high-end, soft lighting, clean background"
        nicho = "healthy lifestyle, fitness, nutrition"
        
        # Query refinada em inglês (Pexels e Unsplash funcionam muito melhor assim)
        query_profissional = f"{estilo_visual}, {nicho}, {titulo}"

        print(f"Buscando imagem profissional para: {titulo}...")

        # 1️⃣ Pexels
        img = self._buscar_pexels(query_profissional)
        if img:
            return img

        # 2️⃣ Unsplash
        img = self._buscar_unsplash(query_profissional)
        if img:
            return img

        # 3️⃣ Fallback para Assets Locais
        print("Bancos de imagens falharam ou repetiram. Usando imagem institucional...")
        return self._buscar_institucional()
