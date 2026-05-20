import pytest
from unittest.mock import patch, MagicMock


# ──────────────────────────────────────────────────────────────
# Fixture: cria uma instância de CrawlerService sem efeitos
# colaterais (sem criar arquivos de log nem configurar handlers).
# O logger é substituído por um MagicMock para inspeção.
# ──────────────────────────────────────────────────────────────
@pytest.fixture
def service():
    with patch("app.services.crawler_service.os.makedirs"), \
         patch("app.services.crawler_service.logging.basicConfig"), \
         patch("app.services.crawler_service.logging.FileHandler", return_value=MagicMock()):
        from app.services.crawler_service import CrawlerService
        svc = CrawlerService()
        svc.logger = MagicMock()
        return svc


# ──────────────────────────────────────────────────────────────
# Testes de logging
# ──────────────────────────────────────────────────────────────
def test_log_inicio_chama_logger(service):
    service.log_inicio()
    assert service.logger.info.called


def test_log_fim_registra_total_de_livros(service):
    service.log_fim(42)
    chamadas = " ".join(str(c) for c in service.logger.info.call_args_list)
    assert "42" in chamadas


def test_log_pagina_registra_pagina_atual_e_total(service):
    service.log_pagina(3, 50)
    chamadas = " ".join(str(c) for c in service.logger.info.call_args_list)
    assert "3" in chamadas
    assert "50" in chamadas


def test_log_quantidade_livros_registra_valor(service):
    service.log_quantidade_livros(20)
    chamadas = " ".join(str(c) for c in service.logger.info.call_args_list)
    assert "20" in chamadas


def test_log_livro_registra_titulo_e_pagina(service):
    service.log_livro(5, "Sapiens", 2)
    chamadas = " ".join(str(c) for c in service.logger.info.call_args_list)
    assert "Sapiens" in chamadas
    assert "2" in chamadas


def test_log_erro_usa_nivel_error(service):
    service.log_erro("conexão recusada")
    service.logger.error.assert_called_once()
    mensagem = service.logger.error.call_args[0][0]
    assert "conexão recusada" in mensagem


# ──────────────────────────────────────────────────────────────
# Testes de exportação
# ──────────────────────────────────────────────────────────────
def test_exportar_excel_cria_dataframe_e_salva(service):
    with patch("app.services.crawler_service.pd.DataFrame") as mock_df_class, \
         patch("app.services.crawler_service.os.makedirs"):
        mock_df = MagicMock()
        mock_df.__len__ = MagicMock(return_value=2)
        mock_df_class.return_value = mock_df

        dados = [
            {"titulo": "Livro A", "valor": "£10.00"},
            {"titulo": "Livro B", "valor": "£20.00"},
        ]
        service.exportar_excel(dados)

        mock_df_class.assert_called_once_with(dados)
        mock_df.to_excel.assert_called_once()
        _, kwargs = mock_df.to_excel.call_args
        assert kwargs["index"] is False


def test_exportar_excel_aceita_lista_vazia(service):
    with patch("app.services.crawler_service.pd.DataFrame") as mock_df_class, \
         patch("app.services.crawler_service.os.makedirs"):
        mock_df = MagicMock()
        mock_df.__len__ = MagicMock(return_value=0)
        mock_df_class.return_value = mock_df

        service.exportar_excel([])

        mock_df_class.assert_called_once_with([])


def test_exportar_csv_cria_dataframe_e_salva(service):
    with patch("app.services.crawler_service.pd.DataFrame") as mock_df_class, \
         patch("app.services.crawler_service.os.makedirs"):
        mock_df = MagicMock()
        mock_df_class.return_value = mock_df

        dados = [{"titulo": "Livro A", "valor": "£10.00"}]
        service.exportar_csv(dados)

        mock_df_class.assert_called_once_with(dados)
        mock_df.to_csv.assert_called_once()
        _, kwargs = mock_df.to_csv.call_args
        assert kwargs["index"] is False
        assert kwargs["encoding"] == "utf-8"


def test_exportar_csv_usa_caminho_com_extensao_csv(service):
    with patch("app.services.crawler_service.pd.DataFrame") as mock_df_class, \
         patch("app.services.crawler_service.os.makedirs"):
        mock_df = MagicMock()
        mock_df_class.return_value = mock_df

        service.exportar_csv([{"titulo": "X"}])

        caminho = mock_df.to_csv.call_args[0][0]
        assert caminho.endswith(".csv")
