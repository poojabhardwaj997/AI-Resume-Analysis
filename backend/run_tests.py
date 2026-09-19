import sys
import time
import pytest

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def main():
    print("=" * 70)
    print(" AI RESUME ANALYSIS & SKILL GAP DETECTION - TEST RUNNER")
    print("=" * 70)
    print("Discovering and executing test suites across all pipeline layers...")
    print("Target directory: tests/\n")

    start_time = time.time()
    
    # Run pytest with verbosity and summary flags
    args = [
        "tests",
        "-v",
        "--tb=short",
        "-rA"
    ]
    
    exit_code = pytest.main(args)
    duration = time.time() - start_time

    print("\n" + "=" * 70)
    if exit_code == 0:
        print(f" [SUCCESS] ALL TESTS PASSED SUCCESSFULLY in {duration:.2f}s!")
    else:
        print(f" [FAILED] TEST SUITE COMPLETED with exit code {exit_code} in {duration:.2f}s")
    print("=" * 70)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
