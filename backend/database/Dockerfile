FROM backend-base:latest
WORKDIR /backend/database

COPY . .

VOLUME ["/backend/data"]

# Default command for init (TODO: Adjust as needed)
CMD ["python", "-c", "from models import initialize_database; initialize_database()"]