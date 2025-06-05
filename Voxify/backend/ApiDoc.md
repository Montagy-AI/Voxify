# Voxify RESTful API Architecture Documentation

## Architecture Overview

Voxify adopts a pure RESTful architecture design, providing a unified, easy-to-use, and scalable HTTP/JSON API for all clients and internal services. All service-to-service and client-to-service communication is performed via RESTful API. There is no gRPC in the system.

- **Flask REST API Gateway**: Provides HTTP/REST interfaces for web clients, mobile applications, admin interfaces, and internal service communication.
- **RESTful Client Support**: All clients and internal services use RESTful API (HTTP/JSON) for communication.

### Architecture Layers
```
┌─────────────────────────────────────────────────────────────┐
│                    Client Layer                             │
│  Web Apps │  Mobile Apps │  Admin UI  │  Internal Services  │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                Flask REST API Gateway (HTTP/JSON)           │
│   - Authentication & Authorization                          │
│   - Request Validation                                      │
│   - Response Formatting                                    │
│   - Admin Interface                                        │
│   - Middleware Layer:                                      │
│     * JWT Authentication                                   │
│     * CORS & Rate Limiting                                 │
│     * Error Handling                                       │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                 Data Storage Layer                          │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   SQLite    │  │    Redis    │  │File Storage │         │
│  │User Data &  │  │ Cache &     │  │   MinIO/S3  │         │
│  │ Metadata    │  │ Sessions    │  │             │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐                          │
│  │Model Storage│  │Vector Database│                        │
│  │Voice Models │  │ Chroma/Qdrant │                        │
│  │ & AI Assets │  │Voice Embeddings│                       │
│  └─────────────┘  └─────────────┘                          │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                 Message Queue Layer                         │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐                          │
│  │   Celery    │  │  RabbitMQ   │                          │
│  │Async Tasks  │  │Message Broker│                         │
│  │ Worker      │  │             │                          │
│  └─────────────┘  └─────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Technology Stack Details

### RESTful API Gateway Layer
```python
# Core Framework
Flask==2.3.3
Flask-RESTful==0.3.10
Flask-JWT-Extended==4.5.3
Flask-CORS==4.0.0
Flask-Limiter==3.5.0
```

### Data Storage & Infrastructure
```python
# Database
SQLite==3.40.0
sqlite3 (Python built-in)

# Vector Database
chromadb==0.4.15
sentence-transformers==2.2.2  # for voice embeddings

# File Storage
MinIO (S3-compatible)

# Message Queue
RabbitMQ==3.11
Celery==5.3.1

# Monitoring & Logging
prometheus-client==0.17.1
structlog==23.1.0
```

---

## RESTful API Endpoints 

### Authentication
- POST /api/v1/auth/register
- POST /api/v1/auth/login
- POST /api/v1/auth/refresh

### Voice Sample Management
- POST /api/v1/voice/samples
- GET /api/v1/voice/samples
- GET /api/v1/voice/samples/{sample_id}
- DELETE /api/v1/voice/samples/{sample_id}
- POST /api/v1/voice/samples/{sample_id}/train

### Text-to-Speech (TTS)
- POST /api/v1/tts/synthesize
- POST /api/v1/tts/synthesize/async
- GET /api/v1/tts/synthesize/stream

### Job Management
- GET /api/v1/jobs
- GET /api/v1/jobs/{job_id}
- POST /api/v1/jobs/{job_id}/cancel
- GET /api/v1/jobs/{job_id}/progress/ws

### File Management
- GET /api/v1/files/audio/{file_id}
- GET /api/v1/files/{file_id}/info

### Admin Endpoints
- GET /api/v1/admin/stats
- GET /api/v1/admin/users
- GET/PUT /api/v1/admin/config

---

## API Response Format

All API responses follow a unified format:
```json
{
    "success": true/false,
    "data": {},
    "message": "Operation description",
    "error": {
        "code": "ERROR_CODE",
        "message": "Error description",
        "details": "Detailed information"
    }
}
```

---

## Pagination
All list APIs support pagination:
```json
{
    "pagination": {
        "page": 1,
        "page_size": 20,
        "total_count": 100,
        "total_pages": 5,
        "has_next": true,
        "has_prev": false
    }
}
```

---

## Authentication
- REST API uses JWT Bearer Token for all user and service authentication.
- Admin endpoints require additional permission verification.

---

## Rate Limiting
- Maximum 100 requests per minute per user
- File upload limit: 50MB/file, maximum 100 files per day
- Speech synthesis limit: maximum 1000 syntheses per day

---

## Project Structure Example
```
backend/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── voice.py         # Voice endpoints
│   │   ├── tts.py           # TTS endpoints
│   │   ├── jobs.py          # Job endpoints
│   │   ├── files.py         # File endpoints
│   │   └── admin.py         # Admin endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py      # Request models
│   │   └── responses.py     # Response models
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth.py          # JWT authentication middleware
│   │   └── error_handler.py # Error handling
│   └── utils/
│       ├── __init__.py
│       ├── validators.py    # Request validation
│       └── formatters.py    # Response formatting
├── tests/
├── requirements.txt
└── app.py
```

---




#### Synchronous Text-to-Speech with Word/Syllable Mapping
```http
POST /api/v1/tts/synthesize
Content-Type: application/json
Authorization: Bearer <access_token>

{
    "text": "Hello world, this is a test.",
    "voice_id": "vs_1234567890",
    "config": {
        "output_format": "wav",
        "sample_rate": 22050,
        "include_timestamps": true,
        "timestamp_granularity": "both"
    }
}
```

**Response**:
```json
{
    "success": true,
    "data": {
        "synthesis_id": "syn_1234567890",
        "audio_url": "https://api.voxify.com/files/audio/syn_1234567890.wav",
        "duration": 3.2,
        "format": "wav",
        "sample_rate": 22050,
        "word_timestamps": [
            {
                "word": "Hello",
                "start_time": 0.0,
                "end_time": 0.5
            },
            {
                "word": "world",
                "start_time": 0.6,
                "end_time": 1.1
            },
            {
                "word": "this",
                "start_time": 1.3,
                "end_time": 1.6
            },
            {
                "word": "is",
                "start_time": 1.7,
                "end_time": 1.9
            },
            {
                "word": "a",
                "start_time": 2.0,
                "end_time": 2.1
            },
            {
                "word": "test",
                "start_time": 2.2,
                "end_time": 2.7
            }
        ],
        "syllable_timestamps": [
            {
                "syllable": "Hel",
                "start_time": 0.0,
                "end_time": 0.2
            },
            {
                "syllable": "lo",
                "start_time": 0.2,
                "end_time": 0.5
            },
            {
                "syllable": "wor",
                "start_time": 0.6,
                "end_time": 0.8
            },
            {
                "syllable": "ld",
                "start_time": 0.8,
                "end_time": 1.1
            },
            {
                "syllable": "this",
                "start_time": 1.3,
                "end_time": 1.6
            },
            {
                "syllable": "is",
                "start_time": 1.7,
                "end_time": 1.9
            },
            {
                "syllable": "a",
                "start_time": 2.0,
                "end_time": 2.1
            },
            {
                "syllable": "test",
                "start_time": 2.2,
                "end_time": 2.7
            }
        ]
    },
    "message": "Speech synthesis completed with timestamps"
}
```

#### Configuration Options for Timestamp Granularity

**Word-only timestamps**:
```json
{
    "config": {
        "timestamp_granularity": "word",
        "include_timestamps": true
    }
}
```

**Syllable-only timestamps**:
```json
{
    "config": {
        "timestamp_granularity": "syllable",
        "include_timestamps": true
    }
}
```

**Both word and syllable timestamps**:
```json
{
    "config": {
        "timestamp_granularity": "both",
        "include_timestamps": true
    }
}
```

#### Asynchronous TTS with Timestamps
```http
POST /api/v1/tts/synthesize/async
Content-Type: application/json
Authorization: Bearer <access_token>

{
    "text": "This is a longer text that requires asynchronous processing with detailed timestamp mapping for each word and syllable.",
    "voice_id": "vs_1234567890",
    "config": {
        "output_format": "mp3",
        "sample_rate": 44100,
        "include_timestamps": true,
        "timestamp_granularity": "both"
    }
}
```

**Response**:
```json
{
    "success": true,
    "data": {
        "synthesis_id": "syn_1234567890",
        "job_id": "job_syn_1234567890",
        "estimated_duration": 45,
        "status": "pending"
    },
    "message": "Asynchronous speech synthesis job created with timestamp mapping"
}
```

When the async job completes, the result (via GET /api/v1/jobs/{job_id}) will include the same timestamp structure as the synchronous endpoint.

---

## Voice Sample Training

### Train Voice Clone Model
```http
POST /api/v1/voice/samples/{sample_id}/train
Content-Type: application/json
Authorization: Bearer <access_token>

{
    "config": {
        "epochs": 100,
        "learning_rate": 0.001,
        "batch_size": 32,
        "enable_timestamp_alignment": true
    }
}
```

**Response**:
```json
{
    "success": true,
    "data": {
        "training_job_id": "job_train_1234567890",
        "estimated_duration": 1800,
        "status": "pending",
        "features": {
            "timestamp_alignment_enabled": true,
            "voice_quality_enhancement": true
        }
    },
    "message": "Voice training job created with timestamp alignment support"
}
```

---

## User Story Examples

### Complete User Workflow

1. **User Registration**
```bash
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "SecurePass123!", "first_name": "John", "last_name": "Doe"}'
```

2. **User Login**
```bash
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "SecurePass123!"}'
```

3. **Upload Voice Sample**
```bash
curl -X POST http://localhost:8080/api/v1/voice/samples \
  -H "Authorization: Bearer <access_token>" \
  -F "file=@voice_sample.wav" \
  -F "name=My Voice Sample" \
  -F "description=High quality recording" \
  -F "language=en-US"
```

4. **Train Voice Clone**
```bash
curl -X POST http://localhost:8080/api/v1/voice/samples/vs_1234567890/train \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"config": {"epochs": 100, "enable_timestamp_alignment": true}}'
```

5. **List Cloned Voices**
```bash
curl -X GET "http://localhost:8080/api/v1/voice/samples?status=ready" \
  -H "Authorization: Bearer <access_token>"
```

6. **Text-to-Speech with Timestamps**
```bash
curl -X POST http://localhost:8080/api/v1/tts/synthesize \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world, this is my cloned voice!",
    "voice_id": "vs_1234567890",
    "config": {
      "output_format": "wav",
      "include_timestamps": true,
      "timestamp_granularity": "both"
    }
  }'
```

---

## Deployment and Configuration

### Docker Compose Example
```yaml
version: '3.8'

services:
  # Flask REST Gateway
  voxify-backend:
    build: ./backend
    ports:
      - "8080:8080"
    environment:
      - JWT_SECRET=your-secret-key
      - DATABASE_URL=sqlite:///data/voxify.db
      - VECTOR_DB_PATH=/data/chroma_db
    volumes:
      - voxify_data:/data
      - voxify_uploads:/uploads
      - voxify_models:/models
  
  # Message Queue (for async processing)
  rabbitmq:
    image: rabbitmq:3.11-management
    environment:
      - RABBITMQ_DEFAULT_USER=voxify
      - RABBITMQ_DEFAULT_PASS=voxify_pass
    ports:
      - "5672:5672"
      - "15672:15672"  # Management UI
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
  
  # Celery Worker (for background tasks)
  celery-worker:
    build: ./backend
    command: celery -A app.celery worker --loglevel=info
    environment:
      - DATABASE_URL=sqlite:///data/voxify.db
      - CELERY_BROKER_URL=pyamqp://voxify:voxify_pass@rabbitmq:5672//
    volumes:
      - voxify_data:/data
      - voxify_uploads:/uploads
      - voxify_models:/models
    depends_on:
      - rabbitmq

volumes:
  voxify_data:        # SQLite database and Chroma vector DB
  voxify_uploads:     # Voice sample uploads
  voxify_models:      # Trained AI models
  rabbitmq_data:      # RabbitMQ data
```

---

## API Best Practices

- All endpoints are RESTful and use HTTP/JSON.
- Unified error and response format.
- JWT authentication for all user and service requests.
- Pagination for all list endpoints.
- Rate limiting and security best practices. 

## AI Acknowledgment
This file was completed with the help of Cursor, which significantly streamlined the process by handling repetitive formatting and ad hoc tasks efficiently. Tools like Cursor reduce the need for manual, repetitive work—something most people understandably want to avoid：）