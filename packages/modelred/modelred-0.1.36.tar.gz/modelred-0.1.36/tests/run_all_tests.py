"""
Master Test Runner - Run All SDK Tests
"""

import sys
import subprocess
from pathlib import Path


def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def run_test(test_file):
    """Run a single test file"""
    test_name = test_file.stem.replace("_", " ").title()
    print_header(f"Running: {test_name}")

    try:
        result = subprocess.run(
            [sys.executable, str(test_file)],
            cwd=test_file.parent,
            capture_output=False,
            text=True,
        )

        if result.returncode == 0:
            print(f"✅ {test_name} PASSED\n")
            return True
        else:
            print(f"❌ {test_name} FAILED\n")
            return False

    except Exception as e:
        print(f"❌ Error running {test_name}: {e}\n")
        return False


def main():
    """Run all tests in order"""

    print_header("ModelRed SDK - Comprehensive Test Suite")
    print("This will test all SDK functionality:")
    print("  1. Model Registration (OpenAI, Anthropic, OpenRouter)")
    print("  2. Probe Discovery (filtering by category/severity)")
    print("  3. Assessment Creation (presets, filters, manual)")
    print("  4. Assessment Waiting & Results")
    print("  5. Helper Functions")
    print("  6. Context Managers & Async")
    print("\nMake sure you've filled in the .env file with your API keys!")
    print("\nPress Enter to start, or Ctrl+C to cancel...")
    input()

    tests_dir = Path(__file__).parent

    # Define test order
    test_files = [
        tests_dir / "test_1_model_registration.py",
        tests_dir / "test_2_probe_discovery.py",
        tests_dir / "test_3_assessment_creation.py",
        tests_dir / "test_4_assessment_waiting.py",
        tests_dir / "test_5_helper_functions.py",
        tests_dir / "test_6_context_managers_async.py",
    ]

    results = []
    for test_file in test_files:
        if not test_file.exists():
            print(f"⚠️  Test file not found: {test_file.name}")
            results.append(False)
            continue

        success = run_test(test_file)
        results.append(success)

    # Summary
    print_header("TEST SUMMARY")
    total = len(results)
    passed = sum(results)
    failed = total - passed

    print(f"Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"\nSuccess Rate: {(passed/total*100):.1f}%")

    if all(results):
        print_header("🎉 ALL TESTS PASSED! 🎉")
        return 0
    else:
        print_header("❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
