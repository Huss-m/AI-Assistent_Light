# Lightweight Python-bild
FROM python:3.12-slim

# Basic settings
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

# Installera beroenden
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiera koden
COPY src ./src

# Cloud Run använder PORT-env variabel, default 8080 lokalt
CMD ["sh", "-c", "uvicorn web.server:app --host 0.0.0.0 --port ${PORT:-8080}"]
