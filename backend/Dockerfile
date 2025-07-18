# Production
FROM python:3.11-slim as production
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 10000
CMD ["python", "app.py"]

# Development
FROM production as development
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt