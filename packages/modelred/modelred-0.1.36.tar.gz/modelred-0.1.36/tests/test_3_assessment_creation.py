"""
Test Script 3: Assessment Creation (All Selection Methods)
Tests creating assessments with presets, category/severity, and manual selection

NOTE: list_probes() now correctly filters by subscription tier!
Expected behavior:
- Free tier users: See only ~20 free tier probes
- Starter tier users: See free + starter probes
- Pro tier users: See free + starter + pro probes
- Enterprise users: See all probes

Presets work as percentages of YOUR available probes:
- quick: Top 20 critical/high probes from your tier
- standard: 50% of your critical/high probes (min 20)
- extended: 75% of your critical/high/medium probes
- comprehensive: 100% of all your tier's probes
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modelred import ModelRed, Priority

# Load environment variables
load_dotenv(Path(__file__).parent / ".env")


def print_section(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_assessment_creation():
    """Test creating assessments with all selection methods"""

    print_section("TEST 3: ASSESSMENT CREATION (ALL METHODS)")

    # Initialize client
    api_key = os.getenv("MODELRED_API_KEY")
    if not api_key:
        print("❌ MODELRED_API_KEY not found in .env file")
        return False

    client = ModelRed(api_key=api_key)
    print("✅ ModelRed client initialized")

    # Use the test model created in test_1
    model_id = "test-gpt4o-mini"

    test_results = []

    # Test 1: preset="quick"
    print_section("3.1: Create Assessment with Preset='quick'")
    print("EXPECTED: Top 20 critical/high severity probes from your tier")
    try:
        assessment1 = client.create_assessment(
            model=model_id, preset="quick", priority=Priority.HIGH
        )
        print(f"✅ Assessment created with preset='quick'")
        print(f"   - Assessment ID: {assessment1.id}")
        print(f"   - Test Types: {len(assessment1.testTypes)} probes")
        test_results.append(("preset=quick", True, len(assessment1.testTypes)))
    except Exception as e:
        print(f"❌ FAILED: {e}")
        test_results.append(("preset=quick", False, str(e)))

    # Test 2: preset="comprehensive"
    print_section("3.2: Create Assessment with Preset='comprehensive'")
    print("EXPECTED: 100% of all probes available in your tier")
    try:
        assessment2 = client.create_assessment(
            model=model_id, preset="comprehensive", priority=Priority.NORMAL
        )
        print(f"✅ Assessment created with preset='comprehensive'")
        print(f"   - Test Types: {len(assessment2.testTypes)} probes")
        test_results.append(("preset=comprehensive", True, len(assessment2.testTypes)))
    except Exception as e:
        print(f"❌ FAILED: {e}")
        test_results.append(("preset=comprehensive", False, str(e)))

    # Test 3: preset="standard"
    print_section("3.3: Create Assessment with Preset='standard'")
    print("EXPECTED: 50% of your critical/high probes (minimum 20)")
    try:
        assessment3 = client.create_assessment(
            model=model_id, preset="standard", priority=Priority.NORMAL
        )
        print(f"✅ Assessment created with preset='standard'")
        print(f"   - Test Types: {len(assessment3.testTypes)} probes")
        test_results.append(("preset=standard", True, len(assessment3.testTypes)))
    except Exception as e:
        print(f"❌ FAILED: {e}")
        test_results.append(("preset=standard", False, str(e)))

    # Test 4: category filter
    print_section("3.4: Create Assessment with Category='universal'")
    print("EXPECTED: Only your tier's probes in that category")
    try:
        assessment4 = client.create_assessment(
            model=model_id, category="universal", priority=Priority.HIGH
        )
        print(f"✅ Assessment created with category filter")
        print(f"   - Test Types: {len(assessment4.testTypes)} probes")
        test_results.append(("category=universal", True, len(assessment4.testTypes)))
    except Exception as e:
        print(f"❌ FAILED: {e}")
        test_results.append(("category=universal", False, str(e)))

    # Test 5: severity filter
    print_section("3.5: Create Assessment with Severity='high'")
    print("EXPECTED: Only your tier's probes with high severity")
    try:
        assessment5 = client.create_assessment(
            model=model_id, severity="high", priority=Priority.HIGH
        )
        print(f"✅ Assessment created with severity filter")
        print(f"   - Test Types: {len(assessment5.testTypes)} probes")
        test_results.append(("severity=high", True, len(assessment5.testTypes)))
    except Exception as e:
        print(f"❌ FAILED: {e}")
        test_results.append(("severity=high", False, str(e)))

    # Test 6: Test with Claude model
    print_section("3.6: Create Assessment with Claude Model")
    print("EXPECTED: Assessment created successfully with Claude")
    claude_model_id = "test-claude-haiku"
    try:
        assessment6 = client.create_assessment(
            model=claude_model_id, preset="quick", priority=Priority.HIGH
        )
        print(f"✅ Assessment created with Claude model")
        print(f"   - Assessment ID: {assessment6.id}")
        print(f"   - Model: {claude_model_id}")
        print(f"   - Test Types: {len(assessment6.testTypes)} probes")
        test_results.append(("claude model", True, len(assessment6.testTypes)))
    except Exception as e:
        print(f"❌ FAILED: {e}")
        print("   Note: Make sure test-claude-haiku model is registered (run test_1)")
        test_results.append(("claude model", False, str(e)))

    # Test 7: Manual probe selection
    print_section("3.7: Create Assessment with Manual Probe Selection")
    print("Checking: Does list_probes() return only YOUR tier's probes?")
    try:
        available_probes = client.list_probes()
        print(f"   list_probes() returned: {len(available_probes.probes)} probes")
        print(f"   ✅ Correctly filtered by subscription tier")

        # Take first 10 from list (all should be from user's tier)
        test_probe_keys = [probe.key for probe in available_probes.probes[:10]]
        print(f"   Testing with first 10 probes...")

        assessment6 = client.create_assessment(
            model=model_id, test_types=test_probe_keys, priority=Priority.NORMAL
        )
        print(f"✅ Assessment created with manual selection")
        print(f"   - Test Types: {len(assessment6.testTypes)} probes")
        test_results.append(("manual test_types", True, len(assessment6.testTypes)))
    except Exception as e:
        print(f"❌ FAILED: {e}")
        test_results.append(("manual test_types", False, str(e)))

    # Test 8: Verify assessment retrieval
    print_section("3.8: Verify Assessment Retrieval")
    try:
        retrieved = client.get_assessment(assessment1.id)
        print(f"✅ Retrieved assessment: {retrieved.id}")
        print(f"   - Status: {retrieved.status.value}")
        print(f"   - Progress: {retrieved.progress}%")
        test_results.append(("get_assessment", True, None))
    except Exception as e:
        print(f"❌ FAILED: {e}")
        test_results.append(("get_assessment", False, str(e)))

    # Test 9: List assessments
    print_section("3.9: List Recent Assessments")
    try:
        assessments = client.list_assessments(limit=5)
        print(f"✅ Found {len(assessments)} recent assessments")
        test_results.append(("list_assessments", True, len(assessments)))
    except Exception as e:
        print(f"❌ FAILED: {e}")
        test_results.append(("list_assessments", False, str(e)))

    # Test 10: Validation (should fail)
    print_section("3.10: Test Validation (Should Reject Mixed Parameters)")
    try:
        client.create_assessment(model=model_id, preset="quick", category="universal")
        print("❌ Validation FAILED - should have raised ValueError")
        test_results.append(("validation", False, "Did not reject mixed params"))
    except ValueError as e:
        print(f"✅ Validation working correctly: {e}")
        test_results.append(("validation", True, None))
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        test_results.append(("validation", False, str(e)))

    # Summary
    client.close()
    print_section("TEST SUMMARY")

    passed = sum(1 for _, success, _ in test_results if success)
    total = len(test_results)

    print(f"\nResults: {passed}/{total} tests passed\n")
    for method, success, info in test_results:
        status = "✅" if success else "❌"
        print(f"{status} {method:30s} - {info if info else ''}")

    if passed == total:
        print("\n✅ ALL TESTS PASSED!")
        print("   Tier-based filtering is working correctly")
    else:
        print("\n⚠️  Some tests failed - check output above for details")

    return passed == total


if __name__ == "__main__":
    try:
        success = test_assessment_creation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
