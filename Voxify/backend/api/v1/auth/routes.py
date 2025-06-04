"""
Authentication API Routes
Implements user registration, login, and token management endpoints
"""

from flask import request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from . import auth_bp
from datetime import datetime

# Import database models
from Voxify.backend.database.models import User, get_database_manager

# Import utility functions
from Voxify.backend.api.utils.password import hash_password, verify_password, validate_password_strength, validate_email

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user

    Request Body:
    - email: User's email address
    - password: User's password
    - first_name: User's first name (optional)
    - last_name: User's last name (optional)

    Returns:
    - 201: User created successfully
    - 400: Invalid request data
    - 409: Email already exists
    """
    # Get request data
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Validate required fields
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # Validate email format
    is_valid, error_message = validate_email(email)
    if not is_valid:
        return jsonify({"error": error_message}), 400

    # Validate password strength
    is_valid, error_message = validate_password_strength(password)
    if not is_valid:
        return jsonify({"error": error_message}), 400

    # Hash password
    password_hash = hash_password(password)

    # Create user object
    new_user = User(
        email=email,
        password_hash=password_hash,
        first_name=data.get('first_name'),
        last_name=data.get('last_name')
    )

    # Save to database
    db_manager = get_database_manager()
    session = db_manager.get_session()

    try:
        session.add(new_user)
        session.commit()

        # Return success response
        return jsonify({
            "message": "User registered successfully",
            "user": new_user.to_dict()
        }), 201

    except IntegrityError:
        session.rollback()
        return jsonify({"error": "Email already exists"}), 409
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate a user and issue JWT tokens

    Request Body:
    - email: User's email address
    - password: User's password

    Returns:
    - 200: Authentication successful
    - 400: Invalid request data
    - 401: Invalid credentials
    """
    # Get request data
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Validate required fields
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # Get user from database
    db_manager = get_database_manager()
    session = db_manager.get_session()

    try:
        user = session.query(User).filter_by(email=email).first()

        # Check if user exists and password is correct
        if not user or not verify_password(password, user.password_hash):
            return jsonify({"error": "Invalid email or password"}), 401

        # Check if user is active
        if not user.is_active:
            return jsonify({"error": "Account is disabled"}), 403

        # Update last login timestamp
        user.last_login_at = datetime.utcnow()
        session.commit()

        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        # Return tokens and user data
        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict()
        }), 200

    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()
