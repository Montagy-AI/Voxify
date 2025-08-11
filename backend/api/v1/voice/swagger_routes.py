"""
Voice Management API Routes with Swagger Documentation
RESTful endpoints for voice samples and clones with comprehensive OpenAPI documentation
"""

import os
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone
from werkzeug.datastructures import FileStorage

# Import the existing functionality
from database import get_database_manager
from database.models import VoiceSample, VoiceModel
from .f5_tts_service import get_f5_tts_service, VoiceCloneConfig

# Create namespace
voice_ns = Namespace(
    "Voice Management", description="Voice sample upload, processing, and clone management", path="/voice"
)

# Define upload parser for file uploads
upload_parser = voice_ns.parser()
upload_parser.add_argument(
    "file", location="files", type="file", required=True, help="Audio file to upload (WAV or MP3, max 16MB)"
)
upload_parser.add_argument("name", location="form", type=str, required=True, help="Name for the voice sample")

# Define data models
voice_sample_model = voice_ns.model(
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
        "status": fields.String(description="Processing status", enum=["uploaded", "processing", "ready", "failed"]),
        "quality_score": fields.Float(description="Audio quality score"),
        "created_at": fields.String(description="Creation timestamp"),
        "updated_at": fields.String(description="Last update timestamp"),
    },
)

voice_clone_model = voice_ns.model(
    "VoiceClone",
    {
        "clone_id": fields.String(required=True, description="Unique clone identifier"),
        "name": fields.String(required=True, description="Clone name"),
        "description": fields.String(description="Clone description"),
        "status": fields.String(description="Clone status", enum=["training", "ready", "failed"]),
        "language": fields.String(description="Primary language code"),
        "created_at": fields.String(description="Creation timestamp"),
        "is_active": fields.Boolean(description="Whether the clone is active"),
        "model_type": fields.String(description="Voice model type", example="f5_tts"),
        "quality_metrics": fields.Nested(
            voice_ns.model(
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

clone_creation_request = voice_ns.model(
    "CloneCreationRequest",
    {
        "sample_ids": fields.List(fields.String, required=True, description="List of sample IDs to use"),
        "name": fields.String(required=True, description="Clone name", example="My Voice Clone"),
        "ref_text": fields.String(required=True, description="Reference text for the primary sample"),
        "description": fields.String(description="Clone description"),
        "language": fields.String(description="Language code", example="en-US"),
    },
)

synthesis_request = voice_ns.model(
    "SynthesisRequest",
    {
        "text": fields.String(required=True, description="Text to synthesize"),
        "speed": fields.Float(description="Speech speed multiplier", example=1.0),
        "language": fields.String(description="Language code"),
        "output_format": fields.String(description="Output format", example="wav"),
    },
)

pagination_model = voice_ns.model(
    "Pagination",
    {
        "page": fields.Integer(required=True, description="Current page number"),
        "page_size": fields.Integer(required=True, description="Items per page"),
        "total_count": fields.Integer(required=True, description="Total number of items"),
        "total_pages": fields.Integer(required=True, description="Total number of pages"),
    },
)

error_model = voice_ns.model(
    "Error",
    {
        "success": fields.Boolean(required=True, description="Always false for errors", example=False),
        "error": fields.Nested(
            voice_ns.model(
                "ErrorDetails",
                {
                    "message": fields.String(required=True, description="Human-readable error message"),
                    "code": fields.String(required=True, description="Machine-readable error code"),
                    "timestamp": fields.String(required=True, description="ISO timestamp of the error"),
                },
            ),
            required=True,
        ),
    },
)

success_response = voice_ns.model(
    "SuccessResponse",
    {
        "success": fields.Boolean(required=True, description="Always true for successful responses", example=True),
        "timestamp": fields.String(required=True, description="ISO timestamp of the response"),
        "message": fields.String(description="Optional success message"),
        "data": fields.Raw(description="Response data"),
    },
)


# Helper functions
def error_response(message: str, code: str = None, status_code: int = 400):
    """Create standardized error response"""
    response = {
        "success": False,
        "error": {
            "message": message,
            "code": code or f"ERROR_{status_code}",
            "timestamp": datetime.utcnow().isoformat(),
        },
    }
    return response, status_code


def success_response_data(data=None, message: str = None, status_code: int = 200):
    """Create standardized success response"""
    response = {"success": True, "timestamp": datetime.utcnow().isoformat()}
    if data is not None:
        response["data"] = data
    if message:
        response["message"] = message
    return response, status_code


@voice_ns.route("/samples")
class VoiceSamplesResource(Resource):
    @voice_ns.doc("upload_voice_sample", security="Bearer")
    @voice_ns.expect(upload_parser)
    @voice_ns.marshal_with(success_response, code=201, description="Voice sample uploaded successfully")
    @voice_ns.response(400, "Invalid file or missing parameters", error_model)
    @voice_ns.response(401, "Authentication required", error_model)
    @voice_ns.response(500, "Upload failed", error_model)
    @jwt_required()
    def post(self):
        """Upload and process a voice sample"""
        # Import here to avoid circular imports
        from .samples import upload_voice_sample

        # Call the actual function from the blueprint
        return upload_voice_sample()

    @voice_ns.doc("list_voice_samples", security="Bearer")
    @voice_ns.param("page", "Page number", type="integer", default=1)
    @voice_ns.param("page_size", "Items per page", type="integer", default=20)
    @voice_ns.param("status", "Filter by status", type="string", enum=["uploaded", "processing", "ready", "failed"])
    @voice_ns.marshal_with(success_response, code=200, description="Voice samples retrieved successfully")
    @voice_ns.response(401, "Authentication required", error_model)
    @voice_ns.response(500, "Failed to retrieve samples", error_model)
    @jwt_required()
    def get(self):
        """List all voice samples for the authenticated user"""
        # Import here to avoid circular imports
        from .samples import list_voice_samples

        # Call the actual function from the blueprint
        return list_voice_samples()


@voice_ns.route("/samples/<string:sample_id>")
class VoiceSampleResource(Resource):
    @voice_ns.doc("get_voice_sample", security="Bearer")
    @voice_ns.marshal_with(success_response, code=200, description="Voice sample details retrieved")
    @voice_ns.response(404, "Voice sample not found", error_model)
    @voice_ns.response(401, "Authentication required", error_model)
    @voice_ns.response(500, "Failed to retrieve sample", error_model)
    @jwt_required()
    def get(self, sample_id):
        """Get details of a specific voice sample"""
        return success_response_data(
            data={"message": f"Voice sample {sample_id} details - implement with existing logic"}
        )

    @voice_ns.doc("delete_voice_sample", security="Bearer")
    @voice_ns.marshal_with(success_response, code=200, description="Voice sample deleted successfully")
    @voice_ns.response(404, "Voice sample not found", error_model)
    @voice_ns.response(401, "Authentication required", error_model)
    @voice_ns.response(500, "Failed to delete sample", error_model)
    @jwt_required()
    def delete(self, sample_id):
        """Delete a voice sample and its associated data"""
        return success_response_data(
            data={"message": f"Voice sample {sample_id} deletion - implement with existing logic"}
        )


@voice_ns.route("/clones")
class VoiceClonesResource(Resource):
    @voice_ns.doc("create_voice_clone", security="Bearer")
    @voice_ns.expect(clone_creation_request)
    @voice_ns.marshal_with(success_response, code=201, description="Voice clone created successfully")
    @voice_ns.response(400, "Invalid request data or samples not ready", error_model)
    @voice_ns.response(401, "Authentication required", error_model)
    @voice_ns.response(500, "Clone creation failed", error_model)
    @jwt_required()
    def post(self):
        """Generate a new voice clone from processed samples using F5-TTS"""
        return success_response_data(
            data={"message": "Voice clone creation endpoint - implement with existing logic"}, status_code=201
        )

    @voice_ns.doc("list_voice_clones", security="Bearer")
    @voice_ns.param("page", "Page number", type="integer", default=1)
    @voice_ns.param("page_size", "Items per page", type="integer", default=20)
    @voice_ns.marshal_with(success_response, code=200, description="Voice clones retrieved successfully")
    @voice_ns.response(401, "Authentication required", error_model)
    @voice_ns.response(500, "Failed to retrieve clones", error_model)
    @jwt_required()
    def get(self):
        """List all voice clones for the authenticated user"""
        return success_response_data(data={"message": "Voice clones list endpoint - implement with existing logic"})


@voice_ns.route("/clones/<string:clone_id>")
class VoiceCloneResource(Resource):
    @voice_ns.doc("get_voice_clone", security="Bearer")
    @voice_ns.marshal_with(success_response, code=200, description="Voice clone details retrieved")
    @voice_ns.response(404, "Voice clone not found", error_model)
    @voice_ns.response(401, "Authentication required", error_model)
    @voice_ns.response(500, "Failed to retrieve clone", error_model)
    @jwt_required()
    def get(self, clone_id):
        """Get details of a specific voice clone"""
        return success_response_data(
            data={"message": f"Voice clone {clone_id} details - implement with existing logic"}
        )

    @voice_ns.doc("delete_voice_clone", security="Bearer")
    @voice_ns.marshal_with(success_response, code=200, description="Voice clone deleted successfully")
    @voice_ns.response(404, "Voice clone not found", error_model)
    @voice_ns.response(401, "Authentication required", error_model)
    @voice_ns.response(500, "Failed to delete clone", error_model)
    @jwt_required()
    def delete(self, clone_id):
        """Remove a voice clone"""
        return success_response_data(
            data={"message": f"Voice clone {clone_id} deletion - implement with existing logic"}
        )


@voice_ns.route("/clones/<string:clone_id>/select")
class VoiceCloneSelectionResource(Resource):
    @voice_ns.doc("select_voice_clone", security="Bearer")
    @voice_ns.marshal_with(success_response, code=200, description="Voice clone selected successfully")
    @voice_ns.response(404, "Voice clone not found", error_model)
    @voice_ns.response(401, "Authentication required", error_model)
    @voice_ns.response(500, "Failed to select clone", error_model)
    @jwt_required()
    def post(self, clone_id):
        """Set a voice clone as the active one for synthesis"""
        return success_response_data(
            data={"message": f"Voice clone {clone_id} selection - implement with existing logic"}
        )


@voice_ns.route("/clones/<string:clone_id>/synthesize")
class VoiceCloneSynthesisResource(Resource):
    @voice_ns.doc("synthesize_with_clone", security="Bearer")
    @voice_ns.expect(synthesis_request)
    @voice_ns.marshal_with(success_response, code=200, description="Speech synthesis completed successfully")
    @voice_ns.response(400, "Invalid request data", error_model)
    @voice_ns.response(404, "Voice clone not found", error_model)
    @voice_ns.response(401, "Authentication required", error_model)
    @voice_ns.response(500, "Synthesis failed", error_model)
    @jwt_required()
    def post(self, clone_id):
        """Synthesize speech using a specific voice clone with F5-TTS"""
        return success_response_data(
            data={"message": f"Voice clone {clone_id} synthesis - implement with existing logic"}
        )


@voice_ns.route("/models")
class VoiceModelsResource(Resource):
    @voice_ns.doc("get_voice_models")
    @voice_ns.marshal_with(success_response, code=200, description="Available voice models retrieved")
    @voice_ns.response(500, "Failed to retrieve models", error_model)
    def get(self):
        """Get available voice models"""
        return success_response_data(
            data={
                "models": [
                    {
                        "id": "f5-tts",
                        "name": "F5-TTS Zero-Shot",
                        "description": "Zero-shot voice cloning using F5-TTS",
                        "type": "zero_shot",
                        "languages": [
                            "zh-CN",
                            "zh-TW",
                            "en-US",
                            "en-GB",  # Native support
                            "ja-JP",
                            "fr-FR",
                            "de-DE",
                            "es-ES",
                            "it-IT",
                            "ru-RU",
                            "hi-IN",
                            "fi-FI",  # Specialized
                            "ko-KR",
                            "pt-BR",
                            "ar-SA",
                            "th-TH",
                            "vi-VN",  # Basic support
                        ],
                        "max_duration": 30,
                        "min_duration": 3,
                    }
                ]
            }
        )


@voice_ns.route("/info")
class VoiceServiceInfoResource(Resource):
    @voice_ns.doc("voice_service_info")
    @voice_ns.marshal_with(success_response, code=200, description="Voice service information retrieved")
    @voice_ns.response(500, "Failed to retrieve service info", error_model)
    def get(self):
        """Get voice service information"""
        return success_response_data(
            data={
                "service": "F5-TTS Voice Cloning",
                "version": "1.0.0",
                "supported_formats": ["wav", "mp3"],
                "max_sample_duration": 30,
                "min_sample_duration": 3,
                "supported_languages": [
                    {"code": "zh-CN", "name": "Chinese (Simplified)", "support_level": "native"},
                    {"code": "zh-TW", "name": "Chinese (Traditional)", "support_level": "native"},
                    {"code": "en-US", "name": "English (US)", "support_level": "native"},
                    {"code": "en-GB", "name": "English (UK)", "support_level": "native"},
                    {"code": "ja-JP", "name": "Japanese", "support_level": "specialized"},
                    {"code": "fr-FR", "name": "French", "support_level": "specialized"},
                    {"code": "de-DE", "name": "German", "support_level": "specialized"},
                    {"code": "es-ES", "name": "Spanish", "support_level": "specialized"},
                    {"code": "it-IT", "name": "Italian", "support_level": "specialized"},
                    {"code": "ru-RU", "name": "Russian", "support_level": "specialized"},
                    {"code": "hi-IN", "name": "Hindi", "support_level": "specialized"},
                    {"code": "ko-KR", "name": "Korean", "support_level": "fallback"},
                    {"code": "pt-BR", "name": "Portuguese (Brazil)", "support_level": "fallback"},
                    {"code": "ar-SA", "name": "Arabic", "support_level": "fallback"},
                    {"code": "th-TH", "name": "Thai", "support_level": "fallback"},
                    {"code": "vi-VN", "name": "Vietnamese", "support_level": "fallback"},
                ],
            }
        )
