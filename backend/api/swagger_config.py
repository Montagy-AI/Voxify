"""
Swagger Configuration and Data Models
Centralizes API documentation configuration and reusable schemas
"""

from flask_restx import fields


def configure_swagger(api):
    """Configure Swagger documentation with global settings"""
    api.doc = {
        "title": "Voxify API",
        "version": "1.0.0",
        "description": "RESTful API for the Voxify voice cloning and TTS synthesis platform",
        "contact": {"name": "Voxify Team", "url": "https://voxify.app", "email": "support@voxify.app"},
        "license": {"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
        "host": "api.voxify.app",
        "basePath": "/api/v1",
        "schemes": ["https", "http"],
        "tags": [
            {"name": "Authentication", "description": "User authentication and token management"},
            {"name": "Voice Samples", "description": "Voice sample upload and management"},
            {"name": "Voice Clones", "description": "Voice clone creation and management"},
            {"name": "Jobs", "description": "Synthesis job management and monitoring"},
            {"name": "Files", "description": "File download and management"},
        ],
        "security": [{"Bearer": []}],
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization",
                "description": "JWT token in format: Bearer {token}",
            }
        },
    }


def get_common_models(api):
    """Define common data models used across multiple endpoints"""

    # Error response model
    error_model = api.model(
        "Error",
        {
            "success": fields.Boolean(required=True, description="Always false for errors", example=False),
            "error": fields.Nested(
                api.model(
                    "ErrorDetails",
                    {
                        "message": fields.String(required=True, description="Human-readable error message"),
                        "code": fields.String(required=True, description="Machine-readable error code"),
                        "timestamp": fields.String(required=True, description="ISO timestamp of the error"),
                        "details": fields.Raw(description="Additional error details (optional)"),
                    },
                ),
                required=True,
            ),
        },
    )

    # Success response wrapper
    success_wrapper = api.model(
        "SuccessResponse",
        {
            "success": fields.Boolean(required=True, description="Always true for successful responses", example=True),
            "timestamp": fields.String(required=True, description="ISO timestamp of the response"),
            "message": fields.String(description="Optional success message"),
            "data": fields.Raw(description="Response data"),
        },
    )

    # Pagination metadata
    pagination_model = api.model(
        "Pagination",
        {
            "page": fields.Integer(required=True, description="Current page number"),
            "page_size": fields.Integer(required=True, description="Items per page"),
            "total_count": fields.Integer(required=True, description="Total number of items"),
            "total_pages": fields.Integer(required=True, description="Total number of pages"),
            "has_next": fields.Boolean(description="Whether there are more pages"),
            "has_prev": fields.Boolean(description="Whether there are previous pages"),
        },
    )

    return {"error": error_model, "success": success_wrapper, "pagination": pagination_model}


def get_auth_models(api):
    """Define authentication-related data models"""

    # User model
    user_model = api.model(
        "User",
        {
            "id": fields.String(required=True, description="Unique user identifier"),
            "email": fields.String(required=True, description="User email address"),
            "first_name": fields.String(description="User first name"),
            "last_name": fields.String(description="User last name"),
            "is_active": fields.Boolean(description="Whether the user account is active"),
            "email_verified": fields.Boolean(description="Whether the email is verified"),
            "created_at": fields.String(description="Account creation timestamp"),
            "updated_at": fields.String(description="Last update timestamp"),
            "last_login_at": fields.String(description="Last login timestamp"),
        },
    )

    # Registration request
    register_request = api.model(
        "RegisterRequest",
        {
            "email": fields.String(required=True, description="User email address", example="user@example.com"),
            "password": fields.String(
                required=True, description="User password (min 8 characters)", example="SecurePass123!"
            ),
            "first_name": fields.String(description="User first name", example="John"),
            "last_name": fields.String(description="User last name", example="Doe"),
        },
    )

    # Login request
    login_request = api.model(
        "LoginRequest",
        {
            "email": fields.String(required=True, description="User email address", example="user@example.com"),
            "password": fields.String(required=True, description="User password", example="SecurePass123!"),
        },
    )

    # Token response
    token_response = api.model(
        "TokenResponse",
        {
            "access_token": fields.String(required=True, description="JWT access token"),
            "refresh_token": fields.String(required=True, description="JWT refresh token"),
            "user": fields.Nested(user_model, required=True, description="User information"),
        },
    )

    # Profile update request
    profile_update_request = api.model(
        "ProfileUpdateRequest",
        {
            "email": fields.String(description="New email address"),
            "first_name": fields.String(description="New first name"),
            "last_name": fields.String(description="New last name"),
        },
    )

    # Password reset requests
    forgot_password_request = api.model(
        "ForgotPasswordRequest",
        {"email": fields.String(required=True, description="User email address", example="user@example.com")},
    )

    reset_password_request = api.model(
        "ResetPasswordRequest",
        {
            "token": fields.String(required=True, description="Password reset token"),
            "new_password": fields.String(required=True, description="New password", example="NewSecurePass123!"),
        },
    )

    return {
        "user": user_model,
        "register_request": register_request,
        "login_request": login_request,
        "token_response": token_response,
        "profile_update_request": profile_update_request,
        "forgot_password_request": forgot_password_request,
        "reset_password_request": reset_password_request,
    }


def get_voice_models(api):
    """Define voice-related data models"""

    # Voice sample model
    voice_sample_model = api.model(
        "VoiceSample",
        {
            "id": fields.String(required=True, description="Unique sample identifier"),
            "name": fields.String(required=True, description="Sample name"),
            "user_id": fields.String(required=True, description="Owner user ID"),
            "file_path": fields.String(description="File storage path"),
            "file_size": fields.Integer(description="File size in bytes"),
            "original_filename": fields.String(description="Original uploaded filename"),
            "format": fields.String(description="Audio format"),
            "duration": fields.Float(description="Duration in seconds"),
            "sample_rate": fields.Integer(description="Audio sample rate"),
            "channels": fields.Integer(description="Number of audio channels"),
            "status": fields.String(
                description="Processing status", enum=["uploaded", "processing", "ready", "failed"]
            ),
            "quality_score": fields.Float(description="Audio quality score"),
            "created_at": fields.String(description="Creation timestamp"),
            "updated_at": fields.String(description="Last update timestamp"),
        },
    )

    # Voice clone model
    voice_clone_model = api.model(
        "VoiceClone",
        {
            "clone_id": fields.String(required=True, description="Unique clone identifier"),
            "name": fields.String(required=True, description="Clone name"),
            "description": fields.String(description="Clone description"),
            "status": fields.String(description="Clone status", enum=["training", "ready", "failed"]),
            "language": fields.String(description="Primary language code"),
            "clone_type": fields.String(description="Clone creation method", enum=["upload", "record"]),
            "ref_text": fields.String(description="Reference text used for cloning"),
            "created_at": fields.String(description="Creation timestamp"),
            "is_active": fields.Boolean(description="Whether the clone is active"),
            "model_type": fields.String(description="Voice model type", example="f5_tts"),
            "quality_metrics": fields.Nested(
                api.model(
                    "QualityMetrics",
                    {
                        "similarity_score": fields.Float(description="Voice similarity score"),
                        "stability_score": fields.Float(description="Voice stability score"),
                        "model_type": fields.String(description="Model type used"),
                    },
                )
            ),
        },
    )

    # Voice clone creation request
    clone_creation_request = api.model(
        "CloneCreationRequest",
        {
            "sample_ids": fields.List(fields.String, required=True, description="List of sample IDs to use"),
            "name": fields.String(required=True, description="Clone name", example="My Voice Clone"),
            "ref_text": fields.String(required=True, description="Reference text for the primary sample"),
            "description": fields.String(description="Clone description"),
            "language": fields.String(description="Language code", example="en-US"),
            "clone_type": fields.String(description="Clone creation method", example="upload", enum=["upload", "record"]),
        },
    )

    # Voice synthesis request
    synthesis_request = api.model(
        "SynthesisRequest",
        {
            "text": fields.String(required=True, description="Text to synthesize"),
            "speed": fields.Float(description="Speech speed multiplier", example=1.0),
            "language": fields.String(description="Language code"),
            "output_format": fields.String(description="Output format", example="wav"),
        },
    )

    return {
        "voice_sample": voice_sample_model,
        "voice_clone": voice_clone_model,
        "clone_creation_request": clone_creation_request,
        "synthesis_request": synthesis_request,
    }


def get_job_models(api):
    """Define job-related data models"""

    # Synthesis job model
    synthesis_job_model = api.model(
        "SynthesisJob",
        {
            "id": fields.String(required=True, description="Unique job identifier"),
            "user_id": fields.String(required=True, description="Owner user ID"),
            "voice_model_id": fields.String(required=True, description="Voice model used"),
            "text_content": fields.String(required=True, description="Text to synthesize"),
            "text_language": fields.String(description="Text language code"),
            "text_length": fields.Integer(description="Text length in characters"),
            "word_count": fields.Integer(description="Number of words"),
            "status": fields.String(
                description="Job status", enum=["pending", "processing", "completed", "failed", "cancelled"]
            ),
            "progress": fields.Float(description="Progress percentage (0.0-1.0)"),
            "output_path": fields.String(description="Output file path"),
            "output_format": fields.String(description="Output audio format"),
            "sample_rate": fields.Integer(description="Audio sample rate"),
            "speed": fields.Float(description="Speech speed multiplier"),
            "pitch": fields.Float(description="Pitch multiplier"),
            "volume": fields.Float(description="Volume multiplier"),
            "duration": fields.Float(description="Generated audio duration"),
            "processing_time_ms": fields.Integer(description="Processing time in milliseconds"),
            "error_message": fields.String(description="Error message if failed"),
            "created_at": fields.String(description="Creation timestamp"),
            "started_at": fields.String(description="Processing start timestamp"),
            "completed_at": fields.String(description="Completion timestamp"),
            "updated_at": fields.String(description="Last update timestamp"),
        },
    )

    # Job creation request
    job_creation_request = api.model(
        "JobCreationRequest",
        {
            "text_content": fields.String(required=True, description="Text to synthesize"),
            "voice_model_id": fields.String(required=True, description="Voice model ID to use"),
            "text_language": fields.String(description="Text language code", example="en-US"),
            "output_format": fields.String(description="Output audio format", example="wav"),
            "sample_rate": fields.Integer(description="Audio sample rate", example=22050),
            "speed": fields.Float(description="Speech speed multiplier", example=1.0),
            "pitch": fields.Float(description="Pitch multiplier", example=1.0),
            "volume": fields.Float(description="Volume multiplier", example=1.0),
            "config": fields.Raw(description="Additional synthesis configuration"),
        },
    )

    # Job update request
    job_update_request = api.model(
        "JobUpdateRequest",
        {
            "text_content": fields.String(description="Updated text content"),
            "speed": fields.Float(description="Updated speech speed"),
            "pitch": fields.Float(description="Updated pitch"),
            "volume": fields.Float(description="Updated volume"),
            "output_format": fields.String(description="Updated output format"),
            "sample_rate": fields.Integer(description="Updated sample rate"),
            "config": fields.Raw(description="Updated synthesis configuration"),
        },
    )

    # Job status update request
    job_status_update = api.model(
        "JobStatusUpdate",
        {
            "status": fields.String(
                description="New job status", enum=["pending", "processing", "completed", "failed", "cancelled"]
            ),
            "progress": fields.Float(description="Job progress (0.0-1.0)"),
            "error_message": fields.String(description="Error message if failed"),
            "output_path": fields.String(description="Path to generated audio file"),
            "duration": fields.Float(description="Duration of generated audio"),
            "processing_time_ms": fields.Integer(description="Processing time in milliseconds"),
        },
    )

    return {
        "synthesis_job": synthesis_job_model,
        "job_creation_request": job_creation_request,
        "job_update_request": job_update_request,
        "job_status_update": job_status_update,
    }


def get_file_models(api):
    """Define file-related data models"""

    # File info model
    file_info_model = api.model(
        "FileInfo",
        {
            "job_id": fields.String(required=True, description="Associated job ID"),
            "text_content": fields.String(description="Original text content"),
            "language": fields.String(description="Text language"),
            "status": fields.String(description="Job status"),
            "output_path": fields.String(description="File path"),
            "duration": fields.Float(description="Audio duration in seconds"),
            "file_size": fields.Integer(description="File size in bytes"),
            "file_exists": fields.Boolean(description="Whether the file exists on server"),
            "created_at": fields.String(description="Creation timestamp"),
            "completed_at": fields.String(description="Completion timestamp"),
        },
    )

    return {"file_info": file_info_model}
