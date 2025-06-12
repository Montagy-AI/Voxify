"""
Voice API Blueprint
Handles voice sample management and processing
"""

from flask import Blueprint

voice_bp = Blueprint('voice', __name__)

# Import routes after blueprint creation to avoid circular imports
from . import routes 