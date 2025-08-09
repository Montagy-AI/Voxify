"""
Job Management API Blueprint
Handles synthesis job listing, monitoring, and cancellation
"""

from flask import Blueprint

job_bp = Blueprint("job", __name__)

# Import routes after blueprint creation to avoid circular imports
from . import routes  # noqa: F401, E402

__all__ = ["job_bp"]
