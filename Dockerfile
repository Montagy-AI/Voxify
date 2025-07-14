FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=backend/start.py
ENV FLASK_ENV=production

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    ffmpeg \
    libsndfile1 \
    libsqlite3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p data/voice_clones data/files/synthesis data/files/samples data/files/temp

# Copy application code
COPY backend/ backend/

# Set permissions
RUN chmod +x backend/start.py

# Expose port
EXPOSE 8000

# Start application
CMD ["python", "backend/start.py"] 