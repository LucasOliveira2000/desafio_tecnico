# ==============================================================
# Stage 1 — builder
# ==============================================================
FROM python:3.13-slim AS builder

WORKDIR /deps

COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/deps/packages -r requirements.txt


# ==============================================================
# Stage 2 — runner
# ==============================================================
FROM python:3.13-slim AS runner

# Copia pacotes Python instalados
COPY --from=builder /deps/packages /usr/local

# Caminho dos browsers do Playwright
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# playwright install-deps já resolve todas as libs do Chromium automaticamente
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && playwright install-deps chromium \
    && playwright install chromium \
    && chmod -R 755 /ms-playwright

WORKDIR /app

COPY . .

RUN groupadd -r crawler \
    && useradd -r -g crawler -d /app -s /sbin/nologin crawler \
    && chown -R crawler:crawler /app

USER crawler

EXPOSE 8080

CMD ["python", "main.py"]