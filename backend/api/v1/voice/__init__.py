"""
Voice Service Package
Handles voice sample management, voice cloning, and TTS synthesis
"""

from flask import Blueprint

# Create the voice blueprint
voice_bp = Blueprint("voice", __name__)

# Import route modules to register endpoints
# This ensures all routes from samples.py and clones.py are registered
from . import samples  # This will register sample routes
from . import clones  # This will register clone routes


# Add voice models endpoint (required by tests)
@voice_bp.route("/models", methods=["GET"])
def get_voice_models():
    """Get available voice models"""
    return {
        "success": True,
        "data": {
            "models": [
                {
                    "id": "f5-tts",
                    "name": "F5-TTS Zero-Shot",
                    "description": "Zero-shot voice cloning using F5-TTS",
                    "type": "zero_shot",
                    "languages": [
                        "zh-CN", "zh-TW", "en-US", "en-GB",  # Native support
                        "ja-JP", "fr-FR", "de-DE", "es-ES", "it-IT", "ru-RU", "hi-IN", "fi-FI",  # Specialized models
                        "ko-KR", "pt-BR", "ar-SA", "th-TH", "vi-VN"  # Basic support
                    ],
                    "max_duration": 30,
                    "min_duration": 3,
                }
            ]
        },
    }


@voice_bp.route("/info", methods=["GET"])
def voice_service_info():
    """Get voice service information"""
    return {
        "success": True,
        "data": {
            "service": "Voxify Voice Service",
            "version": "1.0.0",
            "features": [
                "Voice sample upload and management",
                "Voice cloning with F5-TTS",
                "Speech synthesis",
                "Voice embedding generation",
            ],
            "supported_formats": ["wav", "mp3"],
            "max_sample_duration": 30,
            "min_sample_duration": 3,
        },
    }
