"""
Job Management API Routes with Full Swagger Documentation
RESTful endpoints that connect to existing functionality with comprehensive OpenAPI documentation
"""

from flask import request, Response
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity

# Create namespace
job_ns = Namespace('Job Management', description='Synthesis job management and monitoring', path='/job')

# Define data models
synthesis_job_model = job_ns.model('SynthesisJob', {
    'id': fields.String(required=True, description='Unique job identifier'),
    'user_id': fields.String(required=True, description='Owner user ID'),
    'voice_model_id': fields.String(required=True, description='Voice model used'),
    'text_content': fields.String(required=True, description='Text to synthesize'),
    'text_language': fields.String(description='Text language code'),
    'text_length': fields.Integer(description='Text length in characters'),
    'word_count': fields.Integer(description='Number of words'),
    'status': fields.String(description='Job status', enum=['pending', 'processing', 'completed', 'failed', 'cancelled']),
    'progress': fields.Float(description='Progress percentage (0.0-1.0)'),
    'output_path': fields.String(description='Output file path'),
    'output_format': fields.String(description='Output audio format'),
    'sample_rate': fields.Integer(description='Audio sample rate'),
    'speed': fields.Float(description='Speech speed multiplier'),
    'pitch': fields.Float(description='Pitch multiplier'),
    'volume': fields.Float(description='Volume multiplier'),
    'duration': fields.Float(description='Generated audio duration'),
    'processing_time_ms': fields.Integer(description='Processing time in milliseconds'),
    'error_message': fields.String(description='Error message if failed'),
    'created_at': fields.String(description='Creation timestamp'),
    'started_at': fields.String(description='Processing start timestamp'),
    'completed_at': fields.String(description='Completion timestamp'),
    'updated_at': fields.String(description='Last update timestamp')
})

job_creation_request = job_ns.model('JobCreationRequest', {
    'text_content': fields.String(required=True, description='Text to synthesize'),
    'voice_model_id': fields.String(required=True, description='Voice model ID to use'),
    'text_language': fields.String(description='Text language code', example='en-US'),
    'output_format': fields.String(description='Output audio format', example='wav'),
    'sample_rate': fields.Integer(description='Audio sample rate', example=22050),
    'speed': fields.Float(description='Speech speed multiplier', example=1.0),
    'pitch': fields.Float(description='Pitch multiplier', example=1.0),
    'volume': fields.Float(description='Volume multiplier', example=1.0),
    'config': fields.Raw(description='Additional synthesis configuration')
})

job_update_request = job_ns.model('JobUpdateRequest', {
    'text_content': fields.String(description='Updated text content'),
    'speed': fields.Float(description='Updated speech speed'),
    'pitch': fields.Float(description='Updated pitch'),
    'volume': fields.Float(description='Updated volume'),
    'output_format': fields.String(description='Updated output format'),
    'sample_rate': fields.Integer(description='Updated sample rate'),
    'config': fields.Raw(description='Updated synthesis configuration')
})

job_status_update = job_ns.model('JobStatusUpdate', {
    'status': fields.String(description='New job status', enum=['pending', 'processing', 'completed', 'failed', 'cancelled']),
    'progress': fields.Float(description='Job progress (0.0-1.0)'),
    'error_message': fields.String(description='Error message if failed'),
    'output_path': fields.String(description='Path to generated audio file'),
    'duration': fields.Float(description='Duration of generated audio'),
    'processing_time_ms': fields.Integer(description='Processing time in milliseconds')
})

error_model = job_ns.model('Error', {
    'success': fields.Boolean(required=True, description='Always false for errors', example=False),
    'error': fields.String(required=True, description='Error message')
})

success_response = job_ns.model('SuccessResponse', {
    'success': fields.Boolean(required=True, description='Always true for successful responses', example=True),
    'timestamp': fields.String(required=True, description='ISO timestamp of the response'),
    'message': fields.String(description='Optional success message'),
    'data': fields.Raw(description='Response data'),
    'meta': fields.Raw(description='Additional metadata')
})

@job_ns.route('')
class JobsResource(Resource):
    @job_ns.doc('list_jobs', security='Bearer')
    @job_ns.param('status', 'Filter by job status', type='string', enum=['pending', 'processing', 'completed', 'failed', 'cancelled'])
    @job_ns.param('user_id', 'Filter by user ID (admin only)', type='string')
    @job_ns.param('voice_model_id', 'Filter by voice model ID', type='string')
    @job_ns.param('text_search', 'Search in text content', type='string')
    @job_ns.param('limit', 'Number of items per page (1-100)', type='integer', default=20)
    @job_ns.param('offset', 'Number of items to skip', type='integer', default=0)
    @job_ns.param('sort_by', 'Sort field', type='string', enum=['created_at', 'updated_at', 'status', 'progress', 'duration'], default='created_at')
    @job_ns.param('sort_order', 'Sort order', type='string', enum=['asc', 'desc'], default='desc')
    @job_ns.param('include_text', 'Include full text content in response', type='boolean', default=False)
    @job_ns.marshal_with(success_response, code=200, description='Jobs retrieved successfully')
    @job_ns.response(400, 'Invalid query parameters', error_model)
    @job_ns.response(401, 'Authentication required', error_model)
    @job_ns.response(500, 'Failed to retrieve jobs', error_model)
    @jwt_required()
    def get(self):
        """List synthesis jobs with filtering, sorting, and pagination"""
        from .routes import list_jobs
        return list_jobs()

    @job_ns.doc('create_job', security='Bearer')
    @job_ns.expect(job_creation_request)
    @job_ns.marshal_with(success_response, code=201, description='Job created successfully')
    @job_ns.response(400, 'Invalid request data', error_model)
    @job_ns.response(404, 'Voice model not found', error_model)
    @job_ns.response(401, 'Authentication required', error_model)
    @job_ns.response(500, 'Job creation failed', error_model)
    @jwt_required()
    def post(self):
        """Create a new synthesis job"""
        from .routes import create_job
        return create_job()

@job_ns.route('/<string:job_id>')
class JobResource(Resource):
    @job_ns.doc('get_job', security='Bearer')
    @job_ns.marshal_with(success_response, code=200, description='Job details retrieved')
    @job_ns.response(404, 'Job not found', error_model)
    @job_ns.response(403, 'Access denied', error_model)
    @job_ns.response(401, 'Authentication required', error_model)
    @job_ns.response(500, 'Failed to retrieve job', error_model)
    @jwt_required()
    def get(self, job_id):
        """Get detailed information about a specific synthesis job"""
        from .routes import get_job
        return get_job(job_id)

    @job_ns.doc('update_job', security='Bearer')
    @job_ns.expect(job_update_request)
    @job_ns.marshal_with(success_response, code=200, description='Job updated successfully')
    @job_ns.response(400, 'Invalid request data or job cannot be updated', error_model)
    @job_ns.response(404, 'Job not found', error_model)
    @job_ns.response(403, 'Access denied', error_model)
    @job_ns.response(401, 'Authentication required', error_model)
    @job_ns.response(500, 'Failed to update job', error_model)
    @jwt_required()
    def put(self, job_id):
        """Update a synthesis job (only allowed for pending jobs)"""
        from .routes import update_job
        return update_job(job_id)

    @job_ns.doc('patch_job', security='Bearer')
    @job_ns.expect(job_status_update)
    @job_ns.marshal_with(success_response, code=200, description='Job updated successfully')
    @job_ns.response(400, 'Invalid request data', error_model)
    @job_ns.response(404, 'Job not found', error_model)
    @job_ns.response(403, 'Access denied', error_model)
    @job_ns.response(401, 'Authentication required', error_model)
    @job_ns.response(500, 'Failed to update job', error_model)
    @jwt_required()
    def patch(self, job_id):
        """Partially update a synthesis job or change its status"""
        from .routes import patch_job
        return patch_job(job_id)

    @job_ns.doc('delete_job', security='Bearer')
    @job_ns.response(204, 'Job deleted successfully')
    @job_ns.response(400, 'Job cannot be deleted', error_model)
    @job_ns.response(404, 'Job not found', error_model)
    @job_ns.response(403, 'Access denied', error_model)
    @job_ns.response(401, 'Authentication required', error_model)
    @job_ns.response(500, 'Failed to delete job', error_model)
    @jwt_required()
    def delete(self, job_id):
        """Delete a synthesis job (only allowed for completed, failed, or cancelled jobs)"""
        from .routes import delete_job
        return delete_job(job_id)

@job_ns.route('/<string:job_id>/cancel')
class JobCancellationResource(Resource):
    @job_ns.doc('cancel_job_legacy', security='Bearer', deprecated=True)
    @job_ns.marshal_with(success_response, code=200, description='Job cancelled successfully')
    @job_ns.response(400, 'Job cannot be cancelled', error_model)
    @job_ns.response(404, 'Job not found', error_model)
    @job_ns.response(403, 'Access denied', error_model)
    @job_ns.response(401, 'Authentication required', error_model)
    @job_ns.response(500, 'Failed to cancel job', error_model)
    @jwt_required()
    def post(self, job_id):
        """Cancel a synthesis job (legacy endpoint - use PATCH instead)
        
        This endpoint is deprecated. Use PATCH /<job_id> with status: "cancelled" instead.
        """
        from .routes import cancel_job_legacy
        return cancel_job_legacy(job_id)

@job_ns.route('/<string:job_id>/progress')
class JobProgressResource(Resource):
    @job_ns.doc('stream_job_progress', security='Bearer')
    @job_ns.produces(['text/event-stream'])
    @job_ns.response(200, 'SSE stream with progress updates')
    @job_ns.response(404, 'Job not found', error_model)
    @job_ns.response(403, 'Access denied', error_model)
    @job_ns.response(401, 'Authentication required', error_model)
    @job_ns.response(500, 'Failed to start progress stream', error_model)
    @jwt_required()
    def get(self, job_id):
        """Stream real-time job progress updates using Server-Sent Events (SSE)
        
        Returns a continuous stream of progress updates for the specified job.
        The stream automatically terminates when the job reaches a terminal state.
        
        Events:
        - progress: Regular progress updates
        - complete: Job finished (success/failure)
        - error: Stream error occurred
        """
        from .routes import stream_job_progress
        return stream_job_progress(job_id)