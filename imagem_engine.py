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
    # BUSCA PEXELS
    # ==========================================================

    def _buscar_pexels(self, query):

        if not self.pexels_key:
            return None

        url = "https://api.pexels.com/v1/search"
        headers = {"Authorization": self.pexels_key}
        params = {
            "query": query,
            "orientation": "landscape",
            "per_page": 10
        }

        r = requests.get(url, headers=headers, params=params)

        if r.status_code != 200:
            return None

        data = r.json()

        for foto in data.get("photos", []):
            img_url = foto["src"]["large"]

            if not self._imagem_usada_recentemente(img_url):
                self._registrar_imagem(img_url)
                return img_url

        return None

    # ==========================================================
    # BUSCA UNSPLASH
    # ==========================================================

    def _buscar_unsplash(self, query):

        if not self.unsplash_key:
            return None

        url = "https://api.unsplash.com/search/photos"

        params = {
            "query": query,
            "orientation": "landscape",
            "per_page": 10,
            "client_id": self.unsplash_key
        }

        r = requests.get(url, params=params)

        if r.status_code != 200:
            return None

        data = r.json()

        for foto in data.get("results", []):
            img_url = foto["urls"]["regular"]

            if not self._imagem_usada_recentemente(img_url):
                self._registrar_imagem(img_url)
                return img_url

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
                if "|" not in linha:
                    continue
                _, url_salva = linha.split("|")
                if "assets" in url_salva:
                    ultimo_usado = os.path.basename(url_salva)
                    break

        if ultimo_usado and ultimo_usado in arquivos:
            indice = arquivos.index(ultimo_usado) + 1
        else:
            indice = 0

        if indice >= len(arquivos):
            indice = 0

        proximo = arquivos[indice]

        caminho = f"{PASTA_ASSETS}/{proximo}"

        self._registrar_imagem(caminho)

        return caminho

    # ==========================================================
    # FUNÇÃO PRINCIPAL
    # ==========================================================

    def obter_imagem(self, titulo):

       query = f"weight loss fitness healthy lifestyle nutrition body transformation {titulo}"

        # 1️⃣ Pexels
        img = self._buscar_pexels(query)
        if img:
            return img

        # 2️⃣ Unsplash
        img = self._buscar_unsplash(query)
        if img:
            return img

        # 3️⃣ Institucional
        return self._buscar_institucional()
