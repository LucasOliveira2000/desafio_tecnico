import logging
import os
import pandas as pd
from datetime import datetime

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LOG_PATH = os.path.join(_BASE_DIR, "logs", "crawler.log")
_EXCEL_PATH = os.path.join(_BASE_DIR, "public", "assets", "books", "livros.xlsx")


class CrawlerService:
    def __init__(self):
        os.makedirs(os.path.dirname(_LOG_PATH), exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%d/%m/%Y %H:%M:%S",
            handlers=[
                logging.FileHandler(_LOG_PATH, encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def log_inicio(self):
        self.logger.info("=" * 60)
        self.logger.info("ROBÔ INICIADO")
        self.logger.info(f"Data/Hora de início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        self.logger.info("=" * 60)

    def log_fim(self, total_livros: int):
        self.logger.info("=" * 60)
        self.logger.info("ROBÔ FINALIZADO")
        self.logger.info(f"Data/Hora de fim: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        self.logger.info(f"Total de livros coletados: {total_livros}")
        self.logger.info("=" * 60)

    def log_pagina(self, pagina_atual: int, total_paginas: int):
        self.logger.info(f"--- Processando página {pagina_atual} de {total_paginas} ---")

    def log_quantidade_livros(self, qtd: int):
        self.logger.info(f"Livros encontrados na página: {qtd}")

    def log_livro(self, indice: int, titulo: str, pagina: int):
        self.logger.info(f"[Pág. {pagina}] Coletando livro #{indice}: {titulo}")

    def log_erro(self, mensagem: str):
        self.logger.error(f"ERRO: {mensagem}")

    def exportar_excel(self, dados_livros: list):
        os.makedirs(os.path.dirname(_EXCEL_PATH), exist_ok=True)
        df = pd.DataFrame(dados_livros)
        df.to_excel(_EXCEL_PATH, index=False)
        self.logger.info(f"Excel exportado com sucesso em: {_EXCEL_PATH}")
        self.logger.info(f"Total de registros exportados: {len(df)}")

    def exportar_csv(self, dados_livros: list):
        _csv_path = _EXCEL_PATH.replace(".xlsx", ".csv")
        os.makedirs(os.path.dirname(_csv_path), exist_ok=True)
        df = pd.DataFrame(dados_livros)
        df.to_csv(_csv_path, index=False, encoding="utf-8")
        self.logger.info(f"CSV exportado com sucesso em: {_csv_path}")
