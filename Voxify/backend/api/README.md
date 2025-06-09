# Voxify API Documentation

This document provides information about the Voxify API endpoints, request/response formats, and authentication.

## Authentication

Voxify uses JWT (JSON Web Tokens) for authentication. To access protected endpoints, you need to:

1. Register a user account or login with existing credentials
2. Include the JWT token in the Authorization header of your requests:
   ```
   Authorization: Bearer <your_jwt_token>
   ```

## API Endpoints

### Authentication

#### Register a new user

```
POST /api/v1/auth/register
```

Request body:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

Response (201 Created):
```json
{
  "message": "User registered successfully",
  "user": {
    "id": "uuid-string",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "subscription_type": "free",
    "quota_voice_samples": 5,
    "quota_syntheses_daily": 100,
    "storage_used_bytes": 0,
    "is_active": true,
    "email_verified": false,
    "created_at": "2023-06-01T12:00:00Z",
    "last_login_at": null
  }
}
```

#### Login

```
POST /api/v1/auth/login
```

Request body:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

Response (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "uuid-string",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "subscription_type": "free",
    "quota_voice_samples": 5,
    "quota_syntheses_daily": 100,
    "storage_used_bytes": 0,
    "is_active": true,
    "email_verified": false,
    "created_at": "2023-06-01T12:00:00Z",
    "last_login_at": "2023-06-01T14:30:00Z"
  }
}
```

### Admin

#### List Users

```
GET /api/v1/admin/users
```

Query parameters:
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20, max: 100)
- `sort_by`: Field to sort by (options: created_at, email, last_login_at, subscription_type)
- `order`: Sort order (asc or desc, default: desc)
- `subscription_type`: Filter by subscription type (free, pro, enterprise)
- `is_active`: Filter by active status (true, false)

Response (200 OK):
```json
{
  "users": [
    {
      "id": "uuid-string-1",
      "email": "user1@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "full_name": "John Doe",
      "subscription_type": "free",
      "quota_voice_samples": 5,
      "quota_syntheses_daily": 100,
      "storage_used_bytes": 0,
      "is_active": true,
      "email_verified": false,
      "created_at": "2023-06-01T12:00:00Z",
      "last_login_at": "2023-06-01T14:30:00Z"
    },
    {
      "id": "uuid-string-2",
      "email": "user2@example.com",
      "first_name": "Jane",
      "last_name": "Smith",
      "full_name": "Jane Smith",
      "subscription_type": "pro",
      "quota_voice_samples": 20,
      "quota_syntheses_daily": 500,
      "storage_used_bytes": 1024,
      "is_active": true,
      "email_verified": true,
      "created_at": "2023-05-15T10:00:00Z",
      "last_login_at": "2023-06-02T09:15:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 2,
    "pages": 1
  }
}
```

## Error Responses

All API endpoints return appropriate HTTP status codes:

- `200 OK`: Request succeeded
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required or failed
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource already exists
- `500 Internal Server Error`: Server error

Error response format:
```json
{
  "error": "Error message describing the issue"
}
```

## Database Used

The API endpoints in this implementation use the SQLite database defined in the `database` directory:

- `/api/v1/auth/register`: Uses the SQLite database to store user information
- `/api/v1/auth/login`: Uses the SQLite database to verify user credentials
- `/api/v1/admin/users`: Uses the SQLite database to retrieve user information