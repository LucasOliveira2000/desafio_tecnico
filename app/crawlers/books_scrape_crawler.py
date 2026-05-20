from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from app.services.crawler_service import CrawlerService


def safe_get(locator, attr=None, default=None):
    try:
        if attr:
            return locator.first.get_attribute(attr) or default
        return locator.first.inner_text() or default
    except Exception:
        return default


class BooksScrapeCrawler:
    def __init__(self):
        self.url = "https://books.toscrape.com/catalogue/category/books_1/index.html"
        self.pagina_atual = 1
        self.service = CrawlerService()

    def run(self):
        self.service.log_inicio()

        with Stealth().use_sync(sync_playwright()) as playwright:
            browser = playwright.chromium.launch(headless=True)
            _user_agent = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
            context = browser.new_context(
                user_agent=_user_agent,
                locale="pt-BR",
                timezone_id="America/Sao_Paulo",
            )

            dados_livros = []

            page = context.new_page()
            page.goto(self.url, wait_until="load")

            qtd_paginas = int(page.locator(".current").inner_text().split()[-1])

            while self.pagina_atual <= qtd_paginas:
                self.service.log_pagina(self.pagina_atual, qtd_paginas)
                qtd_livros = len(page.query_selector_all(".product_pod"))
                self.service.log_quantidade_livros(qtd_livros)

                for livro in range(qtd_livros):
                    """
                    A atividade pede para esperar um tempo.
                    """
                    page.wait_for_timeout(2000)
                    try:
                        with page.expect_navigation():
                            page.locator(".product_pod h3 a").nth(livro).click()
                            page.wait_for_load_state("load")

                            categoria_livro = safe_get(page.locator(".breadcrumb li").nth(2))
                            caminho_imagem_livro = safe_get(page.locator(".item.active img").first, attr="src")
                            titulo_livro = safe_get(page.locator(".col-sm-6.product_main h1"))
                            valor_livro = safe_get(page.locator(".price_color"))

                            estrelas_raw = safe_get(page.locator(".star-rating"), attr="class")
                            estrelas_livro = estrelas_raw.split()[-1] if estrelas_raw else None

                            descricao_livro = safe_get(page.locator("#product_description + p"))
                            upc_livro = safe_get(page.locator(".table.table-striped tr").nth(0).locator("td"))
                            texto_avaliacao_livro = safe_get(page.locator(".table.table-striped tr").nth(5).locator("td"))

                            if not titulo_livro or not upc_livro:
                                self.service.log_erro(
                                    f"Livro {livro + 1} na página {self.pagina_atual}: "
                                    "campos obrigatórios ausentes (título ou UPC), pulando."
                                )
                                page.go_back()
                                continue

                            self.service.log_livro(livro + 1, titulo_livro, self.pagina_atual)

                            dados_livros.append({
                                "url": page.url,
                                "categoria": categoria_livro,
                                "caminho_imagem": caminho_imagem_livro,
                                "titulo": titulo_livro,
                                "valor": valor_livro,
                                "estrelas": estrelas_livro,
                                "descricao": descricao_livro,
                                "upc": upc_livro,
                                "texto_avaliacao": texto_avaliacao_livro,
                                "pagina": self.pagina_atual,
                            })

                            page.go_back()
                    except Exception as e:
                        self.service.log_erro(f"Livro {livro + 1} na página {self.pagina_atual}: {e}")
                        page.go_back()

                self.pagina_atual += 1
                if self.pagina_atual <= qtd_paginas:
                    _url_proxima = (
                        f"https://books.toscrape.com/catalogue/category/"
                        f"books_1/page-{self.pagina_atual}.html"
                    )
                    page.goto(_url_proxima, wait_until="load")

            browser.close()

        self.service.exportar_excel(dados_livros)
        self.service.exportar_csv(dados_livros)
        self.service.log_fim(len(dados_livros))