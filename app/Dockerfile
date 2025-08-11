
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    TOKENIZERS_PARALLELISM=false \
    HF_HOME=/opt/hf-cache \
    TRANSFORMERS_CACHE=/opt/hf-cache

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip && \
    pip install -r requirements.txt

RUN mkdir -p $TRANSFORMERS_CACHE && \
    python - <<'PY'
from transformers import pipeline
pipeline("translation", model="Helsinki-NLP/opus-mt-en-fr")
pipeline("translation", model="Helsinki-NLP/opus-mt-fr-en")
PY

COPY . .

RUN useradd -m appuser && chown -R appuser:appuser /app $TRANSFORMERS_CACHE
USER appuser

EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
