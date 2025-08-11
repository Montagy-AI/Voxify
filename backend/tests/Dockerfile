FROM voxify-api:latest

WORKDIR /backend

# Copy requirements files first for better layer caching
COPY backend/requirements.txt ./requirements.txt
COPY backend/requirements-dev.txt ./requirements-dev.txt

# Install development dependencies
RUN pip install --no-cache-dir -r ./requirements-dev.txt

COPY backend/api ./api
COPY backend/data ./data
COPY backend/database ./database
COPY backend/tests ./tests

CMD ["pytest", "-v", "./tests"]