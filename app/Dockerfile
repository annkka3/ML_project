FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libffi-dev \
    curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Скачать модель заранее
RUN python -c "from transformers import pipeline; pipeline('translation', model='Helsinki-NLP/opus-mt-en-fr')"
RUN python -c "from transformers import pipeline; pipeline('translation', model='Helsinki-NLP/opus-mt-fr-en')"

COPY . .

EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]