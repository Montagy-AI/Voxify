FROM backend-base:latest
WORKDIR /app/backend/database

COPY . .

VOLUME ["/app/data"]

# Default command for init (TODO: Adjust as needed)
CMD ["python", "-c", "from models import initialize_database; initialize_database()"]