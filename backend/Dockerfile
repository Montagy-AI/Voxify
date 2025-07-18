FROM python:3.11-slim AS production

RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libsndfile1-dev \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000

ENV FLASK_APP=api:create_app
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=10000

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=10000"]