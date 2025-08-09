# Swagger File Upload Configuration Guide

## 🎯 Overview

This guide explains how file uploads are configured in the Voxify API Swagger documentation to enable the "Choose File" button functionality.

## ✅ Current Configuration

### 1. **Parser Configuration**

```python
# Define upload parser for file uploads
upload_parser = voice_ns.parser()
upload_parser.add_argument('file', 
                          location='files', 
                          type='file',          # Key: Use 'file' not FileStorage
                          required=True, 
                          help='Audio file to upload (WAV or MP3, max 16MB)')
upload_parser.add_argument('name', 
                          location='form', 
                          type=str, 
                          required=True, 
                          help='Name for the voice sample')
```

### 2. **Endpoint Configuration**

```python
@voice_ns.route('/samples')
class VoiceSamplesResource(Resource):
    @voice_ns.doc('upload_voice_sample', security='Bearer')
    @voice_ns.expect(upload_parser, validate=False)  # Important: disable validation
    @voice_ns.marshal_with(success_response, code=201)
    @jwt_required()
    def post(self):
        """Upload and process a voice sample"""
        from .samples import upload_voice_sample
        return upload_voice_sample()
```

## 🔑 Key Configuration Points

### **1. Parameter Type**
- ✅ **Correct**: `type='file'`
- ❌ **Incorrect**: `type=FileStorage` or `type='string'`

### **2. Parameter Location**
- ✅ **Correct**: `location='files'` (for file uploads)
- ✅ **Correct**: `location='form'` (for text parameters)

### **3. Validation**
- ✅ **Recommended**: `validate=False` for file upload endpoints
- This prevents validation errors with multipart form data

### **4. Content Type**
- Flask-RESTX automatically sets `consumes: ['multipart/form-data']`
- No manual configuration needed

## 🎨 Swagger UI Results

With this configuration, Swagger UI will show:

### **File Parameter**
- 📁 **"Choose File" button** for selecting audio files
- File type validation (WAV, MP3)
- Visual file selection interface

### **Form Parameters** 
- 📝 **Text input field** for the sample name
- Parameter validation and help text
- Required field indicators

## 🧪 Testing

### **1. Verify Configuration**
```bash
cd backend
python test_file_upload_swagger.py
```

### **2. Test in Swagger UI**
1. Open `http://localhost:8000/docs/`
2. Authenticate with Bearer token
3. Find `POST /voice/samples` endpoint
4. Click "Try it out"
5. Verify "Choose File" button appears
6. Test file upload functionality

### **3. Test via API**
```bash
python demo_file_upload.py
```

## 📋 Complete Example

### **Full Implementation**
```python
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required

# Create namespace
voice_ns = Namespace('Voice Management', description='Voice sample management')

# Define file upload parser
upload_parser = voice_ns.parser()
upload_parser.add_argument('file', 
                          location='files', 
                          type='file', 
                          required=True, 
                          help='Audio file (WAV/MP3, max 16MB)')
upload_parser.add_argument('name', 
                          location='form', 
                          type=str, 
                          required=True, 
                          help='Sample name')

# Define response models
success_response = voice_ns.model('SuccessResponse', {
    'success': fields.Boolean(required=True),
    'data': fields.Raw(description='Response data')
})

@voice_ns.route('/samples')
class VoiceSamplesResource(Resource):
    @voice_ns.doc('upload_voice_sample', security='Bearer')
    @voice_ns.expect(upload_parser, validate=False)
    @voice_ns.marshal_with(success_response, code=201)
    @voice_ns.response(400, 'Invalid file or parameters')
    @voice_ns.response(401, 'Authentication required')
    @jwt_required()
    def post(self):
        """Upload and process a voice sample"""
        # Implementation connects to existing upload logic
        from .samples import upload_voice_sample
        return upload_voice_sample()
```

## 🚨 Common Issues & Solutions

### **Issue 1: No "Choose File" Button**
**Problem**: Parameter shows as text input instead of file selector
**Solution**: 
- Ensure `type='file'` (not `FileStorage` or `'string'`)
- Verify `location='files'`

### **Issue 2: Validation Errors**
**Problem**: "Validation failed" errors on file upload
**Solution**: 
- Add `validate=False` to `@voice_ns.expect()`
- Files can't be validated like JSON data

### **Issue 3: Content-Type Issues**
**Problem**: Server doesn't accept multipart data
**Solution**: 
- Flask-RESTX automatically handles this
- Ensure parser uses `location='files'` for file parameters

### **Issue 4: File Not Accessible**
**Problem**: `request.files['file']` returns None
**Solution**: 
- Verify parameter name matches (`'file'`)
- Check that actual upload logic uses Flask's `request.files`

## 🎯 Testing Checklist

- [ ] Server running on `http://localhost:8000`
- [ ] Swagger UI accessible at `/docs/`
- [ ] Authentication working (Bearer token)
- [ ] File parameter shows "Choose File" button
- [ ] Text parameter shows input field
- [ ] Can select and upload WAV/MP3 files
- [ ] Upload returns 201 status with sample data
- [ ] Error responses work correctly (401, 400, etc.)

## 📞 Support

If file upload isn't working:

1. **Check Swagger Spec**: `/docs/swagger.json`
   - Look for `multipart/form-data` in consumes
   - Verify parameter types are correct

2. **Check Browser Console**: 
   - Look for JavaScript errors
   - Verify network requests

3. **Test API Directly**:
   ```bash
   curl -X POST http://localhost:8000/voice/samples \
     -H "Authorization: Bearer TOKEN" \
     -F "file=@test.wav" \
     -F "name=Test Sample"
   ```

The file upload functionality is now fully configured and ready for use! 🎉