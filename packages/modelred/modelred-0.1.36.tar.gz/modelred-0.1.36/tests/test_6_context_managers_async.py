"""
Test Script 6: Context Managers & Async
Tests context manager usage and async client
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modelred import ModelRed, AsyncModelRed, Priority, ModelProvider, ProviderConfig

# Load environment variables
load_dotenv(Path(__file__).parent / ".env")


def print_section(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_context_manager():
    """Test sync context manager"""

    print_section("TEST 6.1: SYNC CONTEXT MANAGER")

    api_key = os.getenv("MODELRED_API_KEY")
    if not api_key:
        print("❌ MODELRED_API_KEY not found")
        return False

    # Test 1: with statement
    print("Testing 'with' statement:")
    try:
        with ModelRed(api_key=api_key) as client:
            print("✅ Context manager entered")

            # Test basic operations
            models = client.list_models()
            print(f"✅ Listed {models.total} models inside context")

            probes = client.list_probes()
            print(f"✅ Listed {len(probes.probes)} probes inside context")

        print("✅ Context manager exited (client.close() called automatically)")
        return True

    except Exception as e:
        print(f"❌ Error with context manager: {e}")
        return False


async def test_async_client():
    """Test async client"""

    print_section("TEST 6.2: ASYNC CLIENT")

    api_key = os.getenv("MODELRED_API_KEY")
    if not api_key:
        print("❌ MODELRED_API_KEY not found")
        return False

    try:
        # Test 1: Create async client
        print("Creating async client:")
        async with AsyncModelRed(api_key=api_key) as client:
            print("✅ Async context manager entered")

            # Test 2: List models async
            print("\nTesting async list_models():")
            models = await client.list_models()
            print(f"✅ Listed {models.total} models (async)")

            # Test 3: List probes async
            print("\nTesting async list_probes():")
            probes = await client.list_probes()
            print(f"✅ Listed {len(probes.probes)} probes (async)")

            # Test 4: Filter probes async
            print("\nTesting async list_probes() with filters:")
            critical = await client.list_probes(severity="critical")
            print(f"✅ Found {len(critical.probes)} critical probes (async)")

            # Test 5: Get model async
            print("\nTesting async get_model():")
            model = await client.get_model("test-gpt4o-mini")
            print(f"✅ Retrieved model: {model.displayName} (async)")

            # Test 6: Create assessment async (preset)
            print("\nTesting async create_assessment() with preset='quick':")
            assessment = await client.create_assessment(
                model="test-gpt4o-mini",
                preset="quick",
                priority=Priority.HIGH,
            )
            print(f"✅ Created assessment: {assessment.id} (async)")
            print(f"   - Using preset='quick' (free tier compatible)")

            # Test 7: Get assessment async
            print("\nTesting async get_assessment():")
            retrieved = await client.get_assessment(assessment.id)
            print(f"✅ Retrieved assessment: {retrieved.id} (async)")
            print(f"   - Status: {retrieved.status.value}")
            print(f"   - Progress: {retrieved.progress}%")

            # Test 8: List assessments async
            print("\nTesting async list_assessments():")
            assessments = await client.list_assessments(limit=5)
            print(f"✅ Listed {len(assessments)} assessments (async)")

            # Test 9: Skip manual probe selection (free tier limitation)
            print("\nSkipping manual probe selection test (free tier uses preset only)")

            # Test 10: Wait for completion async
            print("\nTesting async wait_for_completion():")
            print(f"   Waiting for assessment {assessment.id}...")

            progress_count = [0]

            def async_progress(assessment):
                progress_count[0] += 1
                print(
                    f"   📊 Progress: {assessment.progress}% ({progress_count[0]} updates)"
                )

            result = await client.wait_for_completion(
                assessment.id,
                timeout_minutes=30,
                poll_interval=10,
                progress_callback=async_progress,
            )
            print(f"✅ Assessment completed (async)")
            print(f"   - Status: {result.status.value}")
            print(f"   - Progress updates: {progress_count[0]}")

            if result.detailedReport:
                print(
                    f"   - Overall Score: {result.detailedReport.get('overall_score', 'N/A')}"
                )

        print("✅ Async context manager exited")
        return True

    except Exception as e:
        print(f"❌ Error with async client: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_async_model_registration():
    """Test async model registration"""

    print_section("TEST 6.3: ASYNC MODEL REGISTRATION")

    api_key = os.getenv("MODELRED_API_KEY")
    if not api_key:
        print("❌ MODELRED_API_KEY not found")
        return False

    try:
        async with AsyncModelRed(api_key=api_key) as client:
            # Test registering models async
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                print("Testing async create_model():")
                from modelred import ConflictError

                try:
                    model = await client.create_model(
                        modelId="test-async-gpt4o",
                        provider=ModelProvider.OPENAI,
                        displayName="Test Async GPT-4o-mini",
                        providerConfig=ProviderConfig.openai(
                            api_key=openai_key, model_name="gpt-4o-mini"
                        ),
                    )
                    print(f"✅ Created model async: {model.modelId}")
                except ConflictError:
                    print("⚠️  Model exists, fetching...")
                    model = await client.get_model("test-async-gpt4o")
                    print(f"✅ Retrieved existing model: {model.modelId}")
            else:
                print("⚠️  OPENAI_API_KEY not found, skipping")

        return True

    except Exception as e:
        print(f"❌ Error with async model registration: {e}")
        return False


def main():
    """Run all tests"""

    print_section("TEST 6: CONTEXT MANAGERS & ASYNC")

    # Test 1: Sync context manager
    sync_success = test_context_manager()

    # Test 2: Async client
    async_success = asyncio.run(test_async_client())

    # Test 3: Async model registration
    async_model_success = asyncio.run(test_async_model_registration())

    if sync_success and async_success and async_model_success:
        print_section("✅ ALL CONTEXT MANAGER & ASYNC TESTS PASSED")
        return True
    else:
        print_section("❌ SOME TESTS FAILED")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
