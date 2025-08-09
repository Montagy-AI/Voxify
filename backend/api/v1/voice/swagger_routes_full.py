"""
Voice Management API Routes with Full Swagger Documentation
RESTful endpoints that connect to existing functionality with comprehensive OpenAPI documentation
"""

from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity

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

error_model = voice_ns.model(
    "Error",
    {
        "success": fields.Boolean(required=True, description="Always false for errors", example=False),
        "error": fields.String(required=True, description="Error message"),
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


@voice_ns.route("/samples")
class VoiceSamplesResource(Resource):
    @voice_ns.doc("upload_voice_sample", security="Bearer")
    @voice_ns.expect(upload_parser, validate=False)  # Disable validation for file uploads
    @voice_ns.marshal_with(success_response, code=201, description="Voice sample uploaded successfully")
    @voice_ns.response(400, "Invalid file format, missing parameters, or file too large", error_model)
    @voice_ns.response(401, "Authentication required", error_model)
    @voice_ns.response(409, "Duplicate voice sample detected", error_model)
    @voice_ns.response(500, "Upload or processing failed", error_model)
    @jwt_required()
    def post(self):
        """Upload and process a voice sample

        Uploads an audio file and processes it for voice cloning.

        **Supported formats**: WAV, MP3
        **Maximum file size**: 16MB
        **Recommended duration**: 3-30 seconds
        **Sample rate**: 16kHz or higher recommended

        The system will:
        1. Validate the audio file format and quality
        2. Extract audio metadata (duration, sample rate, etc.)
        3. Generate voice embeddings for similarity detection
        4. Check for duplicate samples
        5. Store the processed sample for voice cloning

        **Note**: Duplicate samples will be rejected to maintain uniqueness.
        """
        from .samples import upload_voice_sample

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
        from .samples import list_voice_samples

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
        from .samples import get_voice_sample

        return get_voice_sample(sample_id)

    @voice_ns.doc("delete_voice_sample", security="Bearer")
    @voice_ns.marshal_with(success_response, code=200, description="Voice sample deleted successfully")
    @voice_ns.response(404, "Voice sample not found", error_model)
    @voice_ns.response(401, "Authentication required", error_model)
    @voice_ns.response(500, "Failed to delete sample", error_model)
    @jwt_required()
    def delete(self, sample_id):
        """Delete a voice sample and its associated data"""
        from .samples import delete_voice_sample

        return delete_voice_sample(sample_id)


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
        from .clones import create_voice_clone

        return create_voice_clone()

    @voice_ns.doc("list_voice_clones", security="Bearer")
    @voice_ns.param("page", "Page number", type="integer", default=1)
    @voice_ns.param("page_size", "Items per page", type="integer", default=20)
    @voice_ns.marshal_with(success_response, code=200, description="Voice clones retrieved successfully")
    @voice_ns.response(401, "Authentication required", error_model)
    @voice_ns.response(500, "Failed to retrieve clones", error_model)
    @jwt_required()
    def get(self):
        """List all voice clones for the authenticated user"""
        from .clones import list_voice_clones

        return list_voice_clones()


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
        from .clones import get_voice_clone

        return get_voice_clone(clone_id)

    @voice_ns.doc("delete_voice_clone", security="Bearer")
    @voice_ns.marshal_with(success_response, code=200, description="Voice clone deleted successfully")
    @voice_ns.response(404, "Voice clone not found", error_model)
    @voice_ns.response(401, "Authentication required", error_model)
    @voice_ns.response(500, "Failed to delete clone", error_model)
    @jwt_required()
    def delete(self, clone_id):
        """Remove a voice clone"""
        from .clones import delete_voice_clone

        return delete_voice_clone(clone_id)


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
        from .clones import select_voice_clone

        return select_voice_clone(clone_id)


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
        from .clones import synthesize_with_clone

        return synthesize_with_clone(clone_id)


@voice_ns.route("/models")
class VoiceModelsResource(Resource):
    @voice_ns.doc("get_voice_models")
    @voice_ns.marshal_with(success_response, code=200, description="Available voice models retrieved")
    @voice_ns.response(500, "Failed to retrieve models", error_model)
    def get(self):
        """Get available voice models"""
        # Import and call the function from __init__.py
        from . import get_voice_models

        return get_voice_models()


@voice_ns.route("/info")
class VoiceServiceInfoResource(Resource):
    @voice_ns.doc("voice_service_info")
    @voice_ns.marshal_with(success_response, code=200, description="Voice service information retrieved")
    @voice_ns.response(500, "Failed to retrieve service info", error_model)
    def get(self):
        """Get voice service information"""
        # Import and call the function from __init__.py
        from . import voice_service_info

        return voice_service_info()
