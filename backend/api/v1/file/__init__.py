"""
File API Blueprint
Handles file upload, download, and management
"""

from flask import Blueprint

# Import routes after blueprint creation to avoid circular imports
# from . import routes

file_bp = Blueprint("file", __name__)

__all__ = ["file_bp"]
