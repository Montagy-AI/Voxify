# Voxify RESTful API Documentation

## Architecture Overview

Voxify implements a RESTful API architecture providing voice cloning and text-to-speech synthesis capabilities. The system is built around F5-TTS (Five-shot Text-to-Speech) technology, offering zero-shot voice cloning with multilingual support.

- **Flask REST API Gateway**: Provides HTTP/JSON interfaces for all client applications
- **F5-TTS Voice Processing**: Voice sample processing and synthesis using F5-TTS models
- **RESTful Client Support**: All functionality accessible via HTTP/JSON API

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
│   - Authentication & Authorization (JWT)                   │
│   - Request Validation                                      │
│   - Response Formatting                                    │
│   - CORS & Rate Limiting                                   │
│   - Error Handling                                         │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                 Voice Processing Layer                      │
│   - F5-TTS Service Integration                             │
│   - Voice Sample Processing                                │
│   - Voice Cloning & Synthesis                             │
│   - Multilingual Support                                   │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                 Data Storage Layer                          │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   SQLite    │  │ File Storage│  │Vector Database│        │
│  │User Data &  │  │Voice Samples│  │ Chroma/Qdrant │        │
│  │ Metadata    │  │& Synthesis  │  │Voice Embeddings│       │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Backend Framework
```python
Flask==2.3.3
Flask-JWT-Extended==4.5.3
Flask-CORS==4.0.0
SQLAlchemy
```

### Voice Processing
```python
F5-TTS (Five-shot Text-to-Speech)
soundfile==0.12.1
numpy
torch
```

### Data Storage
```python
SQLite (Primary database)
ChromaDB (Voice embeddings)
File system (Audio files)
```

---

## API Endpoints

### Authentication

#### Register User
- **POST** `/api/v1/auth/register`
- **POST** `/api/v1/auth/login`
- **POST** `/api/v1/auth/refresh`

#### User Profile Management
- **GET** `/api/v1/auth/profile`
- **PUT** `/api/v1/auth/profile`
- **PATCH** `/api/v1/auth/profile`

#### Password Reset
- **POST** `/api/v1/auth/forgot-password`
- **POST** `/api/v1/auth/reset-password`

### Voice Sample Management

#### Voice Sample Operations
- **POST** `/api/v1/voice/samples`
  - Upload voice sample for processing
  - Accepts audio files (WAV, MP3)
  - Generates voice embeddings using F5-TTS
  - Returns sample_id and processing status

- **GET** `/api/v1/voice/samples`
  - List all voice samples for the authenticated user
  - Includes pagination support
  - Returns sample metadata and processing status

- **GET** `/api/v1/voice/samples/{sample_id}`
  - Get details of a specific voice sample
  - Includes processing status and metadata

- **DELETE** `/api/v1/voice/samples/{sample_id}`
  - Remove a voice sample
  - Deletes both metadata and associated embeddings

### Voice Clone Management

#### Voice Clone Operations
- **POST** `/api/v1/voice/clones`
  - Generate a new voice clone from processed samples using F5-TTS
  - Uses F5-TTS zero-shot cloning capabilities
  - Accepts array of sample_ids and reference text
  - Returns clone_id and generation status

- **GET** `/api/v1/voice/clones`
  - List all voice clones for the user
  - Includes generation status and metadata

- **GET** `/api/v1/voice/clones/{clone_id}`
  - Get details of a specific voice clone
  - Includes generation status and sample references

- **DELETE** `/api/v1/voice/clones/{clone_id}`
  - Remove a voice clone

- **POST** `/api/v1/voice/clones/{clone_id}/select`
  - Set a voice clone as the active one for synthesis
  - Returns success status

- **POST** `/api/v1/voice/clones/{clone_id}/synthesize`
  - Direct synthesis using a specific voice clone
  - Supports real-time synthesis with custom parameters

#### Voice Model Information
- **GET** `/api/v1/voice/models`
  - Get available F5-TTS voice models and capabilities
  - Returns supported languages and model specifications

- **GET** `/api/v1/voice/info`
  - Get voice service information and status

### Job Management

#### Synthesis Job Operations
- **GET** `/api/v1/job`
  - List synthesis jobs with filtering, sorting, and pagination
  - Query parameters: status, user_id, voice_model_id, text_search, limit, offset, sort_by, sort_order, include_text
  - Supports filtering by status (pending, processing, completed, failed, cancelled)
  - Returns paginated list with metadata

- **POST** `/api/v1/job`
  - Create a new synthesis job
  - Requires text_content and voice_model_id
  - Supports configuration for speed, pitch, volume, output format, sample rate
  - Returns job details with unique job_id

- **GET** `/api/v1/job/{job_id}`
  - Get detailed information about a specific synthesis job
  - Includes job status, progress, configuration, and results
  - Access control: users can only see their own jobs

- **PUT** `/api/v1/job/{job_id}`
  - Update a synthesis job (only allowed for pending jobs)
  - Can update text_content, speed, pitch, volume, output_format, sample_rate, config
  - Returns updated job details

- **PATCH** `/api/v1/job/{job_id}`
  - Partial update of a synthesis job
  - Supports status updates and progress tracking
  - Can update status, progress, error_message, output_file_path, duration

- **DELETE** `/api/v1/job/{job_id}`
  - Delete a synthesis job
  - Only allowed for jobs with status: pending, completed, failed, cancelled
  - Cannot delete jobs that are currently processing

- **GET** `/api/v1/job/{job_id}/progress`
  - Stream real-time progress updates for a synthesis job
  - Returns Server-Sent Events (SSE) stream
  - Provides continuous progress updates until job completion

- **POST** `/api/v1/job/{job_id}/cancel` *(Deprecated)*
  - Cancel a synthesis job (use PATCH instead)
  - Legacy endpoint for backward compatibility

### File Management

#### Audio File Operations
- **GET** `/api/v1/file/synthesis/{job_id}`
  - Download synthesized audio file
  - Requires valid job ownership
  - Returns audio file with appropriate MIME type

- **DELETE** `/api/v1/file/synthesis/{job_id}`
  - Delete synthesized audio file
  - Removes both file and database references

- **GET** `/api/v1/file/voice-clone/{job_id}`
  - Download voice clone synthesis result
  - Specialized endpoint for voice clone outputs

- **GET** `/api/v1/file/voice-clone/{job_id}/info`
  - Get voice clone synthesis file information
  - Returns metadata without downloading the file

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
        "timestamp": "2024-01-15T10:30:00Z"
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Authentication

- JWT Bearer Token authentication for all protected endpoints
- Access tokens expire in 1 hour (configurable)
- Refresh tokens expire in 30 days (configurable)
- All voice and job operations require authentication

---

## Multilingual Support

Voxify implements true multilingual voice cloning support based on F5-TTS capabilities:

### Support Levels:
- **Native (🔵)**: zh-CN, zh-TW, en-US, en-GB using F5TTS_v1_Base model (best quality)
- **Specialized (🟡)**: ja-JP, fr-FR, de-DE, es-ES, it-IT, ru-RU, hi-IN using dedicated models (high quality)
- **Fallback (🟠)**: ko-KR, pt-BR, ar-SA, th-TH, vi-VN using base model (limited quality)

### Implementation:
- Language-to-model mapping in F5-TTS service
- Language parameter passed to synthesis APIs
- Automatic fallback to base model when specialized models unavailable

---

## API Examples

### User Registration and Authentication

```bash
# Register new user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

### Voice Sample Upload and Clone Creation

```bash
# Upload voice sample
curl -X POST http://localhost:8000/api/v1/voice/samples \
  -H "Authorization: Bearer <access_token>" \
  -F "file=@voice_sample.wav" \
  -F "name=My Voice Sample"

# Create voice clone
curl -X POST http://localhost:8000/api/v1/voice/clones \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "sample_ids": ["sample_123"],
    "name": "My Voice Clone",
    "ref_text": "Hello, this is my reference text for voice cloning.",
    "language": "en-US"
  }'
```

### Synthesis Job Creation and Monitoring

```bash
# Create synthesis job
curl -X POST http://localhost:8000/api/v1/job \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "text_content": "Hello world, this is a test synthesis.",
    "voice_model_id": "clone_456",
    "text_language": "en-US",
    "output_format": "wav",
    "sample_rate": 22050,
    "speed": 1.0,
    "pitch": 1.0,
    "volume": 1.0
  }'

# Monitor job progress (SSE stream)
curl -X GET "http://localhost:8000/api/v1/job/job_123/progress" \
  -H "Authorization: Bearer <access_token>" \
  -H "Accept: text/event-stream"

# Download result
curl -X GET "http://localhost:8000/api/v1/file/synthesis/job_123" \
  -H "Authorization: Bearer <access_token>" \
  -o result.wav
```

---

## Workflow Examples

### Basic Text-to-Speech Workflow

1. **User Registration & Login**
2. **Upload Voice Sample** → `POST /api/v1/voice/samples`
3. **Create Voice Clone** → `POST /api/v1/voice/clones`
4. **Create Synthesis Job** → `POST /api/v1/job`
5. **Monitor Progress** → `GET /api/v1/job/{job_id}/progress`
6. **Download Result** → `GET /api/v1/file/synthesis/{job_id}`

### Advanced Voice Cloning Workflow

1. **Upload Multiple Voice Samples**
2. **Process and Validate Samples**
3. **Create Voice Clone with Multiple References**
4. **Test Clone Quality with Sample Synthesis**
5. **Production Synthesis with Optimized Parameters**

---

## Error Handling

### Common Error Codes

- `400 Bad Request`: Invalid request data or parameters
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: Access denied (insufficient permissions)
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource already exists (e.g., email conflict)
- `500 Internal Server Error`: Server-side processing error

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error description",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

---

## Rate Limiting

- Maximum 100 requests per minute per user
- File upload limit: 16MB per file
- Voice sample processing: Maximum 50 samples per day
- Synthesis jobs: Maximum 100 jobs per day


## Development Notes

This API documentation reflects the current implementation as of the latest version. The system is built on F5-TTS technology providing state-of-the-art voice cloning capabilities with minimal training data requirements.

For development and testing, ensure proper environment setup with required dependencies and model files. Refer to the project README for detailed setup instructions.

---

*Documentation last updated: August 2025*
