# Voxify Hybrid API Architecture Documentation

## Architecture Overview

Voxify adopts a hybrid architecture design that combines Flask REST API gateway and gRPC internal services, providing flexibility and high performance:

- **Flask REST API Gateway**: Provides HTTP/REST interfaces for web clients, mobile applications, and admin interfaces
- **gRPC Internal Services**: High-performance voice processing for inter-service communication and high-performance clients
- **Hybrid Client Support**: Clients can choose REST API (ease of use) or direct gRPC (high performance)

### Architecture Layers
```
┌─────────────────────────────────────────────────────────────┐
│                    Client Layer                             │
│  Web Apps │  Mobile Apps │  Admin UI  │  High-Perf Clients │
└─────────────────────────────────────────────────────────────┘
                        │                        │
                        ▼                        ▼
┌─────────────────────────────────────┐  ┌──────────────────┐
│           Flask REST Gateway         │  │   Direct gRPC    │
│        (HTTP/JSON API)              │  │   (High-Perf)    │
│   - Authentication & Authorization  │  │                 │
│   - Request Validation              │  │                 │
│   - Response Formatting             │  │                 │
│   - Admin Interface                 │  │                 │
│   - Middleware Layer:               │  │                 │
│     * JWT Authentication            │  │                 │
│     * CORS & Rate Limiting          │  │                 │
│     * Error Handling                │  │                 │
└─────────────────────────────────────┘  └──────────────────┘
                        │                        │
                        ▼                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    gRPC Service Layer                       │
│                   (Internal Communication)                 │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │Auth Service │  │Voice Service│  │ TTS Service │         │
│  │  Port 50051 │  │  Port 50052 │  │  Port 50053 │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐                          │
│  │ Job Service │  │File Service │                          │
│  │  Port 50054 │  │  Port 50055 │                          │
│  └─────────────┘  └─────────────┘                          │
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

### Flask REST Gateway Layer
```python
# Core Framework
Flask==2.3.3
Flask-RESTful==0.3.10
Flask-JWT-Extended==4.5.3
Flask-CORS==4.0.0
Flask-Limiter==3.5.0

# gRPC Communication
grpcio==1.58.0
grpcio-tools==1.58.0
protobuf==4.24.3
```

### gRPC Service Layer
```python
# Common Dependencies
grpcio==1.58.0
grpcio-tools==1.58.0
protobuf==4.24.3
asyncio==3.4.3

# Authentication Service
SQLAlchemy==2.0.21
psycopg2-binary==2.9.7
bcrypt==4.0.1
PyJWT==2.8.0

# Voice Service
torch==2.0.1
torchaudio==2.0.2
librosa==0.10.1
numpy==1.24.3

# TTS Service
TTS==0.17.8
espeak-ng==1.51.1
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

## Flask REST API Gateway

### Basic Information
- **Framework**: Flask + Flask-RESTful
- **Port**: 8080 (development), 80/443 (production)
- **Authentication**: JWT Bearer Token
- **Data Format**: JSON
- **Documentation**: Swagger/OpenAPI 3.0

### Service Endpoints
```
http://localhost:8080/api/v1          # Development
https://staging.voxify.com/api/v1     # Staging  
https://api.voxify.com/api/v1         # Production
```

---

## Authentication Endpoints

### User Registration
```http
POST /api/v1/auth/register
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Response**:
```json
{
    "success": true,
    "data": {
        "user_id": "usr_1234567890",
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "created_at": "2024-01-15T10:30:00Z"
    },
    "message": "User registration successful"
}
```

### User Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "SecurePass123!"
}
```

**Response**:
```json
{
    "success": true,
    "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh_token": "refresh_token_here",
        "expires_in": 3600,
        "user": {
            "user_id": "usr_1234567890",
            "email": "user@example.com",
            "first_name": "John",
            "last_name": "Doe"
        }
    }
}
```

### Refresh Token
```http
POST /api/v1/auth/refresh
Content-Type: application/json
Authorization: Bearer <refresh_token>

{
    "refresh_token": "refresh_token_here"
}
```

---

## Voice Sample Endpoints

### Upload Voice Sample
```http
POST /api/v1/voice/samples
Content-Type: multipart/form-data
Authorization: Bearer <access_token>

name: "My Voice Sample"
description: "High quality recording"
language: "en-US"
file: voice_sample.wav
```

**Response**:
```json
{
    "success": true,
    "data": {
        "sample_id": "vs_1234567890",
        "name": "My Voice Sample",
        "description": "High quality recording",
        "status": "uploaded",
        "format": "wav",
        "duration": 15.5,
        "language": "en-US",
        "file_size": 1048576,
        "created_at": "2024-01-15T10:30:00Z"
    },
    "message": "Voice sample uploaded successfully"
}
```

### Get Voice Sample List
```http
GET /api/v1/voice/samples?page=1&page_size=20&status=ready&language=en-US
Authorization: Bearer <access_token>
```

**Response**:
```json
{
    "success": true,
    "data": {
        "samples": [
            {
                "sample_id": "vs_1234567890",
                "name": "My Voice Sample",
                "status": "ready",
                "duration": 15.5,
                "language": "en-US",
                "quality_score": 8.5,
                "created_at": "2024-01-15T10:30:00Z"
            }
        ],
        "pagination": {
            "page": 1,
            "page_size": 20,
            "total_count": 5,
            "total_pages": 1,
            "has_next": false,
            "has_prev": false
        }
    }
}
```

### Get Single Voice Sample
```http
GET /api/v1/voice/samples/{sample_id}
Authorization: Bearer <access_token>
```

### Delete Voice Sample
```http
DELETE /api/v1/voice/samples/{sample_id}
Authorization: Bearer <access_token>
```

### Train Voice Model
```http
POST /api/v1/voice/samples/{sample_id}/train
Content-Type: application/json
Authorization: Bearer <access_token>

{
    "config": {
        "epochs": 100,
        "learning_rate": 0.001,
        "batch_size": 32
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
        "status": "pending"
    },
    "message": "Voice training job created"
}
```

---

## Text-to-Speech Endpoints (TTS)

### Synchronous Speech Synthesis
```http
POST /api/v1/tts/synthesize
Content-Type: application/json
Authorization: Bearer <access_token>

{
    "text": "Hello, this is a voice synthesis test.",
    "voice_id": "vs_1234567890",
    "config": {
        "output_format": "wav",
        "sample_rate": 22050,
        "speed": 1.0,
        "pitch": 1.0,
        "volume": 1.0
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
        "duration": 5.2,
        "format": "wav",
        "sample_rate": 22050
    },
    "message": "Speech synthesis completed"
}
```

### Asynchronous Speech Synthesis
```http
POST /api/v1/tts/synthesize/async
Content-Type: application/json
Authorization: Bearer <access_token>

{
    "text": "This is a long text that requires asynchronous processing...",
    "voice_id": "vs_1234567890",
    "config": {
        "output_format": "mp3",
        "sample_rate": 44100
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
        "estimated_duration": 30,
        "status": "pending"
    },
    "message": "Asynchronous speech synthesis job created"
}
```

### Streaming Speech Synthesis (Server-Sent Events)
```http
GET /api/v1/tts/synthesize/stream
Authorization: Bearer <access_token>
```

**Query Parameters**:
- `text`: Text to synthesize
- `voice_id`: Voice model ID
- `format`: Output format (wav, mp3)

**Response** (Server-Sent Events):
```
data: {"type": "job_info", "synthesis_id": "syn_1234567890", "estimated_duration": 10}

data: {"type": "progress", "progress": 0.1, "message": "Starting processing..."}

data: {"type": "progress", "progress": 0.5, "message": "Synthesizing..."}

data: {"type": "audio_chunk", "chunk_id": 1, "audio_url": "https://api.voxify.com/temp/chunk_1.wav"}

data: {"type": "completed", "audio_url": "https://api.voxify.com/files/audio/syn_1234567890.wav", "duration": 8.5}
```

---

## Job Management Endpoints

### Get Job List
```http
GET /api/v1/jobs?page=1&page_size=20&status=running&type=voice_training
Authorization: Bearer <access_token>
```

**Response**:
```json
{
    "success": true,
    "data": {
        "jobs": [
            {
                "job_id": "job_train_1234567890",
                "type": "voice_training",
                "status": "running",
                "progress": 0.65,
                "title": "Voice Model Training - My Voice Sample",
                "created_at": "2024-01-15T10:30:00Z",
                "estimated_completion": "2024-01-15T11:00:00Z"
            }
        ],
        "pagination": {
            "page": 1,
            "page_size": 20,
            "total_count": 3,
            "total_pages": 1
        }
    }
}
```

### Get Job Details
```http
GET /api/v1/jobs/{job_id}
Authorization: Bearer <access_token>
```

### Cancel Job
```http
POST /api/v1/jobs/{job_id}/cancel
Authorization: Bearer <access_token>
```

### Real-time Job Progress (WebSocket)
```http
GET /api/v1/jobs/{job_id}/progress/ws
Upgrade: websocket
Authorization: Bearer <access_token>
```

**WebSocket Message**:
```json
{
    "job_id": "job_train_1234567890",
    "status": "running",
    "progress": 0.75,
    "message": "Training epoch 75...",
    "timestamp": "2024-01-15T10:45:00Z"
}
```

---

## File Management Endpoints

### Download Audio File
```http
GET /api/v1/files/audio/{file_id}
Authorization: Bearer <access_token>
```

### Get File Information
```http
GET /api/v1/files/{file_id}/info
Authorization: Bearer <access_token>
```

**Response**:
```json
{
    "success": true,
    "data": {
        "file_id": "file_1234567890",
        "filename": "synthesis_output.wav",
        "content_type": "audio/wav",
        "size": 1048576,
        "duration": 15.5,
        "created_at": "2024-01-15T10:30:00Z",
        "expires_at": "2024-01-16T10:30:00Z"
    }
}
```

---

## Admin Interface Endpoints

### System Statistics
```http
GET /api/v1/admin/stats
Authorization: Bearer <admin_token>
```

**Response**:
```json
{
    "success": true,
    "data": {
        "users": {
            "total": 1250,
            "active_today": 89,
            "new_this_week": 23
        },
        "voice_samples": {
            "total": 3450,
            "training": 12,
            "ready": 3420
        },
        "syntheses": {
            "today": 156,
            "this_week": 1247,
            "total": 15678
        },
        "system": {
            "cpu_usage": 45.2,
            "memory_usage": 67.8,
            "disk_usage": 23.1
        }
    }
}
```

### User Management
```http
GET /api/v1/admin/users?page=1&page_size=50
Authorization: Bearer <admin_token>
```

### System Configuration
```http
GET /api/v1/admin/config
Authorization: Bearer <admin_token>

PUT /api/v1/admin/config
Authorization: Bearer <admin_token>
Content-Type: application/json

{
    "max_voice_samples_per_user": 10,
    "max_synthesis_length": 1000,
    "default_sample_rate": 22050
}
```

---

## gRPC Internal Service Layer

### Service Definitions
```protobuf
// Keep the original gRPC service definitions
service AuthService {
    rpc Register(RegisterRequest) returns (RegisterResponse);
    rpc Login(LoginRequest) returns (LoginResponse);
    rpc RefreshToken(RefreshTokenRequest) returns (RefreshTokenResponse);
    rpc ValidateToken(ValidateTokenRequest) returns (ValidateTokenResponse);
}

service VoiceService {
    rpc UploadVoiceSample(stream UploadVoiceSampleRequest) returns (UploadVoiceSampleResponse);
    rpc GetVoiceSamples(GetVoiceSamplesRequest) returns (GetVoiceSamplesResponse);
    rpc TrainVoice(TrainVoiceRequest) returns (TrainVoiceResponse);
    rpc DeleteVoiceSample(DeleteVoiceSampleRequest) returns (DeleteVoiceSampleResponse);
}

service TTSService {
    rpc SynthesizeText(SynthesizeTextRequest) returns (SynthesizeTextResponse);
    rpc SynthesizeTextStream(SynthesizeTextRequest) returns (stream SynthesizeTextStreamResponse);
    rpc SynthesizeTextAsync(SynthesizeTextAsyncRequest) returns (SynthesizeTextAsyncResponse);
}

service JobService {
    rpc GetJob(GetJobRequest) returns (GetJobResponse);
    rpc ListJobs(ListJobsRequest) returns (ListJobsResponse);
    rpc CancelJob(CancelJobRequest) returns (CancelJobResponse);
    rpc GetJobProgress(GetJobProgressRequest) returns (stream JobProgressResponse);
}

service FileService {
    rpc UploadFile(stream UploadFileRequest) returns (UploadFileResponse);
    rpc DownloadFile(DownloadFileRequest) returns (stream DownloadFileResponse);
    rpc GetFileInfo(GetFileInfoRequest) returns (GetFileInfoResponse);
    rpc DeleteFile(DeleteFileRequest) returns (DeleteFileResponse);
}
```

---

## Flask Gateway Implementation Example

### Project Structure
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
│   ├── grpc_clients/
│   │   ├── __init__.py
│   │   ├── auth_client.py   # Auth service client
│   │   ├── voice_client.py  # Voice service client
│   │   ├── tts_client.py    # TTS service client
│   │   └── job_client.py    # Job service client
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
├── grpc_services/
│   ├── auth/
│   ├── voice/
│   ├── tts/
│   ├── job/
│   └── file/
├── proto/
│   ├── auth.proto
│   ├── voice.proto
│   ├── tts.proto
│   ├── job.proto
│   └── file.proto
├── tests/
├── requirements.txt
└── app.py
```

### Flask Application Example Code

```python
# app.py
from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from app.api import auth, voice, tts, jobs, files, admin
from app.middleware.error_handler import register_error_handlers

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Enable CORS
    CORS(app)
    
    # Create API instance
    api = Api(app)
    
    # Register authentication endpoints
    api.add_resource(auth.RegisterResource, '/api/v1/auth/register')
    api.add_resource(auth.LoginResource, '/api/v1/auth/login')
    api.add_resource(auth.RefreshTokenResource, '/api/v1/auth/refresh')
    
    # Register voice endpoints
    api.add_resource(voice.VoiceSamplesResource, '/api/v1/voice/samples')
    api.add_resource(voice.VoiceSampleResource, '/api/v1/voice/samples/<sample_id>')
    api.add_resource(voice.TrainVoiceResource, '/api/v1/voice/samples/<sample_id>/train')
    
    # Register TTS endpoints
    api.add_resource(tts.SynthesizeResource, '/api/v1/tts/synthesize')
    api.add_resource(tts.SynthesizeAsyncResource, '/api/v1/tts/synthesize/async')
    
    # Register job endpoints
    api.add_resource(jobs.JobsResource, '/api/v1/jobs')
    api.add_resource(jobs.JobResource, '/api/v1/jobs/<job_id>')
    
    # Register file endpoints
    api.add_resource(files.FileResource, '/api/v1/files/<file_id>')
    
    # Register admin endpoints
    api.add_resource(admin.StatsResource, '/api/v1/admin/stats')
    
    # Register error handlers
    register_error_handlers(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8080, debug=True)
```

```python
# app/api/voice.py
from flask import request
from flask_restful import Resource
from app.grpc_clients.voice_client import VoiceServiceClient
from app.middleware.auth import jwt_required
from app.utils.validators import validate_voice_upload
from app.utils.formatters import format_response

class VoiceSamplesResource(Resource):
    @jwt_required
    def get(self):
        """Get voice sample list"""
        user_id = request.current_user['user_id']
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        status = request.args.get('status')
        language = request.args.get('language')
        
        # Call gRPC service
        client = VoiceServiceClient()
        response = client.get_voice_samples(
            user_id=user_id,
            page=page,
            page_size=page_size,
            status=status,
            language=language
        )
        
        return format_response(
            success=True,
            data={
                'samples': response.samples,
                'pagination': response.pagination
            }
        )
    
    @jwt_required
    def post(self):
        """Upload voice sample"""
        user_id = request.current_user['user_id']
        
        # Validate request
        validation_result = validate_voice_upload(request)
        if not validation_result.is_valid:
            return format_response(
                success=False,
                error=validation_result.errors
            ), 400
        
        # Call gRPC service
        client = VoiceServiceClient()
        response = client.upload_voice_sample(
            user_id=user_id,
            file_data=request.files['file'],
            metadata={
                'name': request.form.get('name'),
                'description': request.form.get('description'),
                'language': request.form.get('language', 'en-US')
            }
        )
        
        if response.success:
            return format_response(
                success=True,
                data=response.sample_info,
                message="Voice sample uploaded successfully"
            )
        else:
            return format_response(
                success=False,
                error=response.error
            ), 400
```

---

## Client SDK Usage Examples

### Python REST Client
```python
import requests

class VoxifyRESTClient:
    def __init__(self, base_url='http://localhost:8080'):
        self.base_url = base_url
        self.access_token = None
    
    def login(self, email, password):
        """Login to get token"""
        response = requests.post(f'{self.base_url}/api/v1/auth/login', json={
            'email': email,
            'password': password
        })
        if response.status_code == 200:
            data = response.json()['data']
            self.access_token = data['access_token']
            return data
        return None
    
    def upload_voice_sample(self, file_path, name, description=""):
        """Upload voice sample"""
        headers = {'Authorization': f'Bearer {self.access_token}'}
        files = {'file': open(file_path, 'rb')}
        data = {'name': name, 'description': description}
        
        response = requests.post(
            f'{self.base_url}/api/v1/voice/samples',
            headers=headers,
            files=files,
            data=data
        )
        return response.json()
    
    def synthesize_text(self, text, voice_id):
        """Text to speech"""
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.post(
            f'{self.base_url}/api/v1/tts/synthesize',
            headers=headers,
            json={
                'text': text,
                'voice_id': voice_id,
                'config': {
                    'output_format': 'wav',
                    'sample_rate': 22050
                }
            }
        )
        return response.json()

# Usage example
client = VoxifyRESTClient()
client.login('user@example.com', 'password')
result = client.synthesize_text('Hello world', 'vs_1234567890')
print(f"Audio URL: {result['data']['audio_url']}")
```

### JavaScript REST Client
```javascript
class VoxifyRESTClient {
    constructor(baseUrl = 'http://localhost:8080') {
        this.baseUrl = baseUrl;
        this.accessToken = null;
    }
    
    async login(email, password) {
        const response = await fetch(`${this.baseUrl}/api/v1/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });
        
        if (response.ok) {
            const data = await response.json();
            this.accessToken = data.data.access_token;
            return data.data;
        }
        return null;
    }
    
    async synthesizeText(text, voiceId) {
        const response = await fetch(`${this.baseUrl}/api/v1/tts/synthesize`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.accessToken}`
            },
            body: JSON.stringify({
                text,
                voice_id: voiceId,
                config: {
                    output_format: 'wav',
                    sample_rate: 22050
                }
            })
        });
        
        return await response.json();
    }
}

// Usage example
const client = new VoxifyRESTClient();
await client.login('user@example.com', 'password');
const result = await client.synthesizeText('Hello world', 'vs_1234567890');
console.log(`Audio URL: ${result.data.audio_url}`);
```

---

## Deployment and Configuration

### Docker Compose Example
```yaml
version: '3.8'

services:
  # Flask REST Gateway
  rest-gateway:
    build: ./backend/rest_gateway
    ports:
      - "8080:8080"
    environment:
      - GRPC_AUTH_SERVICE=auth-service:50051
      - GRPC_VOICE_SERVICE=voice-service:50052
      - GRPC_TTS_SERVICE=tts-service:50053
      - JWT_SECRET=your-secret-key
    depends_on:
      - auth-service
      - voice-service
      - tts-service
  
  # gRPC Authentication Service
  auth-service:
    build: ./backend/grpc_services/auth
    ports:
      - "50051:50051"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/voxify
  
  # gRPC Voice Service  
  voice-service:
    build: ./backend/grpc_services/voice
    ports:
      - "50052:50052"
    volumes:
      - voice_models:/app/models
      - voice_uploads:/app/uploads
  
  # gRPC TTS Service
  tts-service:
    build: ./backend/grpc_services/tts
    ports:
      - "50053:50053"
    volumes:
      - tts_models:/app/models
      - audio_output:/app/output
  
  # Database
  postgres:
    image: postgres:13
    environment:
      - POSTGRES_DB=voxify
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
  voice_models:
  voice_uploads:
  tts_models:
  audio_output:
```

---

## API Best Practices

### 1. Error Handling
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

### 2. Pagination
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

### 3. Authentication
- REST API uses JWT Bearer Token
- gRPC internal services use inter-service authentication
- Admin endpoints require additional permission verification

### 4. Rate Limiting
- Maximum 100 requests per minute per user
- File upload limit: 50MB/file, maximum 100 files per day
- Speech synthesis limit: maximum 1000 syntheses per day

This hybrid architecture design provides flexibility and high performance, allowing clients to choose REST API (ease of use) or direct gRPC (high performance) based on their needs, while internal services communicate efficiently through gRPC. 