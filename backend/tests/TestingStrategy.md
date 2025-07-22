# Testing Strategy

## 1. Overview
This project uses automated testing to ensure the reliability and correctness of backend APIs and core business logic. All tests are located in the `backend/tests/` directory and are organized by module.

## 2. Test Framework and Tools
- **Framework:** All tests use `pytest` for automation and fixtures.
- **API Testing:** Most tests use `requests` and `subprocess` to interact with the running Flask server, often leveraging `curl` commands for realistic end-to-end coverage.
- **Test Data:** Each test module creates its own test user and authentication tokens to ensure isolation and repeatability.
- **Environment:** Tests are designed to run against a locally running server (default: `127.0.0.1:8000`), with environment variables configurable for host/port.

## 3. Test Structure

### 3.1 Authentication (`test_v1_auth`)
- Tests registration, login, and token refresh endpoints.
- Covers valid and invalid registration, login with wrong credentials, and token refresh with valid/invalid tokens.
- Uses `curl` to simulate real HTTP requests.

### 3.2 File Service (`test_v1_file`)
- Tests file download and deletion endpoints for synthesis results.
- Covers scenarios: without authentication, invalid job IDs, non-existent jobs, valid jobs, malformed IDs, wrong HTTP methods, and error responses.
- Ensures proper permission checks and error handling.

### 3.3 Job Service (`test_v1_job`)
- Tests job creation, listing, updating, patching, and deletion.
- Covers missing/invalid parameters, unauthorized access, duplicate jobs, and job progress streaming.
- Validates correct status codes and error messages for all edge cases.

### 3.4 Voice Service (`test_v1_voice`)
- Tests voice sample upload, listing, details, and deletion.
- Tests voice clone creation, listing, selection, synthesis, and error handling.
- Includes tests for missing/invalid fields, pagination, unauthorized/invalid token access, and not-found errors.

### 3.5 Modal Integration (`test_v1_modal`)
- Contains a script for testing the Modal F5-TTS voice cloning endpoint.
- Reads a local audio file, sends a synthesis request, and saves the generated audio.
- Handles response parsing, error reporting, and file output.

## 4. Test Practices
- **Fixtures:** Common setup (e.g., server URL, test user, tokens) is handled via `pytest` fixtures for reusability.
- **Server Availability:** Each test class checks if the server is running before executing tests, skipping if unavailable.
- **Curl Availability:** Tests check for `curl` installation and skip if not present.
- **Isolation:** Test users and jobs are created per test class to avoid cross-test interference.
- **Error Handling:** All endpoints are tested for both success and failure scenarios, including permission errors, invalid input, and server errors.

## 5. Running the Tests
1. Enter the backend directory and start the backend server locally:
   ```bash
   cd backend
   python start.py
   ```
   The default address is `127.0.0.1:8000`.
2. Ensure `curl` is installed and available in your system path.
3. In another terminal, run all tests with:
   ```bash
   python -m pytest tests/ -v
   ```
4. To run a specific module:
   ```bash
   pytest backend/tests/test_v1_auth/test_curl_auth.py
   ```

## 6. Continuous Integration
- It is recommended to integrate these tests into a CI pipeline (e.g., GitHub Actions) to ensure all code changes are validated before merging.
- Tests should be run on every pull request and commit to the main branch.

## 7. Coverage and Maintenance
- Aim for high coverage of all API endpoints and business logic.
- For every bug fixed, add a regression test to prevent recurrence.
- Update and expand tests as new features and endpoints are added.

--- 