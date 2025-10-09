# ModelRed Python SDK Changelog

## v0.1.34 - Category/Severity Direct Parameters

### ✨ New Features

#### Simplified Probe Selection with Direct Filtering

Added `category` and `severity` parameters directly to `create_assessment()` for streamlined probe filtering without manual `list_probes()` calls.

**New Parameters:**

```python
def create_assessment(
    model: str,
    test_types: Optional[List[str]] = None,
    preset: Optional[str] = None,
    category: Optional[str] = None,      # ⭐ NEW
    severity: Optional[str] = None,      # ⭐ NEW
    priority: Union[str, Priority] = Priority.NORMAL,
) -> Assessment:
```

**Three Selection Methods (Mutually Exclusive):**

1. **Presets** - Quick, tier-adaptive testing

   ```python
   assessment = client.create_assessment(model="x", preset="quick")
   ```

2. **Category/Severity** - Domain-specific filtering ⭐ NEW

   ```python
   # Filter by category
   assessment = client.create_assessment(model="x", category="medical_ethics")

   # Filter by severity
   assessment = client.create_assessment(model="x", severity="critical")

   # Combine both
   assessment = client.create_assessment(
       model="x",
       category="medical_ethics",
       severity="critical"
   )
   ```

3. **Manual Selection** - Full control
   ```python
   probes = client.list_probes(severity="critical")
   assessment = client.create_assessment(model="x", test_types=[p.key for p in probes.probes])
   ```

**Key Benefits:**

- ✅ **67% less code** for common filtering scenarios (3 lines → 1 line)
- ✅ **More readable** - intent is clear from parameters
- ✅ **Automatic probe fetching** - SDK handles `list_probes()` internally
- ✅ **Flexible** - use category, severity, or both together
- ✅ **Validated** - prevents mixing selection methods
- ✅ **Backward compatible** - existing code still works

**Available Categories:**

- `prompt_injection` - Injection attacks
- `jailbreaks` - System bypasses
- `pii_leaks` - Privacy violations
- `toxicity` - Harmful content
- `bias` - Discrimination
- `medical_ethics` - Healthcare (Pro+)
- `financial_compliance` - Finance (Enterprise)

**Available Severities:**

- `critical` - Fix immediately
- `high` - Fix soon
- `medium` - Monitor
- `low` - Nice to fix

**Validation Rules:**

- Must specify ONE of: `preset`, `category`/`severity`, or `test_types`
- Cannot mix selection methods
- Raises `ValueError` with clear error messages if misused

**Real-World Examples:**

```python
# Healthcare compliance
medical_test = client.create_assessment(
    model="medical-chatbot",
    category="medical_ethics",
    severity="critical"
)

# Financial security
finance_test = client.create_assessment(
    model="banking-bot",
    category="financial_compliance",
    severity="high"
)

# Quick critical scan
critical_scan = client.create_assessment(
    model="prod-model",
    severity="critical"
)
```

### 📚 Documentation Updates

- ✅ Updated Quick Start Guide with all three selection methods
- ✅ Added comprehensive Assessments API documentation
- ✅ Added 5 real-world example patterns
- ✅ Added selection method comparison table
- ✅ Enhanced Best Practices guide
- ✅ Updated parameters table with new fields

### 🔄 Migration Guide

No breaking changes! The new parameters are optional and additive:

```python
# All existing code still works
assessment = client.create_assessment(model="x", preset="quick")  # ✅
assessment = client.create_assessment(model="x", test_types=["pii_leak"])  # ✅

# Now you can also do this (simpler)
assessment = client.create_assessment(model="x", category="toxicity")  # ✅ NEW
assessment = client.create_assessment(model="x", severity="critical")  # ✅ NEW
```

---

## v0.1.28 - Complete Provider Support

### ✨ New Features

#### Complete Provider Coverage

Added missing provider support to match API capabilities. The SDK now supports **all 10 providers**!

**New Enum Values:**

- `ModelProvider.GROK` - xAI Grok models
- `ModelProvider.OPENROUTER` - OpenRouter unified API

**New ProviderConfig Helper Methods:**

1. **`ProviderConfig.huggingface()`** - HuggingFace models

   ```python
   config = ProviderConfig.huggingface(
       model_name="meta-llama/Llama-2-7b-chat-hf",
       api_key="hf_...",  # Optional for public models
       use_inference_api=True,
       endpoint_url="https://api-inference.huggingface.co/models",
       task="text-generation"
   )
   ```

2. **`ProviderConfig.rest()`** - Custom REST APIs

   ```python
   config = ProviderConfig.rest(
       uri="https://api.example.com/generate",
       api_key="your-key",
       method="POST",
       headers={"Content-Type": "application/json"},
       req_template_json_object={"prompt": "$INPUT", "max_tokens": 100},
       response_json_field="text"
   )
   ```

3. **`ProviderConfig.bedrock()`** - AWS Bedrock

   ```python
   config = ProviderConfig.bedrock(
       region="us-east-1",
       model_id="anthropic.claude-v2",
       access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
       secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
       temperature=0,
       max_tokens=1024
   )
   ```

4. **`ProviderConfig.sagemaker()`** - AWS SageMaker
   ```python
   config = ProviderConfig.sagemaker(
       region="us-west-2",
       endpoint_name="my-model-endpoint",
       access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
       secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
       request_json_template={"inputs": "$INPUT"}
   )
   ```

### 📋 Complete Provider List

The SDK now supports all these providers with full type safety and helper methods:

1. ✅ **OpenAI** - `ProviderConfig.openai()`
2. ✅ **Anthropic** - `ProviderConfig.anthropic()`
3. ✅ **Azure OpenAI** - `ProviderConfig.azure()`
4. ✅ **HuggingFace** - `ProviderConfig.huggingface()` ⭐ NEW
5. ✅ **Custom REST API** - `ProviderConfig.rest()` ⭐ NEW
6. ✅ **AWS Bedrock** - `ProviderConfig.bedrock()` ⭐ NEW
7. ✅ **AWS SageMaker** - `ProviderConfig.sagemaker()` ⭐ NEW
8. ✅ **Google Gemini** - `ProviderConfig.google()`
9. ✅ **Grok (xAI)** - `ProviderConfig.grok()`
10. ✅ **OpenRouter** - `ProviderConfig.openrouter()`

### 🎯 Benefits

- **Full IDE Autocomplete**: All providers now in `ModelProvider` enum
- **Type Safety**: Helper methods ensure correct configuration structure
- **Better DX**: No more manual dict construction for complex providers
- **API Parity**: SDK now matches 100% of API provider capabilities

### 📦 Installation

```bash
pip install --upgrade modelred
```

---

## v0.1.27 - Enhanced Model Pagination & Filtering

### ✨ New Features

#### Advanced Model Listing with Pagination

The `list_models()` method now supports comprehensive pagination, filtering, searching, and sorting capabilities.

**New Parameters:**

- `page` (int, default: 1): Page number for pagination
- `page_size` (int, default: 100, max: 100): Number of models per page
- `search` (str, optional): Search term for filtering by model name or ID
- `provider` (str, optional): Filter by provider (openai, anthropic, azure, huggingface, rest, bedrock, sagemaker, google, grok, openrouter)
- `status` (str, optional): Filter by status ('active', 'inactive', 'both')
- `sort_by` (str, optional): Sort field (displayName, provider, modelId, modelName, isActive, testCount, lastTested, createdAt)
- `sort_dir` (str, optional): Sort direction ('asc' or 'desc')

**New Return Type:**

- `ModelList` dataclass containing:
  - `models`: List of Model objects
  - `page`: Current page number
  - `pageSize`: Items per page
  - `total`: Total number of models
  - `totalPages`: Total number of pages

**Example Usage:**

```python
from modelred import ModelRed

client = ModelRed(api_key="mr_your_key")

# Get first page of active OpenAI models
result = client.list_models(
    page=1,
    page_size=20,
    provider="openai",
    status="active",
    sort_by="displayName",
    sort_dir="asc"
)

print(f"Found {result.total} models")
print(f"Showing page {result.page}/{result.totalPages}")

for model in result.models:
    print(f"- {model.displayName} ({model.provider})")

# Search for specific models
gpt_models = client.list_models(search="gpt", provider="openai")
```

### 🔄 Breaking Changes

**⚠️ `list_models()` now returns `ModelList` instead of `List[Model]`**

If you were previously using:

```python
models = client.list_models()
for model in models:  # ❌ This will break
    print(model.displayName)
```

Update to:

```python
result = client.list_models()
for model in result.models:  # ✅ Access via .models property
    print(model.displayName)
```

Or get all models at once (legacy behavior):

```python
result = client.list_models(page_size=100)
all_models = result.models
```

### 📦 Installation

```bash
pip install --upgrade modelred
```

---

# ModelRed Python SDK v0.1.25 - Subscription Tier Enforcement

## 🔒 Breaking Change: SDK Access Restricted to Pro & Enterprise Tiers

This version implements server-side enforcement of subscription tier requirements. The ModelRed SDK is now **only available for Pro and Enterprise subscription plans**.

### What Changed

#### ❌ Free & Starter Tiers - SDK Access Disabled

- API key authentication will be **rejected** with a 403 Forbidden error
- Error message: `"API key access is only available on Pro and Enterprise plans. Please upgrade your subscription to use the ModelRed SDK."`
- Users on Free/Starter plans must upgrade to Pro or Enterprise to use the SDK

#### ✅ Pro & Enterprise Tiers - Full SDK Access

- API key authentication works normally
- All SDK features available
- Automatic probe filtering based on subscription tier

### Why This Change?

1. **Business Model Alignment**: SDK access is a premium feature for paying customers
2. **Fair Usage**: Ensures API resources are available for Pro/Enterprise users
3. **Security**: Server-side enforcement prevents bypassing restrictions
4. **Clarity**: Clear separation between web UI (all tiers) and SDK (Pro+ only)

## 📦 Installation

```bash
pip install --upgrade modelred
```

## ⚠️ Migration Guide

### If you're on Free or Starter tier:

```python
from modelred import ModelRed

client = ModelRed(api_key="mr_your_key")
# ❌ Will now fail with:
# AuthorizationError: API key access is only available on Pro and
# Enterprise plans. Please upgrade your subscription to use the ModelRed SDK.
```

**Solution**: Upgrade your subscription to Pro or Enterprise at https://app.modelred.ai/settings

### If you're on Pro or Enterprise tier:

No changes needed! Your SDK will continue to work exactly as before:

```python
from modelred import ModelRed, ModelProvider, ProviderConfig
import os

# ✅ Works perfectly on Pro/Enterprise
client = ModelRed(api_key=os.environ["MODELRED_API_KEY"])

model = client.create_model(
    modelId="my-gpt4",
    provider=ModelProvider.OPENAI,
    displayName="GPT-4o Mini",
    providerConfig=ProviderConfig.openai(
        api_key=os.environ["OPENAI_API_KEY"],
        model_name="gpt-4o-mini"
    )
)

# Probes are automatically filtered by your tier
probes = client.list_probes()  # Returns pro/enterprise probes only
```

## 🔄 Server-Side Changes (Backend)

The enforcement is implemented in three API routes:

### 1. `/api/models` - Model Management

- ✅ Session authentication (web UI): Works for all tiers
- ✅ API key authentication (SDK): **Pro/Enterprise only**
- Added tier check after API key validation
- Returns 403 if tier is "free" or "starter"

### 2. `/api/assessments` - Assessment Creation

- ✅ Session authentication (web UI): Works for all tiers
- ✅ API key authentication (SDK): **Pro/Enterprise only**
- Added tier check after API key validation
- Returns 403 if tier is "free" or "starter"

### 3. `/api/probes` - Probe Discovery

- ✅ Session authentication (web UI): Works for all tiers
- ✅ API key authentication (SDK): **Pro/Enterprise only**
- Added tier check after API key validation
- **Automatic probe filtering**: SDK users only see probes in their subscription tier
  - Pro tier: `free`, `starter`, `pro` probes
  - Enterprise tier: `free`, `starter`, `pro`, `enterprise` probes

## 🛡️ Error Handling

### 403 Forbidden - Tier Restriction

```python
from modelred import ModelRed, AuthorizationError

try:
    client = ModelRed(api_key="mr_free_tier_key")
    client.create_model(...)
except AuthorizationError as e:
    print(e)  # "API key access is only available on Pro and Enterprise plans..."
    # Upgrade at: https://app.modelred.ai/settings
```

### Other Errors Remain Unchanged

```python
from modelred import (
    AuthenticationError,  # Invalid API key
    ValidationError,      # Invalid parameters
    NotFoundError,        # Resource not found
    ConflictError,        # Duplicate resource
)
```

## 📊 Subscription Tier Comparison

| Feature           | Free      | Starter         | Pro                     | Enterprise |
| ----------------- | --------- | --------------- | ----------------------- | ---------- |
| Web UI Access     | ✅        | ✅              | ✅                      | ✅         |
| SDK Access        | ❌        | ❌              | ✅                      | ✅         |
| Models            | 2         | 3               | 5                       | Unlimited  |
| Assessments/month | Unlimited | Unlimited       | Unlimited               | Unlimited  |
| Probe Access      | Basic     | Basic + Starter | All (except Enterprise) | All        |

## 🔧 Technical Details

### Authentication Flow

```
┌─────────────────┐
│  SDK Request    │
│ (API Key Auth)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Validate API Key│ ── Key invalid? ──> 401 Unauthorized
└────────┬────────┘
         │ Key valid
         ▼
┌─────────────────┐
│ Check Org Tier  │
└────────┬────────┘
         │
         ├── Free/Starter? ──> 403 Forbidden
         │
         └── Pro/Enterprise? ──> ✅ Allow Request
                                   │
                                   ▼
                          ┌─────────────────┐
                          │ Filter Probes   │
                          │ by Tier         │
                          └─────────────────┘
```

## 📚 Documentation

- [ModelRed Pricing](https://modelred.ai/pricing)
- [API Documentation](https://docs.modelred.ai)
- [Upgrade Guide](https://app.modelred.ai/settings)

---

**Version**: 0.1.25  
**Release Date**: 2025-01-08  
**Breaking Changes**: Yes (tier-based access control)

# ModelRed Python SDK v0.1.24 - Security Update

## 🔒 Security Improvements

This version includes major security enhancements to protect users from potential misuse:

### 1. **Locked Base URL**

- ✅ `base_url` parameter **removed** from `ModelRed()` and `AsyncModelRed()` constructors
- ✅ Base URL only configurable via `MODELRED_BASE_URL` environment variable
- ✅ Prevents malicious code from redirecting API traffic
- ✅ Production URL (`https://app.modelred.ai`) is the default

```python
# ❌ OLD (INSECURE - removed in v0.1.24)
client = ModelRed(api_key="...", base_url="https://evil.com")

# ✅ NEW (SECURE)
client = ModelRed(api_key="...")  # Uses production URL

# For local development only:
# export MODELRED_BASE_URL=http://localhost:3000/api
```

### 2. **DELETE Operations Disabled**

- ✅ `delete_model()` method **removed** from public API
- ✅ `delete_assessment()` method **removed** from public API
- ✅ Prevents accidental or malicious deletion of resources
- ✅ Models persist for reuse across assessments

```python
# ❌ OLD (removed in v0.1.24)
client.delete_model("my-model")  # No longer available

# ✅ NEW - Models are permanent resources
model = client.create_model(...)  # Create once
model = client.get_model("...")   # Reuse many times
```

### 3. **Automatic Tier-Based Probe Filtering**

- ✅ `get_probes()` renamed to `list_probes()`
- ✅ `tier` parameter **removed** - automatically determined server-side
- ✅ Users can only access probes included in their subscription
- ✅ Category filtering still supported

```python
# ❌ OLD (removed in v0.1.24)
probes = client.get_probes(tier="enterprise")  # Could try to access restricted tiers

# ✅ NEW (SECURE)
probes = client.list_probes()  # Automatically filtered by your subscription tier
medical_probes = client.list_probes(category="medical_ethics")  # Category filter OK
```

### 4. **Enhanced Provider Configurations**

- ✅ Added `ProviderConfig.openrouter()` for OpenRouter API
- ✅ Added `ProviderConfig.grok()` for xAI Grok
- ✅ Improved `ProviderConfig.azure()` documentation
- ✅ Updated default models to latest versions

```python
# OpenRouter support
ProviderConfig.openrouter(
    api_key=os.environ["OPENROUTER_API_KEY"],
    model_name="anthropic/claude-3.5-sonnet"
)

# xAI Grok support
ProviderConfig.grok(
    api_key=os.environ["XAI_API_KEY"],
    model_name="grok-beta"
)

# Azure OpenAI with clear parameters
ProviderConfig.azure(
    api_key=os.environ["AZURE_OPENAI_KEY"],
    endpoint="https://YOUR_RESOURCE.openai.azure.com",
    deployment_name="gpt-4o",
    api_version="2024-06-01"
)
```

## 📦 Installation

```bash
pip install --upgrade modelred
```

## 🚀 Quick Start

```python
import os
from modelred import (
    ModelRed,
    ModelProvider,
    ProviderConfig,
    Priority,
    ConflictError,
)

# Initialize client (secure by default)
client = ModelRed(api_key=os.environ["MODELRED_API_KEY"])

# Create model with idempotent pattern
try:
    model = client.create_model(
        modelId="my-gpt4",
        provider=ModelProvider.OPENAI,
        displayName="GPT-4o Mini",
        providerConfig=ProviderConfig.openai(
            api_key=os.environ["OPENAI_API_KEY"],
            model_name="gpt-4o-mini"
        )
    )
except ConflictError:
    model = client.get_model("my-gpt4")

# List available probes (automatically filtered by your tier)
probes = client.list_probes()
probe_keys = [p.key for p in probes.probes[:3]]

# Run assessment
assessment = client.create_assessment(
    model=model.modelId,
    test_types=probe_keys,
    priority=Priority.NORMAL
)

# Wait for results
result = client.wait_for_completion(assessment.id)
print(f"Risk Level: {result.detailedReport.get('risk_level')}")

client.close()
```

## 🔄 Migration Guide (v0.1.23 → v0.1.24)

### Change 1: Remove `base_url` Parameter

```python
# Before (v0.1.23)
client = ModelRed(
    api_key="...",
    base_url="http://localhost:3000/api"  # ❌ Not allowed anymore
)

# After (v0.1.24)
# Set environment variable instead
# export MODELRED_BASE_URL=http://localhost:3000/api
client = ModelRed(api_key="...")  # ✅
```

### Change 2: Rename `get_probes()` → `list_probes()`

```python
# Before (v0.1.23)
probes = client.get_probes(tier="free")  # ❌ tier parameter removed

# After (v0.1.24)
probes = client.list_probes()  # ✅ Automatic tier filtering
```

### Change 3: Remove Delete Operations

```python
# Before (v0.1.23)
client.delete_model("my-model")  # ❌ Method removed

# After (v0.1.24)
# Models are permanent - no delete operation
# Use get_model() to reuse existing models
```

## 🛡️ Security Best Practices

1. **Never hardcode API keys** - Use environment variables
2. **Trust the default base URL** - Production URL is secure and verified
3. **Use `MODELRED_BASE_URL`** only for local development/testing
4. **Leverage automatic tier filtering** - Don't try to access restricted probes
5. **Follow idempotent patterns** - Use try/except with ConflictError

## 📚 Full Documentation

- [ModelRed Documentation](https://docs.modelred.ai)
- [API Reference](https://docs.modelred.ai/api)
- [Examples](./examples/)

## 🐛 Bug Fixes

- Fixed `KeyError: 'id'` in assessment retrieval (snake_case vs camelCase handling)
- Fixed `parse_assessment` to handle both API response formats
- Improved error messages for authentication failures

---

**Version**: 0.1.24  
**Release Date**: 2025-01-08  
**Breaking Changes**: Yes (security improvements)
