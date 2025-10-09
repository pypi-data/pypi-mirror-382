"""
Test Script 5: Helper Functions
Tests all display helper functions
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modelred import (
    ModelRed,
    Priority,
    print_header,
    print_assessment_summary,
    print_detailed_report,
    print_assessments_list,
    print_model_info,
    progress_tracker,
    print_full_results,
)

# Load environment variables
load_dotenv(Path(__file__).parent / ".env")


def print_section(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_helper_functions():
    """Test all display helper functions"""

    print_section("TEST 5: HELPER FUNCTIONS")

    # Initialize client
    api_key = os.getenv("MODELRED_API_KEY")
    if not api_key:
        print("❌ MODELRED_API_KEY not found in .env file")
        return False

    client = ModelRed(api_key=api_key)
    print("✅ ModelRed client initialized")

    # Test 1: print_header()
    print_section("5.1: Test print_header()")
    try:
        print_header("TEST HEADER")
        print("✅ print_header() works")
    except Exception as e:
        print(f"❌ Error in print_header: {e}")
        return False

    # Test 2: print_model_info()
    print_section("5.2: Test print_model_info()")
    try:
        model = client.get_model("test-gpt4o-mini")
        print_model_info(model)
        print("✅ print_model_info() works")
    except Exception as e:
        print(f"❌ Error in print_model_info: {e}")
        return False

    # Test 3: Create an assessment with preset for testing
    print_section("5.3: Create Test Assessment (preset='quick')")
    try:
        assessment = client.create_assessment(
            model="test-gpt4o-mini", preset="quick", priority=Priority.HIGH
        )
        print(f"✅ Assessment created: {assessment.id}")
        print(f"   - Using preset='quick' (free tier compatible)")
    except Exception as e:
        print(f"❌ Error creating assessment: {e}")
        return False

    # Test 4: print_assessment_summary()
    print_section("5.4: Test print_assessment_summary()")
    try:
        print_assessment_summary(assessment)
        print("✅ print_assessment_summary() works")
    except Exception as e:
        print(f"❌ Error in print_assessment_summary: {e}")
        return False

    # Test 5: Wait for completion and test print_detailed_report()
    print_section("5.5: Wait and Test print_detailed_report()")
    try:
        print("Waiting for assessment to complete...")
        result = client.wait_for_completion(
            assessment.id,
            timeout_minutes=30,
            poll_interval=10,
            progress_callback=progress_tracker,
        )

        if result.detailedReport:
            print("\nTesting print_detailed_report():")
            print_detailed_report(result.detailedReport)
            print("✅ print_detailed_report() works")
        else:
            print("⚠️  Detailed report not available")
    except Exception as e:
        print(f"❌ Error in print_detailed_report: {e}")
        return False

    # Test 6: print_assessments_list()
    print_section("5.6: Test print_assessments_list()")
    try:
        assessments = client.list_assessments(limit=5)
        print_assessments_list(assessments, "RECENT ASSESSMENTS")
        print("✅ print_assessments_list() works")
    except Exception as e:
        print(f"❌ Error in print_assessments_list: {e}")
        return False

    # Test 7: print_full_results()
    print_section("5.7: Test print_full_results()")
    try:
        print_full_results(client, assessment.id)
        print("✅ print_full_results() works")
    except Exception as e:
        print(f"❌ Error in print_full_results: {e}")
        return False

    # Test 8: Test progress_tracker with new assessment
    print_section("5.8: Test progress_tracker Callback")
    try:
        assessment2 = client.create_assessment(
            model="test-gpt4o-mini", severity="high", priority=Priority.HIGH
        )
        print(f"Assessment created: {assessment2.id}")
        print("Testing progress_tracker callback:")

        result2 = client.wait_for_completion(
            assessment2.id,
            timeout_minutes=30,
            poll_interval=10,
            progress_callback=progress_tracker,
        )
        print("✅ progress_tracker callback works")
    except Exception as e:
        print(f"❌ Error with progress_tracker: {e}")
        return False

    # Cleanup
    client.close()
    print_section("✅ ALL HELPER FUNCTION TESTS PASSED")
    return True


if __name__ == "__main__":
    try:
        success = test_helper_functions()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
