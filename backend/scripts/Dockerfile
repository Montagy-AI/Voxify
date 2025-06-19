FROM backend-base:latest

WORKDIR /app/backend/scripts

COPY ../scripts/init_db.py .
COPY ../database ../database
COPY ../data ../data 

CMD ["python", "init_db.py"]

# Build and run:
# docker build -f scripts/Dockerfile -t backend-initdb .
# docker run --rm backend-initdb