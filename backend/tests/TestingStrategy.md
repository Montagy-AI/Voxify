# Testing Strategy

## 1. Overview
This project uses comprehensive automated testing to ensure the reliability and correctness of backend APIs and core business logic. All tests are located in the `backend/tests/` directory and are organized by module and test type.

## 2. Test Framework and Tools
- **Framework:** All tests use `pytest` for automation and fixtures
- **API Testing:** Most tests use `requests` and `subprocess` to interact with the running Flask server, often leveraging `curl` commands for realistic end-to-end coverage
- **Test Data:** Each test module creates its own test user and authentication tokens to ensure isolation and repeatability
- **Environment:** Tests are designed to run against a locally running server (default: `127.0.0.1:8000`), with environment variables configurable for host/port
- **Coverage:** Uses `pytest-cov` for code coverage reporting
- **Performance:** Uses `psutil` for system resource monitoring during performance tests

## 3. Test Structure

### 3.1 Authentication (`test_v1_auth`)
- **Files:** `test_curl_auth.py`, `test_register.py`, `test_log_in.py`
- **Coverage:** Registration, login, and token refresh endpoints
- **Features:** Valid/invalid registration, login with wrong credentials, token refresh with valid/invalid tokens
- **Method:** Uses `curl` to simulate real HTTP requests

### 3.2 File Service (`test_v1_file`)
- **Files:** `test_curl_file.py`, `test_file_logic.py`
- **Coverage:** File download and deletion endpoints for synthesis results
- **Scenarios:** Without authentication, invalid job IDs, non-existent jobs, valid jobs, malformed IDs, wrong HTTP methods, error responses
- **Features:** Proper permission checks and error handling

### 3.3 Job Service (`test_v1_job`)
- **Files:** `test_job_service.py`, `test_job_unit.py`
- **Coverage:** Job creation, listing, updating, patching, and deletion
- **Scenarios:** Missing/invalid parameters, unauthorized access, duplicate jobs, job progress streaming
- **Features:** Validates correct status codes and error messages for all edge cases

### 3.4 Voice Service (`test_v1_voice`)
- **Files:** 8 comprehensive test files with 192 test cases
- **Coverage:** Voice sample upload, listing, details, deletion, voice clone creation, listing, selection, synthesis
- **Test Types:**
  - **Unit Tests:** `test_voice_unit.py` (56 test cases) - Core functionality validation
  - **Service Tests:** `test_voice_service.py` (25+ API tests) - Basic API endpoint testing
  - **Integration Tests:** `test_voice_integration.py` (5 workflow tests) - End-to-end scenarios
  - **Performance Tests:** `test_voice_performance.py` (10+ tests) - Scalability validation
  - **Extended Tests:** `test_voice_service_extended.py` (15+ advanced scenarios)
  - **Error Handling:** `test_voice_error_handling_unit.py` (40+ edge cases)
  - **Embedding Tests:** `test_voice_embeddings_unit.py` (25+ embedding operations)
  - **F5-TTS Tests:** `test_f5_tts_service_unit.py` (30+ TTS service tests)

### 3.5 Modal Integration (`test_v1_modal`)
- **Files:** `test_modal.py`
- **Coverage:** Modal F5-TTS voice cloning endpoint testing
- **Features:** Reads local audio files, sends synthesis requests, saves generated audio
- **Handling:** Response parsing, error reporting, file output

## 4. Test Coverage Analysis

### Current Coverage Status (Latest Run - December 2024)
**Overall Project Coverage: 76%**

| Module | Statements | Covered | Missing | Coverage % |
|--------|------------|---------|---------|------------|
| `api.v1.voice.__init__.py` | 10 | 8 | 2 | **80%** |
| `api.v1.voice.clones.py` | 177 | 26 | 151 | **15%** |
| `api.v1.voice.embeddings.py` | 38 | 36 | 2 | **95%** |
| `api.v1.voice.f5_tts_service.py` | 246 | 135 | 111 | **55%** |
| `api.v1.voice.samples.py` | 103 | 29 | 74 | **28%** |
| `database.models.py` | 317 | 245 | 72 | **77%** |
| `database.vector_config.py` | 74 | 22 | 52 | **30%** |
| `api.v1.auth.routes.py` | 148 | 49 | 99 | **33%** |
| `api.v1.file.routes.py` | 134 | 45 | 89 | **34%** |
| `api.v1.job.routes.py` | 366 | 96 | 270 | **26%** |

### Coverage Breakdown by Module

#### 1. **Voice Module Initialization** (`__init__.py`) - 80% Coverage
- ✅ **Well Covered:** Blueprint creation and route registration
- ❌ **Missing:** Error handling for import failures (lines 21, 42)

#### 2. **Voice Embeddings** (`embeddings.py`) - 95% Coverage
- ✅ **Excellent Coverage:** Core embedding generation and comparison functions
- ❌ **Missing:** Edge cases in error handling (lines 74-75)

#### 3. **F5-TTS Service** (`f5_tts_service.py`) - 55% Coverage
- ✅ **Moderately Covered:** Service initialization and basic operations
- ❌ **Missing:** Remote API operations, error handling paths, advanced configurations

#### 4. **Voice Samples** (`samples.py`) - 28% Coverage
- ✅ **Basic Coverage:** File upload and basic validation
- ❌ **Missing:** Advanced processing, error handling, metadata extraction

#### 5. **Voice Clones** (`clones.py`) - 15% Coverage
- ✅ **Minimal Coverage:** Basic route registration
- ❌ **Missing:** Most clone operations, validation, error handling

#### 6. **Database Models** (`models.py`) - 77% Coverage
- ✅ **Good Coverage:** Core database operations and models
- ❌ **Missing:** Some edge cases and error handling paths

#### 7. **Vector Configuration** (`vector_config.py`) - 30% Coverage
- ✅ **Basic Coverage:** Configuration setup
- ❌ **Missing:** Most advanced configuration scenarios

#### 8. **Authentication Routes** (`auth.routes.py`) - 33% Coverage
- ✅ **Basic Coverage:** Core authentication endpoints
- ❌ **Missing:** Advanced error handling and edge cases

#### 9. **File Routes** (`file.routes.py`) - 34% Coverage
- ✅ **Basic Coverage:** File download and deletion endpoints
- ❌ **Missing:** Advanced file operations and error handling

#### 10. **Job Routes** (`job.routes.py`) - 26% Coverage
- ✅ **Basic Coverage:** Job management endpoints
- ❌ **Missing:** Advanced job operations and workflow handling

## 5. Test Practices

### 5.1 Test Organization
- **Fixtures:** Common setup (server URL, test user, tokens) handled via `pytest` fixtures for reusability
- **Server Availability:** Each test class checks if server is running before executing tests, skipping if unavailable
- **Curl Availability:** Tests check for `curl` installation and skip if not present
- **Isolation:** Test users and jobs created per test class to avoid cross-test interference
- **Error Handling:** All endpoints tested for both success and failure scenarios

### 5.2 Test Categories
- **Unit Tests:** Individual function and method testing with mocking
- **Service Tests:** API endpoint and workflow testing using real HTTP requests
- **Integration Tests:** End-to-end scenario testing with complete workflows
- **Performance Tests:** Scalability and performance validation under load
- **Error Handling Tests:** Edge cases and error scenario validation
- **Security Tests:** Input validation and security vulnerability testing

### 5.3 Advanced Testing Features
- **Concurrent Operations:** Multiple simultaneous requests testing
- **Error Recovery:** System recovery from failures testing
- **Performance Monitoring:** Memory, CPU, and response time tracking
- **Security Validation:** Path traversal, SQL injection, XSS prevention
- **Scalability Testing:** Load testing and performance under stress

## 6. Running the Tests

### 6.1 Prerequisites
1. Enter the backend directory and start the backend server locally:
   ```bash
   cd backend
   python start.py
   ```
   The default address is `127.0.0.1:8000`.

2. Install test dependencies:
   ```bash
   pip install pytest pytest-cov psutil
   ```

3. Ensure `curl` is installed and available in your system path.

### 6.2 Running All Tests
```bash
python -m pytest tests/ -v
```

### 6.3 Running Specific Test Categories
```bash
# All voice tests
python -m pytest tests/test_v1_voice/ -v

# Unit tests only
python -m pytest tests/test_v1_voice/test_voice_unit.py -v

# Service tests only
python -m pytest tests/test_v1_voice/test_voice_service.py -v

# Integration tests only
python -m pytest tests/test_v1_voice/test_voice_integration.py -v

# Performance tests only
python -m pytest tests/test_v1_voice/test_voice_performance.py -v
```

### 6.4 Running Specific Test Methods
```bash
python -m pytest tests/test_v1_voice/test_voice_unit.py::TestVoiceSampleValidation::test_allowed_file_valid_extensions -v
```

### 6.5 Generating Coverage Reports
```bash
# Generate HTML coverage report for voice module
python -m pytest tests/test_v1_voice/ --cov=api.v1.voice --cov-report=html --cov-report=term-missing

# Generate coverage for all modules
python -m pytest tests/ --cov=api --cov=database --cov-report=html --cov-report=term-missing
```

## 7. Test Statistics

### 7.1 Voice Service Test Statistics (Latest Run)
- **Total Test Cases:** 288
- **Test Pass Rate:** 100%
- **Code Coverage:** 76% (overall project)
- **Test Categories:** 20+ main test classes
- **Execution Time:** 117.96s (1 minute 57 seconds)

### 7.2 Detailed Test Count by Category
| Test Category | Test Count | Coverage Focus |
|---------------|------------|----------------|
| Unit Tests | 56 | Core functionality validation |
| Embedding Tests | 25 | Voice embedding operations |
| F5-TTS Service Tests | 30 | TTS service integration |
| Error Handling Tests | 40 | Edge cases and error scenarios |
| Service API Tests | 25 | API endpoint validation |
| Extended Service Tests | 15 | Advanced scenarios |
| Integration Tests | 5 | End-to-end workflows |
| Performance Tests | 10 | Scalability and performance |
| Authentication Tests | 8 | User authentication |
| File Service Tests | 16 | File operations |
| Job Service Tests | 18 | Job management |
| Modal Integration Tests | 1 | External service integration |

### 7.3 Test File Coverage Statistics
| Test File | Lines | Missing | Coverage % |
|-----------|-------|---------|------------|
| `test_voice_unit.py` | 696 | 17 | **98%** |
| `test_voice_service.py` | 452 | 13 | **97%** |
| `test_voice_service_extended.py` | 210 | 6 | **97%** |
| `test_voice_performance.py` | 253 | 7 | **97%** |
| `test_voice_integration.py` | 217 | 11 | **95%** |
| `test_f5_tts_service_unit.py` | 243 | 1 | **99%** |
| `test_voice_embeddings_unit.py` | 158 | 1 | **99%** |
| `test_voice_error_handling_unit.py` | 174 | 1 | **99%** |
| `test_curl_auth.py` | 110 | 12 | **89%** |
| `test_file_logic.py` | 183 | 1 | **99%** |
| `test_job_service.py` | 234 | 14 | **94%** |
| `test_job_unit.py` | 170 | 1 | **99%** |

## 8. Coverage Improvement Plan

### 8.1 High Priority (Critical Missing Coverage)
1. **Voice Clones Module** (15% coverage)
   - Add tests for clone creation workflows
   - Test clone validation and error handling
   - Cover clone selection and management

2. **Voice Samples Module** (28% coverage)
   - Add tests for advanced file processing
   - Test metadata extraction scenarios
   - Cover error handling for corrupted files

3. **F5-TTS Service** (55% coverage)
   - Add tests for remote API operations
   - Test advanced configuration scenarios
   - Cover error recovery mechanisms

4. **Vector Configuration** (30% coverage)
   - Add tests for advanced configuration scenarios
   - Test configuration validation
   - Cover error handling for invalid configurations

5. **Authentication Routes** (33% coverage)
   - Add tests for advanced authentication scenarios
   - Test token refresh mechanisms
   - Cover security validation

6. **File Routes** (34% coverage)
   - Add tests for advanced file operations
   - Test file permission handling
   - Cover error scenarios

7. **Job Routes** (26% coverage)
   - Add tests for job workflow management
   - Test job status transitions
   - Cover concurrent job handling

### 8.2 Medium Priority
1. **Error Handling Paths**
   - Add tests for network timeout scenarios
   - Test database connection failures
   - Cover file system permission errors

2. **Advanced Features**
   - Test concurrent user scenarios
   - Add tests for rate limiting
   - Cover security validation edge cases

### 8.3 Low Priority
1. **Edge Cases**
   - Test with very large files
   - Test with corrupted audio files
   - Test with unusual file formats

## 9. Continuous Integration

### 9.1 GitHub Actions
Tests are automatically run on:
- Pull requests
- Main branch pushes
- Scheduled runs

### 9.2 Test Reports
- Coverage reports generated automatically
- Performance benchmarks tracked
- Test results published to GitHub

## 10. Performance Benchmarks

### 10.1 Regular Performance Benchmarks
- Upload time: < 30 seconds
- Clone creation time: < 60 seconds
- List operation time: < 5 seconds

### 10.2 Performance Monitoring
- Memory usage tracking
- CPU utilization monitoring
- Response time consistency validation
- Concurrent user simulation

### 10.3 Latest Performance Metrics
- **Test Execution Time:** 117.96s for 288 tests
- **Average Test Time:** 0.41s per test
- **Memory Usage:** Monitored during performance tests
- **CPU Usage:** Tracked for system resource validation

## 11. Troubleshooting

### 11.1 Common Issues
1. **Server not running:** Ensure Flask server is started before running integration tests
2. **Database connection:** Verify database is properly initialized
3. **File permissions:** Ensure test audio files are readable
4. **Network issues:** Check connectivity for remote API tests

### 11.2 Debug Mode
```bash
# Run tests with verbose output
python -m pytest tests/test_v1_voice/ -v -s

# Run specific test with debug output
python -m pytest tests/test_v1_voice/test_voice_integration.py::TestVoiceServiceIntegration::test_complete_voice_workflow -v -s
```

### 11.3 Known Warnings
- **Deprecation Warnings:** Some dependencies show deprecation warnings (resemblyzer, audioread)
- **Runtime Warnings:** Zero embedding comparison warnings in embeddings.py
- **Pytest Warnings:** Some performance tests return values instead of using assertions

## 12. Maintenance

### 12.1 Adding New Tests
1. Follow the existing test structure
2. Use appropriate test categories (unit/service/integration/performance)
3. Include comprehensive error handling
4. Add proper documentation
5. Update this README with new test information

### 12.2 Test Guidelines
- Use descriptive test names
- Include proper assertions
- Mock external dependencies
- Handle cleanup properly
- Document complex test scenarios
- Follow PEP 8 style guidelines

### 12.3 Coverage Tracking
- Regular coverage reports to identify gaps
- Performance monitoring of system metrics
- Regular updates to keep tests current with code changes

---

**Last Updated:** December 2024
**Test Framework:** pytest
**Coverage Target:** 80%+ (currently 76% overall)
**Total Test Files:** 15+
**Total Test Cases:** 288
**Latest Test Run:** 288 passed, 10 warnings in 117.96s 