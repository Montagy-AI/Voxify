"""
Voice Sample Management Routes
Handles voice sample upload, processing, and management
"""

import os
import uuid
import tempfile
import soundfile as sf
from pathlib import Path
from datetime import datetime
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import get_database_manager
from database.models import VoiceSample

# Import the blueprint from __init__.py
from . import voice_bp

# Allowed audio file extensions
ALLOWED_EXTENSIONS = {'wav', 'mp3'}

def allowed_file(filename: str) -> bool:
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_audio_metadata(file_path: str) -> dict:
    """Extract metadata from audio file."""
    with sf.SoundFile(file_path) as audio_file:
        return {
            'duration': len(audio_file) / audio_file.samplerate,
            'sample_rate': audio_file.samplerate,
            'channels': audio_file.channels,
            'format': audio_file.format
        }

@voice_bp.route('/samples', methods=['POST'])
@jwt_required()
def upload_voice_sample():
    """
    Upload and process a voice sample.
    
    Request:
        - name: Sample name (required)
        - file: Audio file (required, WAV or MP3)
    
    Returns:
        JSON response with sample_id and processing status
    """
    # Get the current user's ID
    user_id = get_jwt_identity()
    
    # Validate name parameter
    name = request.form.get('name')
    if not name:
        return jsonify({
            'success': False,
            'error': 'Name is required for voice samples'
        }), 400
    
    # Validate file
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No file provided'
        }), 400
    
    file = request.files['file']
    if not file or not allowed_file(file.filename):
        return jsonify({
            'success': False,
            'error': 'Invalid file type. Only WAV and MP3 files are allowed'
        }), 400
    
    try:
        # Generate unique sample ID
        sample_id = str(uuid.uuid4())
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
        
        # Extract audio metadata
        metadata = extract_audio_metadata(temp_path)
        
        # Get database session
        db = get_database_manager()
        
        # Store metadata in SQLite
        with db.get_session() as session:
            voice_sample = VoiceSample(
                id=sample_id,
                name=name,
                user_id=user_id,
                file_path=temp_path,  # Temporary path
                file_size=os.path.getsize(temp_path),
                original_filename=file.filename,
                format=metadata['format'],
                duration=metadata['duration'],
                sample_rate=metadata['sample_rate'],
                channels=metadata['channels'],
                status='uploaded',
                processing_start_time=datetime.utcnow()
            )
            session.add(voice_sample)
            session.commit()
        
        # TODO: Send to TTS service for embedding generation
        # The TTS service will:
        # 1. Generate the voice embedding
        # 2. Store it in ChromaDB
        # 3. Update the VoiceSample status to 'ready'
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        return jsonify({
            'success': True,
            'data': {
                'sample_id': sample_id,
                'name': name,
                'duration': metadata['duration'],
                'format': metadata['format'],
                'status': 'uploaded',
                'message': 'Voice sample uploaded successfully. Processing started.'
            }
        }), 201
        
    except Exception as e:
        # Clean up temporary file if it exists
        if 'temp_path' in locals():
            try:
                os.unlink(temp_path)
            except:
                pass
        
        return jsonify({
            'success': False,
            'error': f'Error processing voice sample: {str(e)}'
        }), 500

@voice_bp.route('/samples', methods=['GET'])
@jwt_required()
def list_voice_samples():
    """
    List all voice samples for the authenticated user.
    
    Query Parameters:
        - page: Page number (default: 1)
        - page_size: Items per page (default: 20)
        - status: Filter by status (optional)
    
    Returns:
        JSON response with list of voice samples and pagination info
    """
    # Get the current user's ID
    user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    status = request.args.get('status')
    
    db = get_database_manager()
    with db.get_session() as session:
        query = session.query(VoiceSample).filter_by(user_id=user_id)
        
        # Filter by status if provided
        if status:
            query = query.filter_by(status=status)
        
        samples = query.order_by(VoiceSample.created_at.desc())\
            .offset((page - 1) * page_size)\
            .limit(page_size)\
            .all()
        
        total = query.count()
        
        return jsonify({
            'success': True,
            'data': {
                'samples': [sample.to_dict() for sample in samples],
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total_count': total,
                    'total_pages': (total + page_size - 1) // page_size
                }
            }
        })

@voice_bp.route('/samples/<sample_id>', methods=['GET'])
@jwt_required()
def get_voice_sample(sample_id: str):
    """
    Get details of a specific voice sample.
    
    Args:
        sample_id: The unique identifier of the voice sample
    
    Returns:
        JSON response with sample details
    """
    # Get the current user's ID
    user_id = get_jwt_identity()
    
    db = get_database_manager()
    with db.get_session() as session:
        sample = session.query(VoiceSample).filter_by(id=sample_id, user_id=user_id).first()
        if not sample:
            return jsonify({
                'success': False,
                'error': 'Voice sample not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': sample.to_dict()
        })

@voice_bp.route('/samples/<sample_id>', methods=['DELETE'])
@jwt_required()
def delete_voice_sample(sample_id: str):
    """
    Delete a voice sample and its associated data.
    
    Args:
        sample_id: The unique identifier of the voice sample
    
    Returns:
        JSON response with deletion status
    """
    # Get the current user's ID
    user_id = get_jwt_identity()
    
    db = get_database_manager()
    with db.get_session() as session:
        sample = session.query(VoiceSample).filter_by(id=sample_id, user_id=user_id).first()
        if not sample:
            return jsonify({
                'success': False,
                'error': 'Voice sample not found'
            }), 404
        
        # Delete from SQLite
        session.delete(sample)
        session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'message': 'Voice sample deleted successfully'
            }
        }) 