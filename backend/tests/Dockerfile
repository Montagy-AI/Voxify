FROM voxify-api:latest

WORKDIR /backend

COPY backend/api ./api
COPY backend/data ./data
COPY backend/database ./database
COPY backend/tests ./tests

CMD ["python", "-m", "pytest", "discover", "-s", "test"]