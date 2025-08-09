"""
Password Reset Tests Runner
Run all password reset functionality tests
"""

import unittest
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def run_all_password_reset_tests():
    """Run all password reset tests"""
    print("🧪 Running All Password Reset Tests")
    print("=" * 60)

    # Discover and run all tests in this directory
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern="test_*.py")

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 60)
    print("🎯 Password Reset Tests Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")

    if result.testsRun > 0:
        success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
        print(f"   Success rate: {success_rate:.1f}%")

        if success_rate == 100.0:
            print("   Status: ✅ ALL TESTS PASSED!")
        else:
            print("   Status: ❌ Some tests failed")
    else:
        print("   Status: ⚠️ No tests found")

    print("=" * 60)

    # Return success status
    return len(result.failures) == 0 and len(result.errors) == 0


if __name__ == "__main__":
    success = run_all_password_reset_tests()
    sys.exit(0 if success else 1)
