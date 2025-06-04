"""
Admin API Routes
Implements administrative endpoints for user management
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc
from . import admin_bp
from functools import wraps

# Import database models
from Voxify.backend.database.models import User, get_database_manager

def admin_required(fn):
    """
    Decorator to check if the user is an admin
    """
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        # Get current user
        user_id = get_jwt_identity()

        # Check if user exists and is admin
        db_manager = get_database_manager()
        session = db_manager.get_session()

        try:
            user = session.query(User).filter_by(id=user_id).first()

            # For simplicity, we're considering users with 'enterprise' subscription as admins
            # In a real application, you would have a dedicated admin flag or role
            if not user or user.subscription_type != 'enterprise':
                return jsonify({"error": "Admin privileges required"}), 403

            return fn(*args, **kwargs)
        finally:
            session.close()

    return wrapper

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """
    Get a list of all users

    Query Parameters:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 20)
    - sort_by: Field to sort by (default: created_at)
    - order: Sort order (asc or desc, default: desc)
    - filter: Filter by subscription_type or is_active

    Returns:
    - 200: List of users
    - 400: Invalid request parameters
    - 403: Not authorized
    """
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    sort_by = request.args.get('sort_by', 'created_at')
    order = request.args.get('order', 'desc')
    subscription_filter = request.args.get('subscription_type')
    active_filter = request.args.get('is_active')

    # Validate parameters
    if page < 1 or per_page < 1 or per_page > 100:
        return jsonify({"error": "Invalid pagination parameters"}), 400

    if sort_by not in ['created_at', 'email', 'last_login_at', 'subscription_type']:
        return jsonify({"error": f"Invalid sort field: {sort_by}"}), 400

    if order not in ['asc', 'desc']:
        return jsonify({"error": f"Invalid sort order: {order}"}), 400

    # Get users from database
    db_manager = get_database_manager()
    session = db_manager.get_session()

    try:
        # Build query
        query = session.query(User)

        # Apply filters
        if subscription_filter:
            query = query.filter(User.subscription_type == subscription_filter)

        if active_filter is not None:
            is_active = active_filter.lower() in ['true', '1', 'yes']
            query = query.filter(User.is_active == is_active)

        # Apply sorting
        if order == 'desc':
            query = query.order_by(desc(getattr(User, sort_by)))
        else:
            query = query.order_by(getattr(User, sort_by))

        # Apply pagination
        total = query.count()
        users = query.limit(per_page).offset((page - 1) * per_page).all()

        # Convert to dict
        users_data = [user.to_dict() for user in users]

        # Return response
        return jsonify({
            "users": users_data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()
