"""
Authentication API Blueprint
Handles user registration, login, and token management
"""

from flask import Blueprint

# Import routes after blueprint creation to avoid circular imports
# from . import routes

auth_bp = Blueprint("auth", __name__)
