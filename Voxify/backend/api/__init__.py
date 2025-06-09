"""
Voxify API Package
Flask REST API for the Voxify platform

This package provides the REST API endpoints for the Voxify platform,
including user authentication, voice sample management, and TTS synthesis.
"""

from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os


def create_app(test_config=None):
    """
    Create and configure the Flask application
    
    Parameters
    ----------
    test_config : dict, optional
        Test configuration to override default configuration
        
    Returns
    -------
    Flask
        Configured Flask application
    """

    load_dotenv()

    # Create Flask app
    app = Flask(__name__, instance_relative_config=True)
    
    # Default configuration
    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY', 'Majick'),
        JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY', 'Majick'),
        JWT_ACCESS_TOKEN_EXPIRES=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600)),
        JWT_REFRESH_TOKEN_EXPIRES=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 2592000)),
        DATABASE_URL=os.getenv('DATABASE_URL', 'sqlite:///C:/Users/Jun/Desktop/Voxify/Specifications/Voxify/backend/data/voxify.db')
    )

    # Override with test config if provided
    if test_config is not None:
        app.config.from_mapping(test_config)
    
    # Initialize extensions
    CORS(app)
    jwt = JWTManager(app)
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"]
    )
    
    from .v1.auth import auth_bp
    from .v1.admin import admin_bp
    from .v1.voice import voice_bp

    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/v1/admin')
    app.register_blueprint(voice_bp, url_prefix='/api/v1/voice')

    # Simple index route
    @app.route('/')
    def index():
        return {"message": "Welcome to Voxify API"}

    return app