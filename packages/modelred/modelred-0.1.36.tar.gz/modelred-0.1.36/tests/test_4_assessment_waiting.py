"""
Test Script 4: Assessment Waiting & Results
Tests waiting for assessment completion and retrieving results
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modelred import ModelRed, Priority, progress_tracker

# Load environment variables
load_dotenv(Path(__file__).parent / ".env")


def print_section(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_assessment_waiting():
    """Test waiting for assessments and retrieving results"""

    print_section("TEST 4: ASSESSMENT WAITING & RESULTS")

    # Initialize client
    api_key = os.getenv("MODELRED_API_KEY")
    if not api_key:
        print("❌ MODELRED_API_KEY not found in .env file")
        return False

    client = ModelRed(api_key=api_key)
    print("✅ ModelRed client initialized")

    # Use the test model created in test_1
    model_id = "test-gpt4o-mini"

    # Test 1: Create assessment with preset and wait with progress tracker
    print_section(
        "4.1: Create Assessment (preset='quick') and Wait with Progress Tracker"
    )
    try:
        assessment = client.create_assessment(
            model=model_id, preset="quick", priority=Priority.HIGH
        )
        print(f"✅ Assessment created: {assessment.id}")
        print(f"   - Using preset='quick' (free tier compatible)")
        print(f"   Starting wait_for_completion with progress tracker...")

        result = client.wait_for_completion(
            assessment.id,
            timeout_minutes=30,
            poll_interval=10,
            progress_callback=progress_tracker,
        )

        print(f"\n✅ Assessment completed!")
        print(f"   - Status: {result.status.value}")
        print(f"   - Progress: {result.progress}%")

        if result.detailedReport:
            print(
                f"   - Overall Score: {result.detailedReport.get('overall_score', 'N/A')}"
            )
            print(f"   - Risk Level: {result.detailedReport.get('risk_level', 'N/A')}")
            print(
                f"   - Total Tests: {result.detailedReport.get('total_tests', 'N/A')}"
            )
            print(f"   - Passed: {result.detailedReport.get('passed_tests', 'N/A')}")
            print(f"   - Failed: {result.detailedReport.get('failed_tests', 'N/A')}")
        else:
            print("   - Detailed report not yet available")

    except Exception as e:
        print(f"❌ Error in wait_for_completion: {e}")
        return False

    # Test 2: Simple status check without waiting
    print_section("4.2: Check Assessment Status (No Wait)")
    try:
        # Get just 10 probes for quick testing
        high_severity_probes = client.list_probes(severity="high")
        probe_keys_10 = [p.key for p in high_severity_probes.probes[:10]]

        assessment2 = client.create_assessment(
            model=model_id, test_types=probe_keys_10, priority=Priority.HIGH
        )
        print(f"✅ Assessment created: {assessment2.id}")
        print(f"   - Using 10 high severity probes (faster testing)")

        # Custom callback
        progress_updates = []

        def custom_callback(assessment):
            progress_updates.append(assessment.progress)
            print(
                f"   📊 Progress update: {assessment.progress}% - {assessment.status.value}"
            )

        result2 = client.wait_for_completion(
            assessment2.id,
            timeout_minutes=30,
            poll_interval=10,
            progress_callback=custom_callback,
        )

        print(f"\n✅ Assessment completed!")
        print(f"   - Received {len(progress_updates)} progress updates")
        print(f"   - Final status: {result2.status.value}")

    except Exception as e:
        print(f"❌ Error with custom callback: {e}")
        return False

    # Test 3: Check detailed report structure
    print_section("4.3: Check Detailed Report Structure")
    try:
        if result.detailedReport:
            report = result.detailedReport
            print("✅ Detailed report structure:")
            print(f"   - overall_score: {report.get('overall_score')}")
            print(f"   - risk_level: {report.get('risk_level')}")
            print(f"   - total_tests: {report.get('total_tests')}")
            print(f"   - passed_tests: {report.get('passed_tests')}")
            print(f"   - failed_tests: {report.get('failed_tests')}")

            if "probes" in report and report["probes"]:
                print(f"\n   Sample probe result:")
                probe_result = report["probes"][0]
                print(f"   - Probe: {probe_result.get('displayName')}")
                print(f"   - Category: {probe_result.get('category')}")
                print(f"   - Severity: {probe_result.get('severity')}")
                print(f"   - Pass Rate: {probe_result.get('pass_rate')}%")
                print(f"   - Total Cases: {probe_result.get('total_cases')}")
        else:
            print("⚠️  Detailed report not available yet")

    except Exception as e:
        print(f"❌ Error checking report structure: {e}")
        return False

    # Test 4: Get assessment without waiting
    print_section("4.4: Get Assessment Status (No Wait)")
    try:
        # Create a new assessment
        assessment3 = client.create_assessment(
            model=model_id, category="universal", priority=Priority.NORMAL
        )
        print(f"✅ Assessment created: {assessment3.id}")

        # Immediately get status
        status_check = client.get_assessment(assessment3.id)
        print(f"   - Immediate status: {status_check.status.value}")
        print(f"   - Progress: {status_check.progress}%")
        print(f"   - Has report: {'Yes' if status_check.detailedReport else 'No'}")

    except Exception as e:
        print(f"❌ Error checking status: {e}")
        return False

    # Cleanup
    client.close()
    print_section("✅ ALL ASSESSMENT WAITING TESTS PASSED")
    return True


if __name__ == "__main__":
    try:
        success = test_assessment_waiting()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
