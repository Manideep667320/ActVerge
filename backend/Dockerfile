# ============================================================
# ActVerge Backend Dockerfile
# ============================================================
FROM python:3.12-slim AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e ".[dev]"

RUN playwright install chromium \
    && playwright install-deps chromium

COPY actverge/ ./actverge/
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY litellm_config.yaml ./

RUN useradd --create-home --shell /bin/bash actverge \
    && chown -R actverge:actverge /app
USER actverge

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

CMD ["uvicorn", "actverge.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
