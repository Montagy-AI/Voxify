# Voxify Hybrid Architecture Implementation Guide

## System Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        WebApp[Web Application<br/>React/Vue]
        MobileApp[Mobile Application<br/>React Native]
        AdminUI[Admin Interface<br/>Flask Admin]
        HPClient[High-Performance Client<br/>Python/Go gRPC]
    end

    subgraph "API Gateway Layer"
        subgraph "Flask REST Gateway (Port 8080)"
            AuthAPI[Authentication API<br/>/api/v1/auth/*]
            VoiceAPI[Voice API<br/>/api/v1/voice/*]
            TTSAPI[TTS API<br/>/api/v1/tts/*]
            JobAPI[Job API<br/>/api/v1/jobs/*]
            FileAPI[File API<br/>/api/v1/files/*]
            AdminAPI[Admin API<br/>/api/v1/admin/*]
        end
        
        subgraph "Middleware Layer"
            JWTAuth[JWT Authentication Middleware]
            CORS[CORS Middleware]
            RateLimit[Rate Limiting Middleware]
            ErrorHandler[Error Handling Middleware]
        end
    end

    subgraph "gRPC Service Layer"
        AuthService[Authentication Service<br/>Port 50051]
        VoiceService[Voice Service<br/>Port 50052]
        TTSService[TTS Service<br/>Port 50053]
        JobService[Job Service<br/>Port 50054]
        FileService[File Service<br/>Port 50055]
    end

    subgraph "Data Storage Layer"
        SQLite[(SQLite<br/>User Data/Metadata)]
        Redis[(Redis<br/>Cache/Sessions)]
        FileStorage[File Storage<br/>MinIO/S3]
        ModelStorage[Model Storage<br/>Local/Network Storage]
        VectorDB[(Vector Database<br/>Chroma/Qdrant)]
    end

    subgraph "Message Queue"
        Celery[Celery<br/>Async Tasks]
        RabbitMQ[RabbitMQ<br/>Message Broker]
    end

    %% Client to API Gateway
    WebApp --> AuthAPI
    WebApp --> VoiceAPI
    WebApp --> TTSAPI
    WebApp --> JobAPI
    
    MobileApp --> AuthAPI
    MobileApp --> VoiceAPI
    MobileApp --> TTSAPI
    
    AdminUI --> AdminAPI
    
    %% High-performance client direct gRPC connection
    HPClient -.-> AuthService
    HPClient -.-> VoiceService
    HPClient -.-> TTSService
    
    %% API Gateway to gRPC Services
    AuthAPI --> AuthService
    VoiceAPI --> VoiceService
    TTSAPI --> TTSService
    JobAPI --> JobService
    FileAPI --> FileService
    AdminAPI --> AuthService
    AdminAPI --> VoiceService
    AdminAPI --> TTSService
    AdminAPI --> JobService
    
    %% gRPC Services to Data Layer
    AuthService --> SQLite
    AuthService --> Redis
    
    VoiceService --> SQLite
    VoiceService --> FileStorage
    VoiceService --> ModelStorage
    VoiceService --> Celery
    
    TTSService --> SQLite
    TTSService --> FileStorage
    TTSService --> ModelStorage
    TTSService --> Celery
    
    JobService --> SQLite
    JobService --> Redis
    
    FileService --> FileStorage
    
    %% Async Task Processing
    Celery --> RabbitMQ
    Celery --> VoiceService
    Celery --> TTSService
```

## Technology Stack Details

### Flask REST Gateway Layer
```python
# Technology Stack
Flask==2.3.3
Flask-RESTful==0.3.10
Flask-JWT-Extended==4.5.3
Flask-CORS==4.0.0
Flask-Limiter==3.5.0
grpcio==1.58.0
grpcio-tools==1.58.0
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

## Detailed Implementation Architecture

### 1. Flask REST Gateway Implementation

#### Project Structure
```
rest_gateway/
├── app/
│   ├── __init__.py              # Flask application factory
│   ├── config.py                # Configuration management
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── voice.py             # Voice sample endpoints
│   │   ├── tts.py               # TTS endpoints
│   │   ├── jobs.py              # Job management endpoints
│   │   ├── files.py             # File management endpoints
│   │   └── admin.py             # Admin endpoints
│   ├── grpc_clients/
│   │   ├── __init__.py
│   │   ├── base_client.py       # gRPC client base class
│   │   ├── auth_client.py       # Authentication service client
│   │   ├── voice_client.py      # Voice service client
│   │   ├── tts_client.py        # TTS service client
│   │   ├── job_client.py        # Job service client
│   │   └── file_client.py       # File service client
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth.py              # JWT authentication decorator
│   │   ├── cors.py              # CORS configuration
│   │   ├── rate_limit.py        # Rate limiting configuration
│   │   └── error_handler.py     # Unified error handling
│   ├── models/
│   │   ├── __init__.py
│   │   ├── request_models.py    # Request validation models
│   │   ├── response_models.py   # Response format models
│   │   └── error_models.py      # Error models
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── validators.py        # Request validators
│   │   ├── formatters.py        # Response formatters
│   │   ├── file_handler.py      # File handling utilities
│   │   └── websocket.py         # WebSocket support
│   └── schemas/
│       ├── __init__.py
│       └── swagger.py           # Swagger API documentation
├── proto/                       # Protocol Buffer definitions
│   ├── auth.proto
│   ├── voice.proto
│   ├── tts.proto
│   ├── job.proto
│   └── file.proto
├── generated/                   # Generated gRPC code
│   ├── auth_pb2.py
│   ├── auth_pb2_grpc.py
│   ├── voice_pb2.py
│   ├── voice_pb2_grpc.py
│   └── ...
├── tests/
│   ├── test_api/
│   ├── test_grpc_clients/
│   └── test_utils/
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── requirements.txt
├── gunicorn.conf.py
└── wsgi.py
```

#### Core Implementation Code

**Flask Application Factory**:
```python
# app/__init__.py
from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(f'app.config.{config_name.title()}Config')
    
    # Initialize extensions
    CORS(app)
    jwt = JWTManager(app)
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=["100 per minute"]
    )
    
    # Create API instance
    api = Api(app)
    
    # Register blueprints and resources
    from app.api import auth, voice, tts, jobs, files, admin
    register_resources(api)
    
    # Register error handlers
    from app.middleware.error_handler import register_error_handlers
    register_error_handlers(app)
    
    return app

def register_resources(api):
    """Register all API resources"""
    # Authentication endpoints
    api.add_resource(auth.RegisterResource, '/api/v1/auth/register')
    api.add_resource(auth.LoginResource, '/api/v1/auth/login')
    api.add_resource(auth.RefreshTokenResource, '/api/v1/auth/refresh')
    api.add_resource(auth.LogoutResource, '/api/v1/auth/logout')
    
    # Voice endpoints
    api.add_resource(voice.VoiceSamplesResource, '/api/v1/voice/samples')
    api.add_resource(voice.VoiceSampleResource, '/api/v1/voice/samples/<sample_id>')
    api.add_resource(voice.TrainVoiceResource, '/api/v1/voice/samples/<sample_id>/train')
    
    # TTS endpoints
    api.add_resource(tts.SynthesizeResource, '/api/v1/tts/synthesize')
    api.add_resource(tts.SynthesizeAsyncResource, '/api/v1/tts/synthesize/async')
    api.add_resource(tts.SynthesizeStreamResource, '/api/v1/tts/synthesize/stream')
    
    # Job endpoints
    api.add_resource(jobs.JobsResource, '/api/v1/jobs')
    api.add_resource(jobs.JobResource, '/api/v1/jobs/<job_id>')
    api.add_resource(jobs.CancelJobResource, '/api/v1/jobs/<job_id>/cancel')
    
    # File endpoints
    api.add_resource(files.FileResource, '/api/v1/files/<file_id>')
    api.add_resource(files.FileInfoResource, '/api/v1/files/<file_id>/info')
    
    # Admin endpoints
    api.add_resource(admin.StatsResource, '/api/v1/admin/stats')
    api.add_resource(admin.UsersResource, '/api/v1/admin/users')
    api.add_resource(admin.ConfigResource, '/api/v1/admin/config')
```

**gRPC Client Base Class**:
```python
# app/grpc_clients/base_client.py
import grpc
import logging
from abc import ABC, abstractmethod
from typing import Optional
from app.config import Config

class BaseGRPCClient(ABC):
    """gRPC client base class"""
    
    def __init__(self, service_host: str, service_port: int):
        self.service_host = service_host
        self.service_port = service_port
        self._channel: Optional[grpc.Channel] = None
        self._stub = None
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @property
    def channel(self) -> grpc.Channel:
        """Get or create gRPC channel"""
        if self._channel is None:
            self._channel = grpc.insecure_channel(
                f'{self.service_host}:{self.service_port}',
                options=[
                    ('grpc.keepalive_time_ms', 30000),
                    ('grpc.keepalive_timeout_ms', 5000),
                    ('grpc.keepalive_permit_without_calls', True),
                    ('grpc.http2.max_pings_without_data', 0),
                    ('grpc.http2.min_ping_interval_without_data_ms', 300000),
                ]
            )
        return self._channel
    
    @abstractmethod
    def create_stub(self):
        """Create service stub, must be implemented by subclasses"""
        pass
    
    def close(self):
        """Close connection"""
        if self._channel:
            self._channel.close()
            self._channel = None
    
    def call_with_auth(self, method, request, user_token: Optional[str] = None):
        """Authenticated gRPC call"""
        metadata = []
        if user_token:
            metadata.append(('authorization', f'Bearer {user_token}'))
        
        try:
            return method(request, metadata=metadata)
        except grpc.RpcError as e:
            self.logger.error(f"gRPC call failed: {e.code()} - {e.details()}")
            raise self._convert_grpc_error(e)
    
    def _convert_grpc_error(self, grpc_error: grpc.RpcError):
        """Convert gRPC error to HTTP error"""
        from app.models.error_models import APIError
        
        error_map = {
            grpc.StatusCode.INVALID_ARGUMENT: (400, "INVALID_ARGUMENT"),
            grpc.StatusCode.UNAUTHENTICATED: (401, "UNAUTHENTICATED"),
            grpc.StatusCode.PERMISSION_DENIED: (403, "PERMISSION_DENIED"),
            grpc.StatusCode.NOT_FOUND: (404, "NOT_FOUND"),
            grpc.StatusCode.INTERNAL: (500, "INTERNAL_ERROR"),
        }
        
        status_code, error_code = error_map.get(
            grpc_error.code(), 
            (500, "UNKNOWN_ERROR")
        )
        
        return APIError(
            status_code=status_code,
            error_code=error_code,
            message=grpc_error.details()
        )
```

**Voice Service Client**:
```python
# app/grpc_clients/voice_client.py
from app.grpc_clients.base_client import BaseGRPCClient
from generated import voice_pb2_grpc, voice_pb2
from typing import BinaryIO, Dict, Any
import os

class VoiceServiceClient(BaseGRPCClient):
    """Voice service client"""
    
    def __init__(self):
        super().__init__(
            service_host=os.getenv('GRPC_VOICE_SERVICE_HOST', 'localhost'),
            service_port=int(os.getenv('GRPC_VOICE_SERVICE_PORT', '50052'))
        )
    
    def create_stub(self):
        """Create voice service stub"""
        if self._stub is None:
            self._stub = voice_pb2_grpc.VoiceServiceStub(self.channel)
        return self._stub
    
    def upload_voice_sample(self, 
                          user_id: str, 
                          file_data: BinaryIO, 
                          metadata: Dict[str, Any],
                          user_token: str) -> voice_pb2.UploadVoiceSampleResponse:
        """Upload voice sample"""
        stub = self.create_stub()
        
        def request_generator():
            # Send metadata
            sample_metadata = voice_pb2.VoiceSampleMetadata(
                name=metadata['name'],
                description=metadata.get('description', ''),
                format=voice_pb2.AudioFormat.WAV,
                sample_rate=metadata.get('sample_rate', 22050),
                file_size=metadata.get('file_size', 0),
                language=metadata.get('language', 'en-US')
            )
            yield voice_pb2.UploadVoiceSampleRequest(
                user_id=user_id,
                metadata=sample_metadata
            )
            
            # Send audio data
            while True:
                chunk = file_data.read(4096)
                if not chunk:
                    break
                yield voice_pb2.UploadVoiceSampleRequest(chunk=chunk)
        
        return self.call_with_auth(
            stub.UploadVoiceSample, 
            request_generator(), 
            user_token
        )
    
    def get_voice_samples(self, 
                         user_id: str, 
                         page: int = 1, 
                         page_size: int = 20,
                         status: str = None,
                         language: str = None,
                         user_token: str = None) -> voice_pb2.GetVoiceSamplesResponse:
        """Get voice sample list"""
        stub = self.create_stub()
        
        request = voice_pb2.GetVoiceSamplesRequest(
            user_id=user_id,
            pagination=voice_pb2.PaginationRequest(
                page=page,
                page_size=page_size
            ),
            status=status or "",
            language=language or ""
        )
        
        return self.call_with_auth(stub.GetVoiceSamples, request, user_token)
    
    def train_voice(self, 
                   sample_id: str, 
                   config: Dict[str, Any],
                   user_token: str) -> voice_pb2.TrainVoiceResponse:
        """Train voice model"""
        stub = self.create_stub()
        
        training_config = voice_pb2.TrainingConfig(
            epochs=config.get('epochs', 100),
            learning_rate=config.get('learning_rate', 0.001),
            batch_size=config.get('batch_size', 32)
        )
        
        request = voice_pb2.TrainVoiceRequest(
            sample_id=sample_id,
            config=training_config
        )
        
        return self.call_with_auth(stub.TrainVoice, request, user_token)
```

**JWT Authentication Middleware**:
```python
# app/middleware/auth.py
from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
import jwt
from app.grpc_clients.auth_client import AuthServiceClient

def jwt_required(f):
    """JWT authentication decorator"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # Verify JWT token
            verify_jwt_in_request()
            
            # Get user identity
            user_id = get_jwt_identity()
            claims = get_jwt()
            
            # Verify token validity (call authentication service)
            auth_client = AuthServiceClient()
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            validation_response = auth_client.validate_token(token)
            if not validation_response.valid:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'TOKEN_INVALID',
                        'message': 'Invalid token'
                    }
                }), 401
            
            # Add user information to request context
            request.current_user = {
                'user_id': user_id,
                'email': claims.get('email'),
                'roles': claims.get('roles', [])
            }
            
            return f(*args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'TOKEN_EXPIRED',
                    'message': 'Token has expired'
                }
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'TOKEN_INVALID',
                    'message': 'Invalid token'
                }
            }), 401
        except Exception as e:
            current_app.logger.error(f"Authentication error: {str(e)}")
            return jsonify({
                'success': False,
                'error': {
                    'code': 'AUTH_ERROR',
                    'message': 'Authentication failed'
                }
            }), 401
    
    return decorated

def admin_required(f):
    """Admin permission decorator"""
    @wraps(f)
    @jwt_required
    def decorated(*args, **kwargs):
        user_roles = request.current_user.get('roles', [])
        if 'admin' not in user_roles:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'PERMISSION_DENIED',
                    'message': 'Admin permission required'
                }
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated
```

### 2. gRPC Service Implementation

#### Authentication Service
```python
# grpc_services/auth/auth_service.py
import grpc
from concurrent import futures
import jwt
import bcrypt
from datetime import datetime, timedelta
from generated import auth_pb2_grpc, auth_pb2
from database.models import User
from database.connection import get_db_session

class AuthService(auth_pb2_grpc.AuthServiceServicer):
    """Authentication service implementation"""
    
    def __init__(self, jwt_secret: str):
        self.jwt_secret = jwt_secret
    
    def Register(self, request, context):
        """User registration"""
        try:
            session = get_db_session()
            
            # Check if user already exists
            existing_user = session.query(User).filter_by(email=request.email).first()
            if existing_user:
                return auth_pb2.RegisterResponse(
                    success=False,
                    error=auth_pb2.ErrorInfo(
                        code=auth_pb2.ErrorCode.USER_ALREADY_EXISTS,
                        message="User already exists"
                    )
                )
            
            # Encrypt password
            hashed_password = bcrypt.hashpw(
                request.password.encode('utf-8'), 
                bcrypt.gensalt()
            )
            
            # Create user
            user = User(
                email=request.email,
                password_hash=hashed_password.decode('utf-8'),
                first_name=request.first_name,
                last_name=request.last_name
            )
            
            session.add(user)
            session.commit()
            
            return auth_pb2.RegisterResponse(
                success=True,
                user_id=str(user.id),
                message="Registration successful"
            )
            
        except Exception as e:
            session.rollback()
            return auth_pb2.RegisterResponse(
                success=False,
                error=auth_pb2.ErrorInfo(
                    code=auth_pb2.ErrorCode.INTERNAL_ERROR,
                    message=f"Registration failed: {str(e)}"
                )
            )
        finally:
            session.close()
    
    def Login(self, request, context):
        """User login"""
        try:
            session = get_db_session()
            
            # Find user
            user = session.query(User).filter_by(email=request.email).first()
            if not user:
                return auth_pb2.LoginResponse(
                    success=False,
                    error=auth_pb2.ErrorInfo(
                        code=auth_pb2.ErrorCode.INVALID_CREDENTIALS,
                        message="Invalid email or password"
                    )
                )
            
            # Verify password
            if not bcrypt.checkpw(
                request.password.encode('utf-8'), 
                user.password_hash.encode('utf-8')
            ):
                return auth_pb2.LoginResponse(
                    success=False,
                    error=auth_pb2.ErrorInfo(
                        code=auth_pb2.ErrorCode.INVALID_CREDENTIALS,
                        message="Invalid email or password"
                    )
                )
            
            # Generate JWT token
            access_token = self._generate_access_token(user)
            refresh_token = self._generate_refresh_token(user)
            
            return auth_pb2.LoginResponse(
                success=True,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=3600,
                user=auth_pb2.UserInfo(
                    user_id=str(user.id),
                    email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name
                )
            )
            
        except Exception as e:
            return auth_pb2.LoginResponse(
                success=False,
                error=auth_pb2.ErrorInfo(
                    code=auth_pb2.ErrorCode.INTERNAL_ERROR,
                    message=f"Login failed: {str(e)}"
                )
            )
        finally:
            session.close()
    
    def ValidateToken(self, request, context):
        """Validate token"""
        try:
            payload = jwt.decode(
                request.token, 
                self.jwt_secret, 
                algorithms=['HS256']
            )
            
            # Check if token is expired
            if payload['exp'] < datetime.utcnow().timestamp():
                return auth_pb2.ValidateTokenResponse(
                    valid=False,
                    error=auth_pb2.ErrorInfo(
                        code=auth_pb2.ErrorCode.TOKEN_EXPIRED,
                        message="Token has expired"
                    )
                )
            
            return auth_pb2.ValidateTokenResponse(
                valid=True,
                user_id=payload['user_id'],
                email=payload['email']
            )
            
        except jwt.InvalidTokenError:
            return auth_pb2.ValidateTokenResponse(
                valid=False,
                error=auth_pb2.ErrorInfo(
                    code=auth_pb2.ErrorCode.TOKEN_INVALID,
                    message="Invalid token"
                )
            )
    
    def _generate_access_token(self, user) -> str:
        """Generate access token"""
        payload = {
            'user_id': str(user.id),
            'email': user.email,
            'roles': user.roles,
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def _generate_refresh_token(self, user) -> str:
        """Generate refresh token"""
        payload = {
            'user_id': str(user.id),
            'type': 'refresh',
            'exp': datetime.utcnow() + timedelta(days=30),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    auth_pb2_grpc.add_AuthServiceServicer_to_server(
        AuthService(jwt_secret=os.getenv('JWT_SECRET')), 
        server
    )
    
    listen_addr = '[::]:50051'
    server.add_insecure_port(listen_addr)
    server.start()
    print(f"Authentication service started on {listen_addr}")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
```

### 3. Deployment Configuration

#### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  # Flask REST Gateway
  rest-gateway:
    build: 
      context: ./rest_gateway
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      - FLASK_ENV=production
      - GRPC_AUTH_SERVICE_HOST=auth-service
      - GRPC_AUTH_SERVICE_PORT=50051
      - GRPC_VOICE_SERVICE_HOST=voice-service
      - GRPC_VOICE_SERVICE_PORT=50052
      - GRPC_TTS_SERVICE_HOST=tts-service
      - GRPC_TTS_SERVICE_PORT=50053
      - JWT_SECRET=${JWT_SECRET}
      - DATABASE_URL=postgresql://voxify:password@postgres:5432/voxify
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - auth-service
      - voice-service
      - tts-service
      - postgres
      - redis
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # gRPC Authentication Service
  auth-service:
    build:
      context: ./grpc_services/auth
      dockerfile: Dockerfile
    ports:
      - "50051:50051"
    environment:
      - DATABASE_URL=postgresql://voxify:password@postgres:5432/voxify
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - postgres
      - redis
    volumes:
      - ./logs:/app/logs

  # gRPC Voice Service
  voice-service:
    build:
      context: ./grpc_services/voice
      dockerfile: Dockerfile
    ports:
      - "50052:50052"
    environment:
      - DATABASE_URL=postgresql://voxify:password@postgres:5432/voxify
      - MINIO_ENDPOINT=minio:9000
      - MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY}
      - MINIO_SECRET_KEY=${MINIO_SECRET_KEY}
      - CELERY_BROKER=redis://redis:6379/1
    depends_on:
      - postgres
      - redis
      - minio
    volumes:
      - voice_models:/app/models
      - ./logs:/app/logs
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G

  # gRPC TTS Service
  tts-service:
    build:
      context: ./grpc_services/tts
      dockerfile: Dockerfile
    ports:
      - "50053:50053"
    environment:
      - DATABASE_URL=postgresql://voxify:password@postgres:5432/voxify
      - MINIO_ENDPOINT=minio:9000
      - MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY}
      - MINIO_SECRET_KEY=${MINIO_SECRET_KEY}
      - CELERY_BROKER=redis://redis:6379/1
    depends_on:
      - postgres
      - redis
      - minio
    volumes:
      - tts_models:/app/models
      - audio_cache:/app/cache
      - ./logs:/app/logs
    deploy:
      resources:
        limits:
          memory: 6G
        reservations:
          memory: 3G

  # gRPC Job Service
  job-service:
    build:
      context: ./grpc_services/job
      dockerfile: Dockerfile
    ports:
      - "50054:50054"
    environment:
      - DATABASE_URL=postgresql://voxify:password@postgres:5432/voxify
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER=redis://redis:6379/1
    depends_on:
      - postgres
      - redis

  # Celery Worker
  celery-worker:
    build:
      context: ./grpc_services/voice
      dockerfile: Dockerfile
    command: celery -A tasks worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://voxify:password@postgres:5432/voxify
      - CELERY_BROKER=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/1
    depends_on:
      - redis
      - postgres
    volumes:
      - voice_models:/app/models
      - audio_cache:/app/cache

  # Database
  postgres:
    image: postgres:13
    environment:
      - POSTGRES_DB=voxify
      - POSTGRES_USER=voxify
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"

  # Redis Cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # File Storage
  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=${MINIO_ACCESS_KEY}
      - MINIO_ROOT_PASSWORD=${MINIO_SECRET_KEY}
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data

  # Nginx Proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - rest-gateway

volumes:
  postgres_data:
  redis_data:
  minio_data:
  voice_models:
  tts_models:
  audio_cache:
```

## Monitoring and Maintenance

### 1. Health Check
```python
# rest_gateway/app/api/health.py
from flask import Blueprint
from flask_restful import Resource, Api
from app.grpc_clients.auth_client import AuthServiceClient
from app.grpc_clients.voice_client import VoiceServiceClient
from app.grpc_clients.tts_client import TTSServiceClient

health_bp = Blueprint('health', __name__)
health_api = Api(health_bp)

class HealthCheckResource(Resource):
    def get(self):
        """System health check"""
        health_status = {
            'status': 'healthy',
            'services': {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Check gRPC service status
        services = [
            ('auth', AuthServiceClient),
            ('voice', VoiceServiceClient),
            ('tts', TTSServiceClient)
        ]
        
        for service_name, client_class in services:
            try:
                client = client_class()
                # Perform simple health check call
                client.health_check()
                health_status['services'][service_name] = 'healthy'
            except Exception as e:
                health_status['services'][service_name] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                health_status['status'] = 'degraded'
        
        status_code = 200 if health_status['status'] == 'healthy' else 503
        return health_status, status_code

health_api.add_resource(HealthCheckResource, '/health')
```

### 2. Logging Configuration
```python
# rest_gateway/app/config.py
import logging
import os
from logging.handlers import RotatingFileHandler

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET') or 'jwt-secret-key'
    
    # gRPC service configuration
    GRPC_AUTH_SERVICE_HOST = os.environ.get('GRPC_AUTH_SERVICE_HOST', 'localhost')
    GRPC_AUTH_SERVICE_PORT = int(os.environ.get('GRPC_AUTH_SERVICE_PORT', '50051'))
    
    # Logging configuration
    LOG_LEVEL = logging.INFO
    LOG_FILE = 'logs/voxify_gateway.log'
    
    @staticmethod
    def init_app(app):
        # Configure logging
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        file_handler = RotatingFileHandler(
            Config.LOG_FILE, 
            maxBytes=10240000, 
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(Config.LOG_LEVEL)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(Config.LOG_LEVEL)
        app.logger.info('Voxify Gateway startup')

class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = logging.DEBUG

class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = logging.WARNING
```


