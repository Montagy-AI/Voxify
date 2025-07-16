FROM python:3.11-slim AS backend-baseg
WORKDIR /backend
RUN apt-get update && apt-get install -y \
    build-essential gcc g++ libsndfile1 libsndfile1-dev curl git \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH=/backend

FROM backend-base
WORKDIR /app/backend
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y ffmpeg libsqlite3-dev && rm -rf /var/lib/apt/lists/*
COPY . .
ENV FLASK_APP=api/app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=development
CMD ["flask", "run", "--host=0.0.0.0", "--port=10000"]