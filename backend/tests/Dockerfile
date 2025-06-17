FROM backend-base:latest

WORKDIR /app/backend

COPY ../api ./api
COPY ../data ./data
COPY ../database ./database

COPY . ./test

# Run tests by default (override with docker run if needed)
CMD ["python", "-m", "unittest", "discover", "-s", "test"]