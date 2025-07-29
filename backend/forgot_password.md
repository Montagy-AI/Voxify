# Forgot Password Configuration

## Overview

The forgot password functionality requires SMTP email service configuration to send password reset emails to users. This document explains the required environment variables and how to configure them.

## Required Environment Variables

The following environment variables must be configured in your `.env` file for the forgot password feature to work:

### SMTP Configuration

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=voxifynoreply@gmail.com
SMTP_PASSWORD=uhxxrskdlliidcyg
SMTP_USE_TLS=true
SMTP_FROM_EMAIL=voxifynoreply@gmail.com
SMTP_FROM_NAME=Voxify
FRONTEND_URL=http://localhost:3000
DATABASE_URL=sqlite:///data/voxify.db
VECTOR_DB_PATH=data/chroma_db
JWT_SECRET_KEY=Majick
SECRET_KEY=Majick
```


## Setup Instructions

### 1. Create .env File

Create a `.env` file in your project root directory:

```bash
# Create .env file
touch .env
```

### 2. Add Configuration

Add your SMTP configuration to the `.env` file using one of the examples above.

### 3. Verify Configuration

You can test your SMTP configuration by running the email service test:

```python
from backend.api.utils.email_service import get_email_service

email_service = get_email_service()
success, message = email_service.test_connection()
print(f"Connection test: {'Success' if success else 'Failed'}")
print(f"Message: {message}")
```

## Security Considerations

### Development Environment
- Use personal email accounts for testing
- Store credentials in `.env` file (excluded from git)
- Never commit sensitive credentials to version control

### Production Environment
- Use dedicated email service (SendGrid, AWS SES, etc.)
- Set environment variables directly on the server
- Use strong, unique passwords
- Regularly rotate credentials
- Consider using OAuth2 instead of passwords where supported

## Docker Configuration

When using Docker, you can either:

### Option 1: Use .env file with docker-compose

```yaml
# docker-compose.yml
api:
  environment:
    - SMTP_HOST=${SMTP_HOST}
    - SMTP_PORT=${SMTP_PORT}
    - SMTP_USERNAME=${SMTP_USERNAME}
    - SMTP_PASSWORD=${SMTP_PASSWORD}
    - SMTP_USE_TLS=${SMTP_USE_TLS}
    - SMTP_FROM_EMAIL=${SMTP_FROM_EMAIL}
    - SMTP_FROM_NAME=${SMTP_FROM_NAME}
    - FRONTEND_URL=${FRONTEND_URL}
```

### Option 2: Set environment variables directly

```yaml
# docker-compose.yml
api:
  environment:
    - SMTP_HOST=smtp.gmail.com
    - SMTP_PORT=587
    # ... other variables
```

**Note**: Option 1 is recommended for security reasons.

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify username and password
   - For Gmail, ensure you're using an App Password, not your regular password
   - Check if 2FA is enabled and properly configured

2. **Connection Timeout**
   - Verify SMTP host and port
   - Check firewall settings
   - Ensure TLS settings are correct

3. **Emails Not Received**
   - Check spam/junk folders
   - Verify sender email is not blacklisted
   - Test with different recipient emails

4. **Invalid Reset Links**
   - Verify `FRONTEND_URL` is correct
   - Ensure frontend is running on the specified URL
   - Check for trailing slashes in URL

### Testing Email Functionality

Run the forgot password test to verify everything works:

```bash
# Run specific forgot password tests
python -m pytest backend/tests/test_v1_auth/password_reset_tests/ -v
```

## Environment Variables Checklist

Before deploying, ensure you have configured:

- [ ] `SMTP_HOST` - Your SMTP server
- [ ] `SMTP_USERNAME` - Your email username
- [ ] `SMTP_PASSWORD` - Your email password/app password
- [ ] `SMTP_FROM_EMAIL` - Sender email address
- [ ] `FRONTEND_URL` - Your frontend application URL
- [ ] Test email sending functionality
- [ ] Verify password reset flow end-to-end

## Support

If you encounter issues with email configuration:

1. Check the application logs for SMTP errors
2. Test SMTP connection using the test utility
3. Verify all environment variables are set correctly
4. Consult your email provider's SMTP documentation 