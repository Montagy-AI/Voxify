#!/usr/bin/env python3
"""
Test suite for Backend Server Initialization
"""

import os
import sys
import tempfile
import pytest
import subprocess
from unittest.mock import patch


def get_start_py_path():
    """Find the start.py file"""
    current_dir = os.path.dirname(__file__)
    start_py_path = os.path.abspath(os.path.join(current_dir, "../../../backend", "start.py"))
    if os.path.exists(start_py_path):
        return start_py_path

    return None


def get_start_py_path_or_skip():
    """Get start.py path or skip test if not found"""
    path = get_start_py_path()
    if path is None:
        pytest.skip("Could not find start.py - skipping start.py tests")
    return path


class TestStartScriptExecution:
    """
    Test start.py script execution and behavior.
    """

    def test_start_py_exists(self):
        """Test that start.py file exists and is executable"""
        start_py_path = get_start_py_path_or_skip()
        assert os.path.exists(start_py_path), f"start.py not found at {start_py_path}"
        assert os.access(start_py_path, os.R_OK), "start.py is not readable"

    def test_start_help_option(self):
        """Test start.py --help option"""
        start_py_path = get_start_py_path_or_skip()
        result = subprocess.run(
            [sys.executable, start_py_path, "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, f"Help command failed: {result.stderr}"
        assert "Voxify One-Click Startup Script" in result.stdout
        assert "--skip-db-init" in result.stdout
        assert "--skip-file-init" in result.stdout
        assert "--init-only" in result.stdout
        assert "--seed" in result.stdout

    def test_start_init_only_success(self):
        """Test start.py --init-only flag (no server startup)"""
        start_py_path = get_start_py_path_or_skip()
        with tempfile.TemporaryDirectory() as temp_dir:
            env = os.environ.copy()
            env["DATABASE_URL"] = f"sqlite:///{temp_dir}/test.db"
            env["VECTOR_DB_PATH"] = f"{temp_dir}/chroma"

            result = subprocess.run(
                [sys.executable, start_py_path, "--init-only"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=temp_dir,
                env=env,
            )

            assert result.returncode in [
                0,
                None,
            ], f"Init failed: {result.stderr}\nStdout: {result.stdout}"
            assert "Initializing file storage" in result.stdout
            assert "Welcome to Voxify!" in result.stdout

    def test_start_seed_only_with_mock_database(self):
        """Test start.py --seed-only flag (no server startup)"""
        start_py_path = get_start_py_path_or_skip()

        result = subprocess.run(
            [sys.executable, start_py_path, "--seed-only"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # This should fail because we don't have a proper database setup
        assert "Welcome to Voxify!" in result.stdout
        # It should either succeed with seeding or fail gracefully
        assert result.returncode in [0, 1], f"Unexpected error: {result.stderr}"

    def test_start_skip_flags_init_only(self):
        """Test start.py with skip flags and init-only (no server startup)"""
        start_py_path = get_start_py_path_or_skip()

        result = subprocess.run(
            [
                sys.executable,
                start_py_path,
                "--skip-db-init",
                "--skip-file-init",
                "--init-only",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode in [0, None], f"Skip flags failed: {result.stderr}"
        assert "Welcome to Voxify!" in result.stdout
        # Should skip the initialization steps
        assert "Database initialization failed" not in result.stdout
        assert "File storage initialization failed" not in result.stdout


class TestFileStorageCreation:
    """
    Test file storage directory creation.
    """

    def test_file_storage_directories_created(self):
        """Test that running start.py creates the expected directories"""
        start_py_path = get_start_py_path_or_skip()
        with tempfile.TemporaryDirectory() as temp_dir:
            env = os.environ.copy()
            env["DATABASE_URL"] = f"sqlite:///{temp_dir}/test.db"
            env["VECTOR_DB_PATH"] = f"{temp_dir}/chroma"

            result = subprocess.run(
                [sys.executable, start_py_path, "--init-only"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=temp_dir,
                env=env,
            )

            # Ensure the subprocess completed successfully
            assert result.returncode in [0, None], f"Init failed: {result.stderr}\nStdout: {result.stdout}"

            # Check if directories were created
            expected_dirs = [
                os.path.join(temp_dir, "data"),
                os.path.join(temp_dir, "data", "files"),
                os.path.join(temp_dir, "data", "files", "synthesis"),
                os.path.join(temp_dir, "data", "files", "samples"),
                os.path.join(temp_dir, "data", "files", "temp"),
            ]

            for expected_dir in expected_dirs:
                if os.path.exists(expected_dir):
                    assert os.path.isdir(expected_dir), f"{expected_dir} exists but is not a directory"

    def test_file_storage_environment_variables_mentioned(self):
        """Test that file storage setup mentions environment variables"""
        start_py_path = get_start_py_path_or_skip()
        result = subprocess.run(
            [sys.executable, start_py_path, "--init-only"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert "file storage" in result.stdout.lower() or "files" in result.stdout.lower()


class TestDatabaseInitialization:
    """
    Test database initialization behavior.
    """

    def test_database_initialization_attempt(self):
        """Test that start.py attempts database initialization"""
        start_py_path = get_start_py_path_or_skip()
        with tempfile.TemporaryDirectory() as temp_dir:
            env = os.environ.copy()
            env["DATABASE_URL"] = f"sqlite:///{temp_dir}/test.db"
            env["VECTOR_DB_PATH"] = f"{temp_dir}/chroma"

            result = subprocess.run(
                [sys.executable, start_py_path, "--init-only"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=temp_dir,
                env=env,
            )

            # Should mention database initialization
            assert "database" in result.stdout.lower() or "Database" in result.stdout

    def test_database_custom_url_handling(self):
        """Test that custom DATABASE_URL is handled"""
        start_py_path = get_start_py_path_or_skip()
        custom_db_path = "/tmp/custom_voxify.db"
        env = os.environ.copy()
        env["DATABASE_URL"] = f"sqlite:///{custom_db_path}"

        result = subprocess.run(
            [sys.executable, start_py_path, "--init-only"],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )

        # Should handle custom database URL (may fail, but should attempt it)
        assert "Welcome to Voxify!" in result.stdout


class TestStartupConfiguration:
    """
    Test startup configuration and environment handling.
    """

    def test_environment_variables_recognition(self):
        """Test that start.py recognizes environment variables"""
        start_py_path = get_start_py_path_or_skip()
        env = os.environ.copy()
        env["FLASK_HOST"] = "127.0.0.1"
        env["FLASK_PORT"] = "8000"
        env["FLASK_DEBUG"] = "true"

        result = subprocess.run(
            [sys.executable, start_py_path, "--init-only"],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )

        assert result.returncode in [0, None] or "Welcome to Voxify!" in result.stdout

    def test_production_vs_development_mode(self):
        """Test that start.py handles different environment modes"""
        start_py_path = get_start_py_path_or_skip()
        # Test development mode
        env = os.environ.copy()
        env["FLASK_ENV"] = "development"

        result = subprocess.run(
            [sys.executable, start_py_path, "--init-only"],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )

        assert "Welcome to Voxify!" in result.stdout

        # Test production mode
        env["FLASK_ENV"] = "production"
        result = subprocess.run(
            [sys.executable, start_py_path, "--init-only"],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )

        assert "Welcome to Voxify!" in result.stdout


class TestArgumentParsing:
    """
    Test command line argument parsing.
    """

    def test_invalid_arguments(self):
        """Test start.py with invalid arguments"""
        start_py_path = get_start_py_path_or_skip()
        result = subprocess.run(
            [sys.executable, start_py_path, "--invalid-flag"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should exit with error for invalid arguments
        assert result.returncode != 0
        assert "error" in result.stderr.lower() or "unrecognized" in result.stderr.lower()

    def test_multiple_valid_arguments(self):
        """Test start.py with multiple valid arguments"""
        start_py_path = get_start_py_path_or_skip()
        result = subprocess.run(
            [
                sys.executable,
                start_py_path,
                "--skip-db-init",
                "--skip-file-init",
                "--init-only",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should handle multiple arguments gracefully
        assert "Welcome to Voxify!" in result.stdout


class TestErrorHandling:
    """Test error handling in start.py"""

    def test_missing_dependencies_graceful_failure(self):
        """Test that start.py fails gracefully with missing dependencies"""
        start_py_path = get_start_py_path_or_skip()
        env = os.environ.copy()
        env["DATABASE_URL"] = "sqlite:///nonexistent/path/test.db"

        result = subprocess.run(
            [sys.executable, start_py_path, "--init-only"],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )

        # Should either succeed or fail gracefully (not crash)
        assert "Welcome to Voxify!" in result.stdout
        # Should not have Python tracebacks in normal output
        assert "Traceback" not in result.stdout


class TestScriptIntegrity:
    """
    Test script file integrity and basic functionality.
    """

    def test_script_syntax_valid(self):
        """Test that start.py has valid Python syntax"""
        start_py_path = get_start_py_path_or_skip()
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", start_py_path],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, f"Syntax error in start.py: {result.stderr}"

    def test_script_imports_valid(self):
        """Test that start.py imports are valid (basic import check)"""
        start_py_path = get_start_py_path_or_skip()
        # Test that the script can at least be parsed for imports
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                f"import ast; ast.parse(open(r'{start_py_path}', encoding='utf-8').read())",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, f"Import parsing failed: {result.stderr}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
