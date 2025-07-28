"""
Voice Service Performance Tests
Tests for performance and scalability of voice service functionality
"""

import pytest
import time
import threading
import subprocess
import json
import sys
import os
import statistics

# Add the backend directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))


class TestVoiceServicePerformance:
    """Performance tests for voice service functionality"""

    @pytest.fixture(scope="class", autouse=True)
    def check_server(self, server_url):
        """Check if server is running before tests"""
        try:
            import requests

            response = requests.get(f"{server_url}/api/v1/auth/login", timeout=5)
            assert response.status_code == 405, f"Unexpected status code: {response.status_code}"
        except Exception as e:
            pytest.skip(f"Server not available: {e}")

    @pytest.fixture(scope="class")
    def server_url(self):
        """Get the Flask server URL based on start.py configuration"""
        host = os.getenv("FLASK_HOST", "127.0.0.1")
        port = int(os.getenv("PORT", os.getenv("FLASK_PORT", 8000)))
        return f"http://{host}:{port}"

    @pytest.fixture(scope="class")
    def test_user(self):
        """Test user credentials for performance tests"""
        return {
            "email": "performance_test@example.com",
            "password": "PerformanceTest123!@#",
            "first_name": "Performance",
            "last_name": "Tester",
        }

    @pytest.fixture(scope="class")
    def auth_tokens(self, server_url, test_user):
        """Get authentication tokens for testing"""
        # Register user
        register_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/auth/register",
            "-H",
            "Content-Type: application/json",
            "-d",
            json.dumps(test_user),
        ]
        subprocess.run(register_cmd, capture_output=True)

        # Login to get tokens
        login_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/auth/login",
            "-H",
            "Content-Type: application/json",
            "-d",
            json.dumps({"email": test_user["email"], "password": test_user["password"]}),
        ]
        result = subprocess.run(login_cmd, capture_output=True, text=True)
        response = json.loads(result.stdout)
        return {
            "access_token": response.get("data", {}).get("access_token"),
            "refresh_token": response.get("data", {}).get("refresh_token"),
        }

    @pytest.fixture(scope="class")
    def test_audio_file(self):
        """Use the local file_example_WAV_1MG.wav as the test audio file."""
        return os.path.join(os.path.dirname(__file__), "file_example_WAV_1MG.wav")

    def test_upload_performance_single_file(self, server_url, auth_tokens, test_audio_file):
        """Test performance of single file upload"""
        start_time = time.time()

        upload_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/voice/samples",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
            "-F",
            f"name=Performance Test Sample",
            "-F",
            f"file=@{test_audio_file}",
        ]

        result = subprocess.run(upload_cmd, capture_output=True, text=True)
        end_time = time.time()

        upload_time = end_time - start_time

        assert result.returncode == 0, f"Upload failed: {result.stderr}"

        upload_response = json.loads(result.stdout)
        assert upload_response.get("success") is True, f"Upload failed: {upload_response}"

        # Performance assertions
        assert upload_time < 30.0, f"Upload took too long: {upload_time:.2f}s"

        print(f"Single file upload time: {upload_time:.2f}s")

        return upload_response["data"]["sample_id"]

    def test_upload_performance_multiple_files(self, server_url, auth_tokens, test_audio_file):
        """Test performance of multiple file uploads"""
        upload_times = []
        sample_ids = []

        for i in range(3):
            start_time = time.time()

            upload_cmd = [
                "curl",
                "-X",
                "POST",
                f"{server_url}/api/v1/voice/samples",
                "-H",
                f"Authorization: Bearer {auth_tokens['access_token']}",
                "-F",
                f"name=Performance Test Sample {i+1}",
                "-F",
                f"file=@{test_audio_file}",
            ]

            result = subprocess.run(upload_cmd, capture_output=True, text=True)
            end_time = time.time()

            upload_time = end_time - start_time
            upload_times.append(upload_time)

            assert result.returncode == 0, f"Upload {i+1} failed: {result.stderr}"

            upload_response = json.loads(result.stdout)
            assert upload_response.get("success") is True, f"Upload {i+1} failed: {upload_response}"

            sample_ids.append(upload_response["data"]["sample_id"])

        # Performance analysis
        avg_upload_time = statistics.mean(upload_times)
        max_upload_time = max(upload_times)
        min_upload_time = min(upload_times)

        print(f"Multiple file upload performance:")
        print(f"  Average time: {avg_upload_time:.2f}s")
        print(f"  Min time: {min_upload_time:.2f}s")
        print(f"  Max time: {max_upload_time:.2f}s")

        # Performance assertions
        assert avg_upload_time < 30.0, f"Average upload time too long: {avg_upload_time:.2f}s"
        assert max_upload_time < 60.0, f"Max upload time too long: {max_upload_time:.2f}s"

        return sample_ids

    def test_concurrent_upload_performance(self, server_url, auth_tokens, test_audio_file):
        """Test performance of concurrent file uploads"""
        results = []
        upload_times = []

        def upload_sample(thread_id):
            """Upload a sample in a separate thread"""
            start_time = time.time()

            upload_cmd = [
                "curl",
                "-X",
                "POST",
                f"{server_url}/api/v1/voice/samples",
                "-H",
                f"Authorization: Bearer {auth_tokens['access_token']}",
                "-F",
                f"name=Concurrent Performance Test {thread_id}",
                "-F",
                f"file=@{test_audio_file}",
            ]

            result = subprocess.run(upload_cmd, capture_output=True, text=True)
            end_time = time.time()

            upload_time = end_time - start_time
            response = json.loads(result.stdout)

            results.append((thread_id, response.get("success"), upload_time))

        # Start multiple upload threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=upload_sample, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Analyze results
        successful_uploads = [r for r in results if r[1]]
        upload_times = [r[2] for r in results]

        print(f"Concurrent upload performance:")
        print(f"  Successful uploads: {len(successful_uploads)}/{len(results)}")
        print(f"  Average time: {statistics.mean(upload_times):.2f}s")
        print(f"  Max time: {max(upload_times):.2f}s")

        # Performance assertions
        assert len(successful_uploads) == len(results), "Some concurrent uploads failed"
        assert (
            statistics.mean(upload_times) < 60.0
        ), f"Average concurrent upload time too long: {statistics.mean(upload_times):.2f}s"

    def test_clone_creation_performance(self, server_url, auth_tokens, test_audio_file):
        """Test performance of voice clone creation"""
        # First upload a sample
        upload_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/voice/samples",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
            "-F",
            f"name=Clone Performance Test Sample",
            "-F",
            f"file=@{test_audio_file}",
        ]

        result = subprocess.run(upload_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Upload for clone performance test failed: {result.stderr}"

        upload_response = json.loads(result.stdout)
        assert upload_response.get("success") is True, f"Upload for clone performance test failed: {upload_response}"

        sample_id = upload_response["data"]["sample_id"]

        # Test clone creation performance
        start_time = time.time()

        clone_data = {
            "sample_ids": [sample_id],
            "name": "Performance Test Clone",
            "ref_text": "This is a performance test reference text for voice cloning",
        }

        clone_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/voice/clones",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
            "-H",
            "Content-Type: application/json",
            "-d",
            json.dumps(clone_data),
        ]

        result = subprocess.run(clone_cmd, capture_output=True, text=True)
        end_time = time.time()

        clone_creation_time = end_time - start_time

        assert result.returncode == 0, f"Clone creation failed: {result.stderr}"

        clone_response = json.loads(result.stdout)
        assert clone_response.get("success") is True, f"Clone creation failed: {clone_response}"

        print(f"Clone creation time: {clone_creation_time:.2f}s")

        # Performance assertions
        assert clone_creation_time < 120.0, f"Clone creation took too long: {clone_creation_time:.2f}s"

        return clone_response["data"]["clone_id"]

    def test_synthesis_performance(self, server_url, auth_tokens, test_audio_file):
        """Test performance of speech synthesis"""
        # First create a clone
        upload_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/voice/samples",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
            "-F",
            f"name=Synthesis Performance Test Sample",
            "-F",
            f"file=@{test_audio_file}",
        ]

        result = subprocess.run(upload_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Upload for synthesis performance test failed: {result.stderr}"

        upload_response = json.loads(result.stdout)
        assert (
            upload_response.get("success") is True
        ), f"Upload for synthesis performance test failed: {upload_response}"

        sample_id = upload_response["data"]["sample_id"]

        # Create clone
        clone_data = {
            "sample_ids": [sample_id],
            "name": "Synthesis Performance Test Clone",
            "ref_text": "This is a performance test reference text for synthesis",
        }

        clone_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/voice/clones",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
            "-H",
            "Content-Type: application/json",
            "-d",
            json.dumps(clone_data),
        ]

        result = subprocess.run(clone_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Clone creation for synthesis performance test failed: {result.stderr}"

        clone_response = json.loads(result.stdout)
        assert (
            clone_response.get("success") is True
        ), f"Clone creation for synthesis performance test failed: {clone_response}"

        clone_id = clone_response["data"]["clone_id"]

        # Test synthesis performance
        synthesis_times = []

        for i in range(3):
            start_time = time.time()

            synthesis_data = {
                "text": f"This is synthesis performance test {i+1}. Hello, this is a performance test for speech synthesis.",
                "speed": 1.0,
                "language": "zh-CN",
            }

            synthesize_cmd = [
                "curl",
                "-X",
                "POST",
                f"{server_url}/api/v1/voice/clones/{clone_id}/synthesize",
                "-H",
                f"Authorization: Bearer {auth_tokens['access_token']}",
                "-H",
                "Content-Type: application/json",
                "-d",
                json.dumps(synthesis_data),
            ]

            result = subprocess.run(synthesize_cmd, capture_output=True, text=True)
            end_time = time.time()

            synthesis_time = end_time - start_time
            synthesis_times.append(synthesis_time)

            assert result.returncode == 0, f"Synthesis {i+1} failed: {result.stderr}"

            synthesis_response = json.loads(result.stdout)
            assert synthesis_response.get("success") is True, f"Synthesis {i+1} failed: {synthesis_response}"

        # Performance analysis
        avg_synthesis_time = statistics.mean(synthesis_times)
        max_synthesis_time = max(synthesis_times)
        min_synthesis_time = min(synthesis_times)

        print(f"Synthesis performance:")
        print(f"  Average time: {avg_synthesis_time:.2f}s")
        print(f"  Min time: {min_synthesis_time:.2f}s")
        print(f"  Max time: {max_synthesis_time:.2f}s")

        # Performance assertions
        assert avg_synthesis_time < 60.0, f"Average synthesis time too long: {avg_synthesis_time:.2f}s"
        assert max_synthesis_time < 120.0, f"Max synthesis time too long: {max_synthesis_time:.2f}s"

    def test_list_operations_performance(self, server_url, auth_tokens):
        """Test performance of list operations"""
        list_times = []

        for i in range(5):
            start_time = time.time()

            list_cmd = [
                "curl",
                "-X",
                "GET",
                f"{server_url}/api/v1/voice/samples",
                "-H",
                f"Authorization: Bearer {auth_tokens['access_token']}",
            ]

            result = subprocess.run(list_cmd, capture_output=True, text=True)
            end_time = time.time()

            list_time = end_time - start_time
            list_times.append(list_time)

            assert result.returncode == 0, f"List operation {i+1} failed: {result.stderr}"

            list_response = json.loads(result.stdout)
            assert list_response.get("success") is True, f"List operation {i+1} failed: {list_response}"

        # Performance analysis
        avg_list_time = statistics.mean(list_times)
        max_list_time = max(list_times)
        min_list_time = min(list_times)

        print(f"List operations performance:")
        print(f"  Average time: {avg_list_time:.2f}s")
        print(f"  Min time: {min_list_time:.2f}s")
        print(f"  Max time: {max_list_time:.2f}s")

        # Performance assertions
        assert avg_list_time < 5.0, f"Average list time too long: {avg_list_time:.2f}s"
        assert max_list_time < 10.0, f"Max list time too long: {max_list_time:.2f}s"

    def test_memory_usage_monitoring(self):
        """Test memory usage monitoring"""
        import psutil
        import os

        # Get current memory usage
        process = psutil.Process(os.getpid())
        memory_usage = process.memory_info().rss / 1024 / 1024  # MB

        print(f"Current memory usage: {memory_usage:.2f} MB")

        # Memory usage should be reasonable
        assert memory_usage < 1000, f"Memory usage too high: {memory_usage:.2f} MB"

    def test_cpu_usage_monitoring(self):
        """Test CPU usage monitoring"""
        import psutil

        # Get current CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)

        print(f"Current CPU usage: {cpu_percent:.2f}%")

        # CPU usage should be reasonable
        assert 0 <= cpu_percent <= 100, f"Invalid CPU usage: {cpu_percent:.2f}%"

    def test_response_time_consistency(self, server_url, auth_tokens):
        """Test consistency of response times"""
        response_times = []

        # Perform multiple identical requests
        for i in range(10):
            start_time = time.time()

            list_cmd = [
                "curl",
                "-X",
                "GET",
                f"{server_url}/api/v1/voice/samples",
                "-H",
                f"Authorization: Bearer {auth_tokens['access_token']}",
            ]

            result = subprocess.run(list_cmd, capture_output=True, text=True)
            end_time = time.time()

            response_time = end_time - start_time
            response_times.append(response_time)

            assert result.returncode == 0, f"Request {i+1} failed: {result.stderr}"

            list_response = json.loads(result.stdout)
            assert list_response.get("success") is True, f"Request {i+1} failed: {list_response}"

        # Calculate consistency metrics
        avg_response_time = statistics.mean(response_times)
        std_response_time = statistics.stdev(response_times)
        cv_response_time = std_response_time / avg_response_time if avg_response_time > 0 else 0

        print(f"Response time consistency:")
        print(f"  Average time: {avg_response_time:.3f}s")
        print(f"  Standard deviation: {std_response_time:.3f}s")
        print(f"  Coefficient of variation: {cv_response_time:.3f}")

        # Consistency assertions
        assert cv_response_time < 0.5, f"Response time too inconsistent: CV = {cv_response_time:.3f}"
        assert avg_response_time < 5.0, f"Average response time too long: {avg_response_time:.3f}s"

    def test_concurrent_user_simulation(self, server_url, auth_tokens, test_audio_file):
        """Test performance under simulated concurrent users"""
        results = []

        def simulate_user(user_id):
            """Simulate a user performing typical operations"""
            user_results = []

            # Upload a sample
            start_time = time.time()
            upload_cmd = [
                "curl",
                "-X",
                "POST",
                f"{server_url}/api/v1/voice/samples",
                "-H",
                f"Authorization: Bearer {auth_tokens['access_token']}",
                "-F",
                f"name=Concurrent User {user_id} Sample",
                "-F",
                f"file=@{test_audio_file}",
            ]

            result = subprocess.run(upload_cmd, capture_output=True, text=True)
            upload_time = time.time() - start_time

            if result.returncode == 0:
                upload_response = json.loads(result.stdout)
                if upload_response.get("success"):
                    user_results.append(("upload", upload_time, True))
                else:
                    user_results.append(("upload", upload_time, False))
            else:
                user_results.append(("upload", upload_time, False))

            # List samples
            start_time = time.time()
            list_cmd = [
                "curl",
                "-X",
                "GET",
                f"{server_url}/api/v1/voice/samples",
                "-H",
                f"Authorization: Bearer {auth_tokens['access_token']}",
            ]

            result = subprocess.run(list_cmd, capture_output=True, text=True)
            list_time = time.time() - start_time

            if result.returncode == 0:
                list_response = json.loads(result.stdout)
                if list_response.get("success"):
                    user_results.append(("list", list_time, True))
                else:
                    user_results.append(("list", list_time, False))
            else:
                user_results.append(("list", list_time, False))

            return user_results

        # Simulate multiple concurrent users
        threads = []
        for i in range(3):
            thread = threading.Thread(target=lambda: results.append(simulate_user(i)))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Analyze results
        all_operations = []
        for user_results in results:
            all_operations.extend(user_results)

        successful_operations = [op for op in all_operations if op[2]]
        operation_times = [op[1] for op in all_operations]

        print(f"Concurrent user simulation results:")
        print(f"  Total operations: {len(all_operations)}")
        print(f"  Successful operations: {len(successful_operations)}")
        print(f"  Success rate: {len(successful_operations)/len(all_operations)*100:.1f}%")
        print(f"  Average operation time: {statistics.mean(operation_times):.2f}s")

        # Performance assertions
        assert len(successful_operations) / len(all_operations) > 0.8, "Success rate too low"
        assert statistics.mean(operation_times) < 30.0, "Average operation time too long"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
