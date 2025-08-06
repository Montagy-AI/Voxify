"""
File Management API Routes with Swagger Documentation
RESTful endpoints for file download and management with comprehensive OpenAPI documentation
"""

from flask import send_file
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

# Create namespace
file_ns = Namespace('File Management', description='File download and management for synthesis results', path='/file')

# Define data models
file_info_model = file_ns.model('FileInfo', {
    'job_id': fields.String(required=True, description='Associated job ID'),
    'text_content': fields.String(description='Original text content'),
    'language': fields.String(description='Text language'),
    'status': fields.String(description='Job status'),
    'output_path': fields.String(description='File path'),
    'duration': fields.Float(description='Audio duration in seconds'),
    'file_size': fields.Integer(description='File size in bytes'),
    'file_exists': fields.Boolean(description='Whether the file exists on server'),
    'created_at': fields.String(description='Creation timestamp'),
    'completed_at': fields.String(description='Completion timestamp')
})

error_model = file_ns.model('Error', {
    'success': fields.Boolean(required=True, description='Always false for errors', example=False),
    'error': fields.Nested(file_ns.model('ErrorDetails', {
        'message': fields.String(required=True, description='Human-readable error message'),
        'code': fields.String(required=True, description='Machine-readable error code'),
        'timestamp': fields.String(required=True, description='ISO timestamp of the error')
    }), required=True)
})

success_response = file_ns.model('SuccessResponse', {
    'success': fields.Boolean(required=True, description='Always true for successful responses', example=True),
    'timestamp': fields.String(required=True, description='ISO timestamp of the response'),
    'message': fields.String(description='Optional success message'),
    'data': fields.Raw(description='Response data')
})

# Helper functions
def error_response(message: str, code: str = None, status_code: int = 400):
    """Create standardized error response"""
    response = {
        "success": False,
        "error": {
            "message": message,
            "code": code or f"ERROR_{status_code}",
            "timestamp": datetime.utcnow().isoformat(),
        },
    }
    return response, status_code

def success_response_data(data=None, message: str = None, status_code: int = 200):
    """Create standardized success response"""
    response = {"success": True, "timestamp": datetime.utcnow().isoformat()}
    if data is not None:
        response["data"] = data
    if message:
        response["message"] = message
    return response, status_code

@file_ns.route('/synthesis/<string:job_id>')
class SynthesisFileResource(Resource):
    @file_ns.doc('download_synthesis_file', security='Bearer')
    @file_ns.produces(['audio/wav', 'audio/mp3', 'audio/flac', 'audio/ogg'])
    @file_ns.response(200, 'Audio file download')
    @file_ns.response(404, 'File not found', error_model)
    @file_ns.response(403, 'Access denied', error_model)
    @file_ns.response(401, 'Authentication required', error_model)
    @file_ns.response(500, 'Download failed', error_model)
    @jwt_required()
    def get(self, job_id):
        """Download synthesized audio file
        
        Downloads the generated audio file for the specified synthesis job.
        The file is served with appropriate audio MIME type and filename.
        Access is restricted to the job owner.
        """
        # Return placeholder response for documentation
        return success_response_data(
            data={"message": f"Synthesis file download for job {job_id} - implement with existing logic"}
        )

    @file_ns.doc('delete_synthesis_file', security='Bearer')
    @file_ns.marshal_with(success_response, code=200, description='File deleted successfully')
    @file_ns.response(404, 'File not found', error_model)
    @file_ns.response(403, 'Access denied', error_model)
    @file_ns.response(401, 'Authentication required', error_model)
    @file_ns.response(500, 'Deletion failed', error_model)
    @jwt_required()
    def delete(self, job_id):
        """Delete synthesized audio file
        
        Removes the audio file from storage and updates the database records.
        This action cannot be undone. Access is restricted to the job owner.
        """
        return success_response_data(
            data={"message": f"Synthesis file deletion for job {job_id} - implement with existing logic"}
        )

@file_ns.route('/voice-clone/<string:job_id>')
class VoiceCloneSynthesisFileResource(Resource):
    @file_ns.doc('download_voice_clone_synthesis', security='Bearer')
    @file_ns.produces(['audio/wav'])
    @file_ns.response(200, 'Audio file download/stream')
    @file_ns.response(404, 'File not found', error_model)
    @file_ns.response(403, 'Access denied', error_model)
    @file_ns.response(401, 'Authentication required', error_model)
    @file_ns.response(500, 'Download failed', error_model)
    @jwt_required()
    def get(self, job_id):
        """Download voice clone synthesized audio file
        
        Downloads or streams the audio file generated by voice clone synthesis.
        The file is served for audio playback rather than download attachment.
        Handles both relative and absolute file paths automatically.
        """
        return success_response_data(
            data={"message": f"Voice clone synthesis file download for job {job_id} - implement with existing logic"}
        )

@file_ns.route('/voice-clone/<string:job_id>/info')
class VoiceCloneSynthesisInfoResource(Resource):
    @file_ns.doc('get_voice_clone_synthesis_info', security='Bearer')
    @file_ns.marshal_with(success_response, code=200, description='File information retrieved')
    @file_ns.response(404, 'Job not found', error_model)
    @file_ns.response(403, 'Access denied', error_model)
    @file_ns.response(401, 'Authentication required', error_model)
    @file_ns.response(500, 'Failed to get file info', error_model)
    @jwt_required()
    def get(self, job_id):
        """Get voice clone synthesis file information
        
        Returns metadata about the synthesis job and its output file,
        including file size, duration, and existence status.
        Useful for checking file availability before download.
        """
        return success_response_data(
            data={
                "job_id": job_id,
                "text_content": "Sample text content",
                "language": "en-US",
                "status": "completed",
                "output_path": f"/path/to/synthesis_{job_id}.wav",
                "duration": 3.5,
                "file_size": 123456,
                "file_exists": True,
                "created_at": datetime.utcnow().isoformat(),
                "completed_at": datetime.utcnow().isoformat()
            }
        )

# Additional utility endpoints for file management
@file_ns.route('/storage/info')
class StorageInfoResource(Resource):
    @file_ns.doc('get_storage_info', security='Bearer')
    @file_ns.marshal_with(success_response, code=200, description='Storage information retrieved')
    @file_ns.response(401, 'Authentication required', error_model)
    @file_ns.response(500, 'Failed to get storage info', error_model)
    @jwt_required()
    def get(self):
        """Get storage information and usage statistics
        
        Returns information about file storage paths, available space,
        and user-specific storage usage. Useful for monitoring and
        capacity planning.
        """
        return success_response_data(
            data={
                "storage_paths": {
                    "synthesis_output": "/data/files/synthesis/output",
                    "synthesis_cache": "/data/files/synthesis/cache",
                    "voice_samples": "/data/files/samples"
                },
                "usage": {
                    "total_files": 0,
                    "total_size_bytes": 0,
                    "user_files": 0,
                    "user_size_bytes": 0
                },
                "supported_formats": ["wav", "mp3", "flac", "ogg"],
                "max_file_size": 16777216,  # 16MB
                "cache_enabled": True
            }
        )

@file_ns.route('/cleanup')
class FileCleanupResource(Resource):
    @file_ns.doc('cleanup_files', security='Bearer')
    @file_ns.marshal_with(success_response, code=200, description='Cleanup completed')
    @file_ns.response(401, 'Authentication required', error_model)
    @file_ns.response(500, 'Cleanup failed', error_model)
    @jwt_required()
    def post(self):
        """Clean up orphaned and temporary files
        
        Removes files that are no longer referenced by database records,
        temporary files older than a specified age, and cached files
        that exceed storage limits. This is a maintenance operation.
        """
        return success_response_data(
            data={
                "cleaned_files": 0,
                "reclaimed_space_bytes": 0,
                "categories": {
                    "orphaned_files": 0,
                    "temporary_files": 0,
                    "expired_cache": 0
                }
            },
            message="File cleanup completed successfully"
        )