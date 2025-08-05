# Voxify API Documentation with Swagger

This document explains how to use and access the Swagger/OpenAPI documentation for the Voxify API.

## Access Swagger UI

Once the API server is running, you can access the interactive Swagger documentation at:

- **Local Development**: `http://localhost:8000/docs/`
- **Production**: `https://your-domain.com/docs/`

## Features

### Interactive Documentation
- Browse all API endpoints organized by category
- View request/response schemas
- Test endpoints directly from the browser
- Authentication support with JWT tokens

### API Categories

1. **Authentication** (`/api/v1/auth`)
   - User registration and login
   - Token management (access/refresh)
   - Profile management
   - Password reset functionality

2. **Voice Management** (`/api/v1/voice`)
   - Voice sample upload and processing
   - Voice clone creation and management
   - Speech synthesis with custom voices
   - Voice model information

3. **Job Management** (`/api/v1/job`)
   - Synthesis job creation and monitoring
   - Real-time progress tracking via SSE
   - Job status management
   - Batch operations

4. **File Management** (`/api/v1/file`)
   - Audio file downloads
   - File metadata and information
   - Storage management
   - Cleanup operations

## Authentication

### Using JWT Tokens in Swagger UI

1. **Login** via the `/auth/login` endpoint
2. **Copy** the returned `access_token`
3. **Click** the "Authorize" button in Swagger UI
4. **Enter**: `Bearer <your-access-token>`
5. **Click** "Authorize"

Now all subsequent requests will include your authentication token.

### Token Format
```
Authorization: Bearer <jwt-access-token>
```

## Data Models

All API endpoints use standardized request/response formats:

### Success Response
```json
{
  "success": true,
  "timestamp": "2024-01-01T00:00:00Z",
  "message": "Operation completed successfully",
  "data": { ... }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "message": "Human-readable error message",
    "code": "MACHINE_READABLE_ERROR_CODE",
    "timestamp": "2024-01-01T00:00:00Z",
    "details": { ... }
  }
}
```

## API Versioning

- **Current Version**: v1
- **Base URL**: `/api/v1`
- **Swagger Docs**: `/docs/`

## Development Notes

### Dual Route System
The API supports both:
- **Swagger Routes**: New Flask-RESTX based routes with documentation
- **Legacy Routes**: Original Flask Blueprint routes for backward compatibility

### Adding New Endpoints

1. **Create Swagger Route**: Add to appropriate `swagger_routes.py`
2. **Define Models**: Use Flask-RESTX field definitions
3. **Add Documentation**: Use decorators for comprehensive docs
4. **Test**: Verify in Swagger UI

### Example Endpoint Documentation
```python
@api.route('/example')
class ExampleResource(Resource):
    @api.doc('example_endpoint', security='Bearer')
    @api.expect(request_model)
    @api.marshal_with(response_model, code=200)
    @api.response(400, 'Bad Request', error_model)
    @jwt_required()
    def post(self):
        \"\"\"Example endpoint with full documentation\"\"\"
        return {"message": "Success"}
```

## Configuration

### Environment Variables
- `FLASK_ENV`: Set to `development` for detailed error messages
- `JWT_SECRET_KEY`: Secret key for JWT token signing
- `DATABASE_URL`: Database connection string

### CORS Configuration
The API supports CORS for web frontend integration with configured origins.

## Testing with Swagger UI

1. **Explore Endpoints**: Browse available operations
2. **Review Schemas**: Understand request/response formats
3. **Test Authentication**: Login and use tokens
4. **Try Operations**: Execute API calls directly
5. **Check Responses**: Verify expected behavior

## Production Considerations

### Security
- All endpoints require HTTPS in production
- JWT tokens have configurable expiration
- Rate limiting is implemented
- Input validation on all endpoints

### Performance
- Pagination for list endpoints
- Caching for frequently accessed data
- Optimized database queries
- File streaming for large downloads

### Monitoring
- Structured logging with request IDs
- Error tracking and alerting
- Performance metrics collection
- Health check endpoints

## OpenAPI Specification

The complete OpenAPI 3.0 specification is available at:
- **JSON Format**: `/docs/swagger.json`
- **YAML Format**: `/docs/swagger.yml`

This specification can be imported into other tools like Postman, Insomnia, or used for client code generation.

## Support

For API support and questions:
- **Email**: support@voxify.app
- **Documentation**: Check Swagger UI for latest information
- **Issues**: Report bugs via project repository