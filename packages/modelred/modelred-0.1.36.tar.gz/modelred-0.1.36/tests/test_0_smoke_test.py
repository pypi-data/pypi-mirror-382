"""
Quick Smoke Test - Validates SDK is installed correctly
Run this first to make sure everything is set up properly
"""

import sys
from pathlib import Path


def print_check(msg, success):
    status = "✅" if success else "❌"
    print(f"{status} {msg}")
    return success


def smoke_test():
    """Quick validation that SDK is installed and imports work"""

    print("\n" + "=" * 80)
    print("  ModelRed SDK - Smoke Test")
    print("=" * 80 + "\n")

    all_passed = True

    # Test 1: Check if src is in path
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

    # Test 2: Import main module
    try:
        import modelred

        all_passed &= print_check("Import modelred", True)
    except ImportError as e:
        all_passed &= print_check(f"Import modelred - {e}", False)
        return False

    # Test 3: Import main classes
    try:
        from modelred import ModelRed, AsyncModelRed

        all_passed &= print_check("Import ModelRed, AsyncModelRed", True)
    except ImportError as e:
        all_passed &= print_check(f"Import clients - {e}", False)

    # Test 4: Import enums and types
    try:
        from modelred import ModelProvider, Priority, AssessmentStatus

        all_passed &= print_check(
            "Import ModelProvider, Priority, AssessmentStatus", True
        )
    except ImportError as e:
        all_passed &= print_check(f"Import enums - {e}", False)

    # Test 5: Import config helpers
    try:
        from modelred import ProviderConfig

        all_passed &= print_check("Import ProviderConfig", True)
    except ImportError as e:
        all_passed &= print_check(f"Import ProviderConfig - {e}", False)

    # Test 6: Import display helpers
    try:
        from modelred import (
            print_header,
            print_assessment_summary,
            print_detailed_report,
            print_assessments_list,
            print_model_info,
            progress_tracker,
            print_full_results,
        )

        all_passed &= print_check("Import helper functions (7 functions)", True)
    except ImportError as e:
        all_passed &= print_check(f"Import helpers - {e}", False)

    # Test 7: Import exceptions
    try:
        from modelred import (
            ModelRedError,
            AuthenticationError,
            AuthorizationError,
            ValidationError,
            NotFoundError,
            ConflictError,
            SubscriptionLimitError,
            RateLimitError,
            ServerError,
            NetworkError,
        )

        all_passed &= print_check("Import exceptions (10 exception types)", True)
    except ImportError as e:
        all_passed &= print_check(f"Import exceptions - {e}", False)

    # Test 8: Check python-dotenv
    try:
        import dotenv

        all_passed &= print_check("Import dotenv (for .env file)", True)
    except ImportError:
        all_passed &= print_check(
            "Import dotenv (OPTIONAL - run: pip install python-dotenv)", False
        )
        print("   Note: dotenv is optional but needed for test scripts")

    # Test 9: Check .env file
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        all_passed &= print_check(f".env file exists at {env_path}", True)

        # Check if it has content
        content = env_path.read_text()

        # Check which environment we're targeting
        import os
        from dotenv import load_dotenv

        load_dotenv(env_path)
        base_url = os.getenv("MODELRED_BASE_URL", "https://app.modelred.ai/api")

        if "localhost" in base_url:
            print(f"   🏠 LOCAL DEV MODE: {base_url}")
        else:
            print(f"   🌐 PRODUCTION MODE: {base_url}")

        if "your_modelred_api_key_here" in content:
            print("   ⚠️  Warning: .env still has placeholder values")
            print("   → Edit .env and add your real API keys")
    else:
        all_passed &= print_check(".env file missing", False)
        print("   → Run setup.bat to create .env template")

    print("\n" + "=" * 80)
    if all_passed:
        print("  ✅ SMOKE TEST PASSED - SDK is ready!")
        print("=" * 80)
        print("\nNext steps:")
        print("  1. Edit .env file with your API keys (if not done)")
        print("  2. Run: python run_all_tests.py")
        print()
        return True
    else:
        print("  ❌ SMOKE TEST FAILED - Fix issues above")
        print("=" * 80)
        print("\nTroubleshooting:")
        print("  1. Run: setup.bat")
        print("  2. Install SDK: pip install -e ..")
        print("  3. Install dotenv: pip install python-dotenv")
        print()
        return False


if __name__ == "__main__":
    try:
        success = smoke_test()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
