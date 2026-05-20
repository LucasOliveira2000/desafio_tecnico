# Books Scraper — Desafio Técnico Trainee

Scraper automatizado que coleta dados estruturados de todos os livros do site [books.toscrape.com](https://books.toscrape.com), itera por todas as páginas do catálogo e exporta os resultados em Excel e CSV.

---

## Sumário

1. [Pré-requisitos](#pré-requisitos)
2. [Como Rodar Localmente](#como-rodar-localmente)
3. [Estrutura dos Dados Extraídos](#estrutura-dos-dados-extraídos)
4. [Como o Pipeline CI/CD Funciona](#como-o-pipeline-cicd-funciona)
5. [Estrutura do Projeto](#estrutura-do-projeto)
6. [Decisões Técnicas](#decisões-técnicas)
7. [O que Faria Diferente com Mais Tempo](#o-que-faria-diferente-com-mais-tempo)
8. [Uso de IA no Desafio](#uso-de-ia-no-desafio)

---

## Pré-requisitos

- Python 3.13+
- Docker e Docker Compose (para execução containerizada)

---

## Como Rodar Localmente

### Sem Docker

```bash
# 1. Clonar o repositório
git clone <url-do-repo>
cd Desafio_Trainee

# 2. Criar e ativar o ambiente virtual
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Instalar o browser Chromium do Playwright
playwright install chromium

# 5. Executar o scraper
python main.py
```

Os arquivos de saída serão gerados em:
- `app/public/assets/books/livros.xlsx`
- `app/public/assets/books/livros.csv`
- `app/logs/crawler.log`

### Com Docker

```bash
# Build da imagem
docker build -t books-scraper .

# Execução (monta saída no host)
docker run --name books-scraper

# ver logs
docker logs -f scraper
```

## Estrutura dos Dados Extraídos

### Schema dos campos

| Campo             | Tipo      | Descrição                                    | Exemplo                                    |
|-------------------|-----------|----------------------------------------------|--------------------------------------------|
| `url`             | `string`  | URL completa da página do livro              | `https://books.toscrape.com/catalogue/...` |
| `categoria`       | `string`  | Categoria do livro                           | `Mystery`                                  |
| `caminho_imagem`  | `string`  | Caminho relativo da imagem de capa           | `../../media/cache/2c/da/2cda...jpg`       |
| `titulo`          | `string`  | Título completo do livro                     | `A Light in the Attic`                     |
| `valor`           | `string`  | Preço com símbolo da moeda                   | `£51.77`                                   |
| `estrelas`        | `string`  | Avaliação por extenso (classe CSS mapeada)   | `Three`                                    |
| `descricao`       | `string`  | Sinopse/descrição do livro                   | `It's hard to imagine...`                  |
| `upc`             | `string`  | Universal Product Code                       | `a897fe39b1053632`                         |
| `texto_avaliacao` | `string`  | Disponibilidade em estoque                   | `In stock`                                 |
| `pagina`          | `integer` | Número da página do catálogo onde foi colhido | `1`                                       |

### Exemplo de registro (JSON equivalente)

```json
{
  "url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
  "categoria": "Poetry",
  "caminho_imagem": "../../media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg",
  "titulo": "A Light in the Attic",
  "valor": "£51.77",
  "estrelas": "Three",
  "descricao": "It's hard to imagine a world without A Light in the Attic...",
  "upc": "a897fe39b1053632",
  "texto_avaliacao": "In stock",
  "pagina": 1
}
```

### Saídas geradas

| Arquivo                                | Formato | Finalidade                                      |
|----------------------------------------|---------|-------------------------------------------------|
| `app/public/assets/books/livros.xlsx`  | Excel   | Análise ad hoc, fácil de abrir no Excel/Sheets  |
| `app/public/assets/books/livros.csv`   | CSV     | Integração com pipelines de dados e ferramentas de BI |
| `app/logs/crawler.log`                 | Log     | Rastreabilidade passo a passo da execução       |

---

## Como o Pipeline CI/CD Funciona

O arquivo `.gitlab-ci.yml` define 4 estágios que rodam em sequência em cada push:

### Stage 1 — `lint`

- **Ferramenta:** `flake8` com configuração em `.flake8`
- **O que faz:** Verifica estilo e qualidade do código Python (PEP 8): imports não usados, linhas muito longas, erros de sintaxe
- **Falha se:** Houver qualquer violação de lint
- **Cache:** Dependências pip cacheadas por branch para acelerar builds subsequentes

### Stage 2 — `test`

- **Ferramenta:** `pytest`
- **O que faz:** Executa todos os testes em `tests/` com saída verbosa
- **Falha se:** Algum teste falhar
- **Cobertura:** Testa os métodos de logging (`log_inicio`, `log_fim`, `log_pagina`, `log_livro`, `log_erro`) e de exportação (`exportar_excel`, `exportar_csv`) com mocks — sem dependência de rede ou disco

### Stage 3 — `build`

- **Ferramenta:** Docker-in-Docker (`docker:24.0.5-dind`)
- **O que faz:** Constrói a imagem com o `Dockerfile` multi-stage e faz push para o GitLab Container Registry
- **Variáveis usadas (injetadas automaticamente pelo GitLab):**
  - `$CI_REGISTRY` — endereço do registry
  - `$CI_REGISTRY_USER` / `$CI_REGISTRY_PASSWORD` — credenciais
  - `$CI_REGISTRY_IMAGE` — nome completo da imagem
  - `$CI_COMMIT_SHORT_SHA` — tag imutável baseada no commit
- **Tags geradas:** `<image>:<commit-sha>` e `<image>:latest`

### Stage 4 — `deploy`

- **O que faz:** Simula o comando de atualização de serviço no AWS ECS
- **Condição:** Roda **somente** na branch `main`
- **Em produção:** Substituir os `echo` pelo AWS CLI real, com as variáveis `$ECS_CLUSTER` e `$ECS_SERVICE` configuradas nas CI/CD Variables do GitLab

---

## Estrutura do Projeto

```
Desafio_Trainee/
├── app/
│   ├── crawlers/
│   │   └── books_scrape_crawler.py   # Lógica de navegação e extração com Playwright
│   ├── logs/
│   │   └── crawler.log               # Gerado em tempo de execução
│   ├── public/
│   │   └── assets/books/
│   │       ├── livros.xlsx           # Saída Excel
│   │       └── livros.csv            # Saída CSV
│   └── services/
│       └── crawler_service.py        # Logging estruturado + exportação de dados
├── tests/
│   ├── __init__.py
│   └── test_crawler_service.py       # Testes unitários (pytest + unittest.mock)
├── .flake8                           # Configuração do linter
├── .gitlab-ci.yml                    # Pipeline CI/CD (lint → test → build → deploy)
├── .gitignore
├── docker-compose.yml                # Orquestração local
├── Dockerfile                        # Build multi-stage, usuário não-root
├── main.py                           # Ponto de entrada
├── pytest.ini                        # Configuração do pytest
└── requirements.txt                  # Dependências Python
```

---

## Decisões Técnicas

### Por que Playwright em vez de `requests` + `BeautifulSoup`?

O `books.toscrape.com` é estático e poderia ser raspado com `requests` + `BeautifulSoup`. Optei pelo **Playwright** para demonstrar capacidade de lidar com páginas dinâmicas (carregadas via JavaScript), que é o cenário real da maioria dos projetos de RPA/Crawler em produção. A navegação real também permite simular melhor o comportamento de um usuário humano, reduzindo chances de bloqueio.

### Por que Python e não Go?

Python é a linguagem dominante em automação e RPA, com o ecossistema mais maduro (Playwright, Selenium, Scrapy). A curva de aprendizado mais baixa e a vasta documentação disponível tornam o desenvolvimento e a manutenção mais ágeis.

### Separação entre Crawler e Service

Seguir o princípio de **Single Responsibility**: a lógica de navegação e extração fica no crawler, enquanto logging e exportação de dados ficam no `CrawlerService`. Isso facilita testes unitários (o service pode ser testado sem instanciar um browser) e reuso em outros crawlers.

### Exportação Excel + CSV

O Excel é o formato mais amigável para análise ad hoc por times não-técnicos. O CSV é gerado em paralelo para compatibilidade com pipelines de dados, bancos de dados e ferramentas de BI (Power BI, Metabase, etc.).

### Dockerfile multi-stage

- **Stage `builder`:** instala as dependências pip num diretório isolado
- **Stage `runner`:** copia apenas os pacotes compilados, sem pip, cache de build ou ferramentas de desenvolvimento

Resultado: imagem final menor e menor superfície de ataque.

### Usuário não-root no container

Boa prática de segurança: mesmo que um processo seja comprometido dentro do container, ele não terá permissões de root no sistema host.

---

## O que Faria Diferente com Mais Tempo

- **Scraping paralelo:** Usar `asyncio` + `playwright.async_api` para processar múltiplas páginas simultaneamente, reduzindo o tempo total de coleta de horas para minutos
- **Anti-bot avançado:** Rotação de proxies, fingerprint de browser aleatório, delays com distribuição probabilística humana
- **Persistência em banco de dados:** PostgreSQL com SQLAlchemy para armazenar histórico de coletas e detectar variações de preço ao longo do tempo
- **Observabilidade:** Integrar OpenTelemetry + Grafana/Prometheus para métricas de execução em tempo real (livros/minuto, taxa de erro, duração por página)
- **IA na extração:** Usar um LLM (OpenAI / Mistral) para parsear descrições em texto livre e extrair informações estruturadas: gênero literário real, público-alvo, palavras-chave
- **Exportação JSON:** Gerar um `.json` estruturado para consumo direto por APIs

---

## Uso de IA no Desafio

| Tarefa | Ferramenta | O que funcionou |
|--------|------------|-----------------|
| Geração do `CrawlerService` com logging para arquivo e console simultâneos | GitHub Copilot (Claude Sonnet 4.6) | Funcionou na primeira tentativa; estrutura de handlers correta |
| Configuração do `Dockerfile` multi-stage com Playwright e usuário não-root | GitHub Copilot | Gerou a estrutura correta; ajuste manual nas permissões do diretório de browsers (`PLAYWRIGHT_BROWSERS_PATH`) |
| Geração do `.gitlab-ci.yml` com cache de pip e regras por branch | GitHub Copilot | Estágios e variáveis corretos; revisão manual das regras de deploy |
| Testes unitários com `pytest` e `unittest.mock` (patches de logging e pandas) | GitHub Copilot | Gerou fixtures e patches funcionais; ajuste manual na asserção do caminho CSV |
| Documentação do README | GitHub Copilot | Estrutura completa gerada; revisão e personalização manual de conteúdo |

A IA foi usada como **aceleradora de scaffolding** — especialmente para infraestrutura (Docker, CI/CD) e testes, onde a estrutura é conhecida mas verbosa. Todo código gerado somente foi revisado, executado e ajustado manualmente antes de ser incorporado ao projeto.
