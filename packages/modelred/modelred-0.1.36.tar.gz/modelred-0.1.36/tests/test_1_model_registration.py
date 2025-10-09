"""
Test Script 1: Model Registration
Tests creating and managing models with different providers
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modelred import ModelRed, ModelProvider, ProviderConfig, ConflictError

# Load environment variables
load_dotenv(Path(__file__).parent / ".env")


def print_section(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_model_registration():
    """Test registering models with different providers"""

    print_section("TEST 1: MODEL REGISTRATION")

    # Initialize client
    api_key = os.getenv("MODELRED_API_KEY")
    if not api_key:
        print("❌ MODELRED_API_KEY not found in .env file")
        return False

    print(f"✅ API Key loaded: {api_key[:10]}...")

    client = ModelRed(api_key=api_key)
    print("✅ ModelRed client initialized")

    # Test 1: Register OpenAI GPT-4o-mini
    print_section("1.1: Register OpenAI GPT-4o-mini")
    try:
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            print("⚠️  OPENAI_API_KEY not found, skipping OpenAI model")
        else:
            try:
                gpt_model = client.create_model(
                    modelId="test-gpt4o-mini",
                    provider=ModelProvider.OPENAI,
                    displayName="Test GPT-4o-mini",
                    providerConfig=ProviderConfig.openai(
                        api_key=openai_key, model_name="gpt-4o-mini"
                    ),
                )
                print(f"✅ OpenAI model registered: {gpt_model.modelId}")
                print(f"   - Display Name: {gpt_model.displayName}")
                print(f"   - Provider: {gpt_model.provider}")
                print(f"   - Model Name: {gpt_model.modelName}")
                print(f"   - Active: {gpt_model.isActive}")
            except ConflictError:
                print("⚠️  Model already exists, fetching existing...")
                gpt_model = client.get_model("test-gpt4o-mini")
                print(f"✅ Fetched existing OpenAI model: {gpt_model.modelId}")
    except Exception as e:
        print(f"❌ Error registering OpenAI model: {e}")
        return False

    # Test 2: Register Anthropic Claude 3.5 Haiku
    print_section("1.2: Register Anthropic Claude 3.5 Haiku")
    try:
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_key:
            print("⚠️  ANTHROPIC_API_KEY not found, skipping Anthropic model")
        else:
            try:
                claude_model = client.create_model(
                    modelId="test-claude-haiku",
                    provider=ModelProvider.ANTHROPIC,
                    displayName="Test Claude 3.5 Haiku",
                    providerConfig=ProviderConfig.anthropic(
                        api_key=anthropic_key, model_name="claude-3-5-haiku-20241022"
                    ),
                )
                print(f"✅ Anthropic model registered: {claude_model.modelId}")
                print(f"   - Display Name: {claude_model.displayName}")
                print(f"   - Provider: {claude_model.provider}")
                print(f"   - Model Name: {claude_model.modelName}")
                print(f"   - Active: {claude_model.isActive}")
            except ConflictError:
                print("⚠️  Model already exists, fetching existing...")
                claude_model = client.get_model("test-claude-haiku")
                print(f"✅ Fetched existing Anthropic model: {claude_model.modelId}")
    except Exception as e:
        print(f"❌ Error registering Anthropic model: {e}")
        return False

    # Test 3: List all models
    print_section("1.3: List All Models")
    try:
        models = client.list_models()
        print(f"✅ Found {models.total} total models")
        print(f"   - Page: {models.page}/{models.totalPages}")
        print(f"   - Page Size: {models.pageSize}")
        print(f"\nRegistered models:")
        for i, model in enumerate(models.models[:5], 1):
            print(
                f"   {i}. {model.displayName} ({model.provider}) - ID: {model.modelId}"
            )
    except Exception as e:
        print(f"❌ Error listing models: {e}")
        return False

    # Test 4: Get specific model
    print_section("1.4: Get Specific Model")
    try:
        model = client.get_model("test-gpt4o-mini")
        print(f"✅ Retrieved model: {model.modelId}")
        print(f"   - Display Name: {model.displayName}")
        print(f"   - Provider: {model.provider}")
        print(f"   - Test Count: {model.testCount}")
        print(f"   - Last Tested: {model.lastTested}")
    except Exception as e:
        print(f"❌ Error getting model: {e}")
        return False

    # Cleanup
    client.close()
    print_section("✅ ALL MODEL REGISTRATION TESTS PASSED")
    return True


if __name__ == "__main__":
    try:
        success = test_model_registration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
