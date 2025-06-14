FROM python:3.11-slim

WORKDIR /app/database

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt
    
COPY . .

# Optional: create volume mount point
VOLUME ["/app/data"]

# Default command for init (TODO: Adjust as needed)
CMD ["python", "-c", "from models import initialize_database; initialize_database()"]
