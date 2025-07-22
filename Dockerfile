FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=backend/start.py
ENV FLASK_ENV=production

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    ffmpeg \
    libsndfile1 \
    libsqlite3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p data/voice_clones data/files/synthesis data/files/samples data/files/temp

COPY backend/ backend/
RUN chmod +x backend/start.py
EXPOSE 10000

CMD ["python", "backend/start.py"] 