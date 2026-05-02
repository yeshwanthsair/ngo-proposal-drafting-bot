"""
Run Week 1 tests and print a summary report.
Usage: python scripts/run_tests.py
"""
import subprocess
import sys

if __name__ == "__main__":
    print("=" * 60)
    print("NGO Proposal Drafting Bot - Week 1 Test Suite")
    print("=" * 60)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_week1.py", "-v", "--tb=short"],
        capture_output=False,
    )
    sys.exit(result.returncode)
