# ModelRed Python SDK Documentation

<div align="center">

![Version](https://img.shields.io/badge/version-0.1.28-blue)
![Python](https://img.shields.io/badge/python-3.6+-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

**AI Security Testing & Red Teaming Platform**

Test your LLMs against 200+ security probes covering prompt injection, jailbreaks, data leakage, and more.

[Installation](#installation) • [Quick Start](#quick-start) • [API Reference](#api-reference) • [Examples](#examples)

</div>

---

## 📚 Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Authentication](#authentication)
- [Client Initialization](#client-initialization)
- [API Reference](#api-reference)
  - [Models API](#models-api)
  - [Assessments API](#assessments-api)
  - [Probes API](#probes-api)
  - [Provider Configuration](#provider-configuration)
- [Data Models](#data-models)
- [Error Handling](#error-handling)
- [CI/CD Integration](#cicd-integration)
- [Advanced Usage](#advanced-usage)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

ModelRed SDK provides comprehensive AI security testing and red teaming capabilities for Large Language Models (LLMs). Perfect for integrating security testing into your CI/CD pipelines.

### ✨ Features

- ✅ **200+ Security Probes** - Test against prompt injection, jailbreaks, data leakage, and more
- ✅ **10 Provider Support** - OpenAI, Anthropic, Azure, Google, HuggingFace, AWS Bedrock, SageMaker, REST APIs, Grok, OpenRouter
- ✅ **Automated Testing** - CI/CD ready with progress callbacks and timeout controls
- ✅ **Async Support** - Full async/await API for high-concurrency applications
- ✅ **Comprehensive Reports** - Detailed security scores, vulnerability findings, and recommendations

---

## 📦 Installation

```bash
pip install modelred
```

### Requirements

- Python 3.6 or higher
- API key from [ModelRed Dashboard](https://app.modelred.ai)

---

## 🚀 Quick Start

```python
from modelred import ModelRed, ModelProvider, ProviderConfig
import os

# Initialize client
client = ModelRed(api_key=os.environ["MODELRED_API_KEY"])

# Register your model
model = client.create_model(
    modelId="my-gpt4",
    provider=ModelProvider.OPENAI,
    displayName="Production GPT-4",
    providerConfig=ProviderConfig.openai(
        api_key=os.environ["OPENAI_API_KEY"],
        model_name="gpt-4o-mini"
    )
)

# List available security probes
probes = client.list_probes()
test_types = [p.key for p in probes.probes[:10]]  # Select first 10

# Create security assessment
assessment = client.create_assessment(
    model="my-gpt4",
    test_types=test_types
)

# Wait for results
result = client.wait_for_completion(assessment.id)
print(f"Security Score: {result.detailedReport['overall_score']}/100")

client.close()
```

---

## 🔐 Authentication

### API Key Setup

1. Get your API key from [ModelRed Dashboard](https://app.modelred.ai/api-keys)
2. Set as environment variable:

```bash
export MODELRED_API_KEY=mr_your_api_key_here
```

### Security Best Practices

- ✅ Always use environment variables for API keys
- ✅ Never commit API keys to version control
- ✅ Rotate keys regularly
- ✅ Use separate keys for dev/staging/production

---

## 🔧 Client Initialization

### Synchronous Client

```python
from modelred import ModelRed

# Using environment variable (recommended)
client = ModelRed()

# Or pass directly
client = ModelRed(api_key="mr_your_key")

# With custom timeout
client = ModelRed(timeout=60)

# Context manager (auto-closes connection)
with ModelRed() as client:
    models = client.list_models()
    # Use client...
# Automatically closed
```

### Async Client

```python
from modelred import AsyncModelRed

async with AsyncModelRed() as client:
    model = await client.create_model(...)
    assessment = await client.create_assessment(...)
    result = await client.wait_for_completion(assessment.id)
```

### Constructor Parameters

| Parameter | Type  | Default | Description                                                     |
| --------- | ----- | ------- | --------------------------------------------------------------- |
| `api_key` | `str` | `None`  | Your ModelRed API key. Falls back to `MODELRED_API_KEY` env var |
| `timeout` | `int` | `30`    | Request timeout in seconds                                      |

---

## 📖 API Reference

### Models API

Models represent your AI systems under test. Each model has provider-specific configuration.

#### `create_model()`

Register a new model for security testing.

```python
def create_model(
    *,
    modelId: str,
    provider: ModelProvider,
    displayName: str,
    providerConfig: Dict[str, Any],
    description: Optional[str] = None
) -> Model
```

**Parameters:**

| Parameter        | Type            | Required | Description                                                           |
| ---------------- | --------------- | -------- | --------------------------------------------------------------------- |
| `modelId`        | `str`           | ✅       | Unique identifier (use lowercase with hyphens)                        |
| `provider`       | `ModelProvider` | ✅       | Provider enum (see [Provider Configuration](#provider-configuration)) |
| `displayName`    | `str`           | ✅       | Human-readable name for dashboard                                     |
| `providerConfig` | `dict`          | ✅       | Provider-specific configuration (use `ProviderConfig` helpers)        |
| `description`    | `str`           | ❌       | Optional model description                                            |

**Returns:** `Model` object

**Raises:**

- `ValidationError` - Invalid parameters
- `ConflictError` - Model with this modelId already exists
- `AuthenticationError` - Invalid API key
- `AuthorizationError` - Insufficient permissions

**Example:**

```python
from modelred import ModelRed, ModelProvider, ProviderConfig

client = ModelRed()

# OpenAI model
model = client.create_model(
    modelId="prod-gpt4",
    provider=ModelProvider.OPENAI,
    displayName="Production GPT-4",
    providerConfig=ProviderConfig.openai(
        api_key=os.environ["OPENAI_API_KEY"],
        model_name="gpt-4o-mini"
    ),
    description="Production chatbot model"
)

print(f"Created model: {model.modelId}")
```

**Idempotency:**

```python
from modelred import ConflictError

try:
    model = client.create_model(modelId="my-model", ...)
except ConflictError:
    model = client.get_model("my-model")
```

---

#### `get_model()`

Retrieve an existing model by identifier.

```python
def get_model(model_identifier: str) -> Model
```

**Parameters:**

| Parameter          | Type  | Required | Description                     |
| ------------------ | ----- | -------- | ------------------------------- |
| `model_identifier` | `str` | ✅       | Model ID or modelId to retrieve |

**Returns:** `Model` object

**Raises:**

- `NotFoundError` - Model does not exist
- `AuthenticationError` - Invalid API key

**Example:**

```python
model = client.get_model("prod-gpt4")
print(f"Model: {model.displayName}")
print(f"Tests run: {model.testCount}")
print(f"Last tested: {model.lastTested}")
```

---

#### `list_models()`

List all models with pagination and filtering support.

```python
def list_models(
    *,
    page: int = 1,
    page_size: int = 100,
    search: Optional[str] = None,
    provider: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_dir: Optional[str] = None
) -> ModelList
```

**Parameters:**

| Parameter   | Type  | Default | Description                                     |
| ----------- | ----- | ------- | ----------------------------------------------- |
| `page`      | `int` | `1`     | Page number                                     |
| `page_size` | `int` | `100`   | Models per page (max: 100)                      |
| `search`    | `str` | `None`  | Search by name or ID                            |
| `provider`  | `str` | `None`  | Filter by provider                              |
| `status`    | `str` | `None`  | Filter by status (`active`, `inactive`, `both`) |
| `sort_by`   | `str` | `None`  | Sort field (e.g., `displayName`, `createdAt`)   |
| `sort_dir`  | `str` | `None`  | Sort direction (`asc` or `desc`)                |

**Returns:** `ModelList` object containing:

- `models` - List of Model objects
- `page` - Current page number
- `pageSize` - Items per page
- `total` - Total number of models
- `totalPages` - Total number of pages

**Example:**

```python
# Get all models
result = client.list_models()
print(f"Found {result.total} models")

for model in result.models:
    print(f"• {model.displayName} ({model.provider})")

# Search and filter
result = client.list_models(
    search="gpt",
    provider="openai",
    status="active",
    sort_by="testCount",
    sort_dir="desc"
)

# Pagination
page1 = client.list_models(page=1, page_size=20)
page2 = client.list_models(page=2, page_size=20)
```

---

### Assessments API

Assessments are security test runs. Create an assessment to test your model against selected probes.

#### `create_assessment()`

Create a new security assessment.

```python
def create_assessment(
    *,
    model: str,
    test_types: List[str],
    priority: Priority = Priority.NORMAL
) -> Assessment
```

**Parameters:**

| Parameter    | Type        | Default  | Description                               |
| ------------ | ----------- | -------- | ----------------------------------------- |
| `model`      | `str`       | -        | Model ID or modelId to test               |
| `test_types` | `List[str]` | -        | List of probe keys (from `list_probes()`) |
| `priority`   | `Priority`  | `NORMAL` | Queue priority (`LOW`, `NORMAL`, `HIGH`)  |

**Returns:** `Assessment` object

**Raises:**

- `ValidationError` - Invalid parameters
- `NotFoundError` - Model does not exist
- `SubscriptionLimitError` - Exceeded concurrent assessment limit
- `AuthenticationError` - Invalid API key

**Example:**

```python
from modelred import Priority

# Get available probes
probes = client.list_probes()

# Select probes by category
injection_probes = [
    p.key for p in probes.probes
    if p.category == "prompt_injection"
]

# Create assessment
assessment = client.create_assessment(
    model="prod-gpt4",
    test_types=injection_probes,
    priority=Priority.NORMAL
)

print(f"Assessment created: {assessment.id}")
print(f"Status: {assessment.status.value}")
```

**Probe Selection Strategies:**

```python
# Quick smoke test (5-10 probes)
quick_probes = [p.key for p in probes.probes[:10]]

# By severity
critical_probes = [
    p.key for p in probes.probes
    if p.severity == "critical"
]

# By category
medical_probes = [
    p.key for p in probes.probes
    if p.category == "medical_ethics"
]

# Combined filters
critical_injection = [
    p.key for p in probes.probes
    if p.severity == "critical" and "injection" in p.category
]
```

---

#### `get_assessment()`

Check assessment status and retrieve results.

```python
def get_assessment(assessment_id: str) -> Assessment
```

**Parameters:**

| Parameter       | Type  | Required | Description                              |
| --------------- | ----- | -------- | ---------------------------------------- |
| `assessment_id` | `str` | ✅       | Assessment ID from `create_assessment()` |

**Returns:** `Assessment` object with current status and results (if completed)

**Example:**

```python
from modelred import AssessmentStatus

assessment = client.get_assessment("assess_abc123")

if assessment.status == AssessmentStatus.COMPLETED:
    print(f"Score: {assessment.detailedReport['overall_score']}")
elif assessment.status == AssessmentStatus.RUNNING:
    print(f"Progress: {assessment.progress}%")
elif assessment.status == AssessmentStatus.FAILED:
    print(f"Error: {assessment.errorMessage}")
```

---

#### `list_assessments()`

List recent assessments.

```python
def list_assessments(limit: Optional[int] = None) -> List[Assessment]
```

**Parameters:**

| Parameter | Type  | Default | Description                              |
| --------- | ----- | ------- | ---------------------------------------- |
| `limit`   | `int` | `None`  | Maximum number of assessments (optional) |

**Returns:** List of `Assessment` objects, sorted by creation date (newest first)

**Example:**

```python
# Get last 10 assessments
recent = client.list_assessments(limit=10)

for assessment in recent:
    print(f"{assessment.id}: {assessment.status.value}")
```

---

#### `wait_for_completion()`

Wait for assessment to complete, polling for status updates.

```python
def wait_for_completion(
    assessment_id: str,
    *,
    timeout_minutes: int = 60,
    poll_interval: int = 10,
    progress_callback: Optional[Callable[[Assessment], None]] = None
) -> Assessment
```

**Parameters:**

| Parameter           | Type       | Default | Description                                  |
| ------------------- | ---------- | ------- | -------------------------------------------- |
| `assessment_id`     | `str`      | -       | Assessment ID to wait for                    |
| `timeout_minutes`   | `int`      | `60`    | Max time to wait before raising TimeoutError |
| `poll_interval`     | `int`      | `10`    | Seconds between status checks                |
| `progress_callback` | `Callable` | `None`  | Function called on each status update        |

**Returns:** Completed `Assessment` object with `detailedReport` populated

**Raises:**

- `TimeoutError` - Assessment did not complete within timeout
- `NotFoundError` - Assessment does not exist

**Example:**

```python
# Simple usage
result = client.wait_for_completion("assess_abc123")
print(f"Score: {result.detailedReport['overall_score']}")

# With progress logging
def log_progress(assessment):
    print(f"[{assessment.status.value}] {assessment.progress}% complete")

result = client.wait_for_completion(
    "assess_abc123",
    timeout_minutes=30,
    poll_interval=5,
    progress_callback=log_progress
)

# CI/CD usage with threshold
result = client.wait_for_completion(assessment.id)
score = result.detailedReport['overall_score']

if score < 80:
    print(f"❌ Security score too low: {score}/100")
    sys.exit(1)
else:
    print(f"✅ Security score passed: {score}/100")
```

---

### Probes API

Probes are security tests that check for specific vulnerabilities.

#### `list_probes()`

List all security probes available for your subscription tier.

```python
def list_probes(
    *,
    category: Optional[str] = None
) -> ProbesIndex
```

**Parameters:**

| Parameter  | Type  | Default | Description                   |
| ---------- | ----- | ------- | ----------------------------- |
| `category` | `str` | `None`  | Filter by category (optional) |

**Available Categories:**

- `universal` - Basic security tests (all tiers)
- `prompt_injection` - Injection attacks
- `jailbreak` - Jailbreak attempts
- `data_leakage` - Information disclosure
- `medical_ethics` - Healthcare compliance (Pro+)
- `legal_ethics` - Legal compliance (Pro+)
- `financial_compliance` - Financial regulations (Enterprise)
- `cyber_operations` - Advanced attacks (Enterprise)

**Returns:** `ProbesIndex` object with:

- `probes` - List of `Probe` objects
- `probe_categories` - List of available categories
- `tier_definitions` - Dict of tier information

**Example:**

```python
# Get all available probes
probes_index = client.list_probes()
print(f"Available probes: {len(probes_index.probes)}")
print(f"Categories: {', '.join(probes_index.probe_categories)}")

# Get probes by category
medical = client.list_probes(category="medical_ethics")
print(f"Medical ethics probes: {len(medical.probes)}")

# Display probe details
for probe in probes_index.probes[:5]:
    print(f"\n• {probe.display_name}")
    print(f"  Key: {probe.key}")
    print(f"  Category: {probe.category}")
    print(f"  Severity: {probe.severity}")
    print(f"  Description: {probe.description}")
```

**Tier Information:**

| Tier       | Probes | Description                        |
| ---------- | ------ | ---------------------------------- |
| Free       | ~30    | Universal probes                   |
| Pro        | ~100   | Universal + specialized categories |
| Enterprise | 200+   | All categories including advanced  |

> 🔒 **Note:** Tier filtering is enforced server-side. You can only access probes available in your subscription tier.

---

### Provider Configuration

The `ProviderConfig` class provides helper methods to create provider-specific configurations.

#### OpenAI

```python
@staticmethod
def openai(
    api_key: str,
    model_name: str = "gpt-4o-mini",
    organization: Optional[str] = None
) -> Dict[str, Any]
```

**Supported Models:** `gpt-4o`, `gpt-4o-mini`, `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`

```python
config = ProviderConfig.openai(
    api_key=os.environ["OPENAI_API_KEY"],
    model_name="gpt-4o-mini"
)
```

---

#### Anthropic

```python
@staticmethod
def anthropic(
    api_key: str,
    model_name: str = "claude-3-5-sonnet-20241022"
) -> Dict[str, Any]
```

**Supported Models:** `claude-3-5-sonnet-20241022`, `claude-3-5-haiku-20241022`, `claude-3-opus-20240229`

```python
config = ProviderConfig.anthropic(
    api_key=os.environ["ANTHROPIC_API_KEY"],
    model_name="claude-3-5-sonnet-20241022"
)
```

---

#### Azure OpenAI

```python
@staticmethod
def azure(
    api_key: str,
    endpoint: str,
    deployment_name: str,
    api_version: str = "2024-06-01"
) -> Dict[str, Any]
```

```python
config = ProviderConfig.azure(
    api_key=os.environ["AZURE_OPENAI_KEY"],
    endpoint="https://my-resource.openai.azure.com",
    deployment_name="gpt-4-deployment"
)
```

---

#### Google Gemini

```python
@staticmethod
def google(
    api_key: str,
    model_name: str,
    *,
    generation_config: Optional[Dict[str, Any]] = None,
    safety_settings: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]
```

**Supported Models:** `gemini-2.0-flash-exp`, `gemini-1.5-pro`, `gemini-1.5-flash`

```python
config = ProviderConfig.google(
    api_key=os.environ["GOOGLE_API_KEY"],
    model_name="gemini-2.0-flash-exp",
    generation_config={
        "temperature": 0.7,
        "max_output_tokens": 1024
    }
)
```

---

#### HuggingFace

```python
@staticmethod
def huggingface(
    model_name: str,
    api_key: str = "",
    *,
    use_inference_api: bool = True,
    endpoint_url: str = "https://api-inference.huggingface.co/models",
    task: str = "text-generation"
) -> Dict[str, Any]
```

```python
config = ProviderConfig.huggingface(
    model_name="meta-llama/Llama-2-7b-chat-hf",
    api_key=os.environ.get("HUGGINGFACE_TOKEN", ""),
    use_inference_api=True
)
```

---

#### Custom REST API

```python
@staticmethod
def rest(
    uri: str,
    *,
    api_key: Optional[str] = None,
    method: str = "POST",
    headers: Optional[Dict[str, str]] = None,
    req_template: str = "$INPUT",
    req_template_json_object: Optional[Dict[str, Any]] = None,
    response_json: bool = True,
    response_json_field: str = "text",
    request_timeout: int = 20
) -> Dict[str, Any]
```

```python
config = ProviderConfig.rest(
    uri="https://api.example.com/generate",
    api_key="your-api-key",
    headers={"Content-Type": "application/json"},
    req_template_json_object={
        "prompt": "$INPUT",
        "max_tokens": 100
    },
    response_json_field="generated_text"
)
```

---

#### AWS Bedrock

```python
@staticmethod
def bedrock(
    region: str,
    model_id: str,
    access_key_id: str,
    secret_access_key: str,
    *,
    session_token: Optional[str] = None,
    temperature: float = 0,
    max_tokens: int = 1024
) -> Dict[str, Any]
```

```python
config = ProviderConfig.bedrock(
    region="us-east-1",
    model_id="anthropic.claude-v2",
    access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"]
)
```

---

#### AWS SageMaker

```python
@staticmethod
def sagemaker(
    region: str,
    endpoint_name: str,
    access_key_id: str,
    secret_access_key: str,
    *,
    request_json_template: Optional[Dict[str, Any]] = None,
    response_json_field: str = "generated_text",
    timeout_ms: int = 20000
) -> Dict[str, Any]
```

```python
config = ProviderConfig.sagemaker(
    region="us-west-2",
    endpoint_name="my-llm-endpoint",
    access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    request_json_template={"inputs": "$INPUT"}
)
```

---

#### Grok (xAI)

```python
@staticmethod
def grok(
    api_key: str,
    model_name: str = "grok-beta"
) -> Dict[str, Any]
```

```python
config = ProviderConfig.grok(
    api_key=os.environ["XAI_API_KEY"],
    model_name="grok-beta"
)
```

---

#### OpenRouter

```python
@staticmethod
def openrouter(
    api_key: str,
    model_name: str,
    base_url: str = "https://openrouter.ai/api/v1"
) -> Dict[str, Any]
```

**Supported Models:** 100+ models including:

- `anthropic/claude-3.5-sonnet`
- `google/gemini-pro-1.5`
- `meta-llama/llama-3.1-70b-instruct`

```python
config = ProviderConfig.openrouter(
    api_key=os.environ["OPENROUTER_API_KEY"],
    model_name="anthropic/claude-3.5-sonnet"
)
```

---

## 📊 Data Models

### Model

Represents a registered AI model.

```python
@dataclass
class Model:
    id: str                     # Database ID
    modelId: str                # Your unique identifier
    provider: str               # Provider name
    modelName: Optional[str]    # Provider's model name
    displayName: str            # Human-readable name
    description: Optional[str]  # Description
    isActive: bool              # Active status
    lastTested: Optional[datetime]  # Last assessment date
    testCount: int              # Number of assessments
    createdAt: Optional[datetime]   # Creation timestamp
    updatedAt: Optional[datetime]   # Last update timestamp
```

---

### Assessment

Represents a security assessment run.

```python
@dataclass
class Assessment:
    id: str                     # Assessment unique ID
    modelId: str                # Model being tested
    status: AssessmentStatus    # Current status
    testTypes: List[str]        # Probe keys
    priority: Priority          # Priority level
    progress: int               # Completion % (0-100)
    createdAt: Optional[datetime]       # Creation timestamp
    completedAt: Optional[datetime]     # Completion timestamp
    detailedReport: Optional[Dict]      # Results (when completed)
    errorMessage: Optional[str]         # Error details (when failed)
```

#### Detailed Report Structure

```python
{
    "overall_score": 85,        # 0-100 security score
    "risk_level": "medium",     # low, medium, high, critical
    "total_tests": 50,
    "passed_tests": 42,
    "failed_tests": 8,
    "probes": [
        {
            "key": "reverse_psychology",
            "displayName": "Reverse Psychology",
            "category": "prompt_injection",
            "severity": "high",
            "total_cases": 10,
            "passed_cases": 8,
            "failed_cases": 2,
            "pass_rate": 80.0,
            "findings": [...]
        }
    ],
    "vulnerabilities": [
        {
            "probe": "data_leakage_01",
            "severity": "critical",
            "description": "Model leaked training data",
            "recommendation": "Implement output filtering"
        }
    ]
}
```

---

### Probe

Represents a security test probe.

```python
@dataclass
class Probe:
    key: str                    # Unique identifier
    display_name: str           # Human-readable name
    description: str            # What the probe tests
    category: str               # Probe category
    severity: str               # low, medium, high, critical
    tier: str                   # Required subscription tier
    tags: List[str]             # Related tags
```

---

### ModelProvider (Enum)

```python
class ModelProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
    GOOGLE = "google"
    HUGGINGFACE = "huggingface"
    REST = "rest"
    BEDROCK = "bedrock"
    SAGEMAKER = "sagemaker"
    GROK = "grok"
    OPENROUTER = "openrouter"
```

---

### AssessmentStatus (Enum)

```python
class AssessmentStatus(Enum):
    QUEUED = "queued"           # Waiting to start
    RUNNING = "running"         # Currently executing
    COMPLETED = "completed"     # Successfully finished
    FAILED = "failed"           # Error occurred
    CANCELLED = "cancelled"     # User cancelled
```

---

### Priority (Enum)

```python
class Priority(Enum):
    LOW = "low"                 # Background processing
    NORMAL = "normal"           # Standard queue (default)
    HIGH = "high"               # Prioritized (premium tiers)
```

---

## 🚨 Error Handling

### Exception Hierarchy

All exceptions inherit from `ModelRedError` base class.

```python
from modelred import (
    ModelRedError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ConflictError,
    RateLimitError,
    SubscriptionLimitError,
    ServerError,
    NetworkError
)
```

### Exception Types

| Exception                | HTTP Status | Description                 |
| ------------------------ | ----------- | --------------------------- |
| `ValidationError`        | 400, 422    | Invalid request parameters  |
| `AuthenticationError`    | 401         | Invalid or missing API key  |
| `AuthorizationError`     | 403         | Insufficient permissions    |
| `NotFoundError`          | 404         | Resource does not exist     |
| `ConflictError`          | 409         | Resource already exists     |
| `RateLimitError`         | 429         | API rate limit exceeded     |
| `SubscriptionLimitError` | 403         | Subscription limit reached  |
| `ServerError`            | 5xx         | Internal server error       |
| `NetworkError`           | -           | Network connectivity issues |

### Best Practices

```python
from modelred import (
    ModelRed,
    ValidationError,
    ConflictError,
    SubscriptionLimitError,
    NetworkError
)

try:
    client = ModelRed()

    # Handle duplicate models
    try:
        model = client.create_model(modelId="my-model", ...)
    except ConflictError:
        model = client.get_model("my-model")

    # Handle subscription limits
    try:
        assessment = client.create_assessment(...)
    except SubscriptionLimitError:
        print("Too many concurrent assessments, waiting...")
        time.sleep(60)
        assessment = client.create_assessment(...)

    result = client.wait_for_completion(assessment.id)

except ValidationError as e:
    print(f"Invalid request: {e}")
except AuthenticationError:
    print("Invalid API key")
except NetworkError as e:
    print(f"Network error: {e}")
finally:
    client.close()
```

---

## 🔄 CI/CD Integration

### GitHub Actions

```yaml
name: AI Security Testing

on: [push, pull_request]

jobs:
  security-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.9"

      - name: Install dependencies
        run: pip install modelred

      - name: Run security assessment
        env:
          MODELRED_API_KEY: ${{ secrets.MODELRED_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: python security_test.py
```

### Jenkins

```groovy
pipeline {
    agent any
    environment {
        MODELRED_API_KEY = credentials('modelred-api-key')
        OPENAI_API_KEY = credentials('openai-api-key')
    }
    stages {
        stage('Security Test') {
            steps {
                sh '''
                    pip install modelred
                    python security_test.py
                '''
            }
        }
    }
}
```

### GitLab CI

```yaml
security-test:
  image: python:3.9
  script:
    - pip install modelred
    - python security_test.py
  variables:
    MODELRED_API_KEY: $MODELRED_API_KEY
    OPENAI_API_KEY: $OPENAI_API_KEY
```

### CI/CD Test Script

```python
#!/usr/bin/env python3
"""CI/CD security testing script."""

import os
import sys
from modelred import (
    ModelRed,
    ModelProvider,
    ProviderConfig,
    ConflictError,
    AssessmentStatus
)

def main():
    client = ModelRed()

    # Register model (or use existing)
    try:
        model = client.create_model(
            modelId="ci-model",
            provider=ModelProvider.OPENAI,
            displayName="CI Test Model",
            providerConfig=ProviderConfig.openai(
                api_key=os.environ["OPENAI_API_KEY"],
                model_name="gpt-4o-mini"
            )
        )
        print(f"✓ Model registered: {model.modelId}")
    except ConflictError:
        model = client.get_model("ci-model")
        print(f"✓ Using existing model: {model.modelId}")

    # Get critical probes
    probes = client.list_probes()
    critical_probes = [
        p.key for p in probes.probes
        if p.severity == "critical"
    ][:10]

    print(f"✓ Running {len(critical_probes)} critical security probes")

    # Create assessment
    assessment = client.create_assessment(
        model="ci-model",
        test_types=critical_probes
    )
    print(f"✓ Assessment started: {assessment.id}")

    # Wait for completion with progress
    def log_progress(a):
        print(f"  [{a.status.value}] {a.progress}% complete")

    result = client.wait_for_completion(
        assessment.id,
        timeout_minutes=30,
        poll_interval=10,
        progress_callback=log_progress
    )

    # Check results
    if result.status == AssessmentStatus.COMPLETED:
        report = result.detailedReport
        score = report['overall_score']
        risk = report['risk_level']

        print(f"\n{'='*60}")
        print(f"Security Score: {score}/100")
        print(f"Risk Level: {risk.upper()}")
        print(f"Tests: {report['passed_tests']}/{report['total_tests']} passed")
        print(f"{'='*60}\n")

        # Fail CI if score too low
        THRESHOLD = 70
        if score < THRESHOLD:
            print(f"❌ FAILED: Score {score} below threshold {THRESHOLD}")
            sys.exit(1)
        else:
            print(f"✅ PASSED: Score {score} meets threshold {THRESHOLD}")
            sys.exit(0)
    else:
        print(f"❌ Assessment failed: {result.errorMessage}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## 🚀 Advanced Usage

### Async Client

For high-concurrency applications or async frameworks (FastAPI, aiohttp):

```python
import asyncio
from modelred import AsyncModelRed, ModelProvider, ProviderConfig

async def run_security_test():
    async with AsyncModelRed() as client:
        # All methods are async and must be awaited
        model = await client.create_model(
            modelId="async-model",
            provider=ModelProvider.OPENAI,
            displayName="Async Model",
            providerConfig=ProviderConfig.openai(
                api_key=os.environ["OPENAI_API_KEY"],
                model_name="gpt-4o-mini"
            )
        )

        probes = await client.list_probes()
        test_types = [p.key for p in probes.probes[:10]]

        assessment = await client.create_assessment(
            model="async-model",
            test_types=test_types
        )

        result = await client.wait_for_completion(assessment.id)
        return result

# Run in event loop
result = asyncio.run(run_security_test())
```

### Parallel Assessments

Test multiple models concurrently:

```python
from modelred import ModelRed
import concurrent.futures

def test_model(model_id, test_types):
    client = ModelRed()
    assessment = client.create_assessment(
        model=model_id,
        test_types=test_types
    )
    result = client.wait_for_completion(assessment.id)
    client.close()
    return result

models = ["model-a", "model-b", "model-c"]
probes = client.list_probes()
test_types = [p.key for p in probes.probes[:10]]

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(test_model, m, test_types) for m in models]
    results = [f.result() for f in futures]
```

### Custom Progress Tracking

```python
from datetime import datetime

class ProgressTracker:
    def __init__(self, assessment_id):
        self.assessment_id = assessment_id
        self.start_time = datetime.now()
        self.last_progress = 0

    def __call__(self, assessment):
        elapsed = (datetime.now() - self.start_time).seconds
        progress_delta = assessment.progress - self.last_progress

        # Estimate time remaining
        if progress_delta > 0:
            rate = progress_delta / 10  # per poll interval
            remaining = (100 - assessment.progress) / rate * 10
            print(f"Progress: {assessment.progress}% (est. {remaining}s remaining)")

        self.last_progress = assessment.progress

tracker = ProgressTracker(assessment.id)
result = client.wait_for_completion(
    assessment.id,
    progress_callback=tracker
)
```

---

## ✅ Best Practices

### 1. API Key Management

- ✅ Always use environment variables
- ✅ Never commit keys to version control
- ✅ Rotate keys regularly
- ✅ Use separate keys for dev/staging/prod

### 2. Model Registration

- ✅ Use descriptive modelId (e.g., `production-gpt4`)
- ✅ Handle `ConflictError` for idempotency
- ✅ Set meaningful displayName

### 3. Probe Selection

- ✅ Start with critical severity probes
- ✅ Filter by relevant categories
- ✅ Quick tests in CI (10-20 probes)
- ✅ Full tests nightly (all probes)

### 4. Assessment Management

- ✅ Use `wait_for_completion()` for synchronous testing
- ✅ Set reasonable timeouts (5-30 minutes typical)
- ✅ Implement progress callbacks for long tests
- ✅ Check subscription limits

### 5. Error Handling

- ✅ Wrap API calls in try/except blocks
- ✅ Handle `ConflictError` for idempotent operations
- ✅ Retry on `NetworkError` with backoff
- ✅ Log errors for debugging

### 6. CI/CD Integration

- ✅ Use exit codes for pass/fail
- ✅ Set appropriate security thresholds
- ✅ Store secrets in CI vault
- ✅ Run quick tests on commits, full tests nightly

### 7. Performance

- ✅ Close client when done (or use context manager)
- ✅ Reuse models across assessments
- ✅ Use appropriate poll intervals
- ✅ Consider async client for high concurrency

---

## 🔍 Troubleshooting

### AuthenticationError: Invalid API key

**Solutions:**

1. Verify API key at [Dashboard](https://app.modelred.ai/api-keys)
2. Check environment variable: `echo $MODELRED_API_KEY`
3. Remove whitespace: `MODELRED_API_KEY="$(cat key.txt | tr -d '\n')"`

---

### NetworkError: Connection refused

**Solutions:**

1. Check internet connection
2. Verify `MODELRED_BASE_URL` is unset (or correct for dev)
3. Check firewall/proxy settings

---

### SubscriptionLimitError: Maximum concurrent assessments

**Solutions:**

1. Wait for existing assessments to complete
2. Upgrade subscription tier
3. List running assessments: `client.list_assessments()`

---

### ConflictError: Model already exists

**Solution:**

```python
try:
    model = client.create_model(...)
except ConflictError:
    model = client.get_model(modelId)
```

---

### TimeoutError: Assessment did not complete

**Solutions:**

1. Increase timeout: `wait_for_completion(timeout_minutes=120)`
2. Check status manually: `client.get_assessment(id)`
3. Contact support if stuck

---

### ValidationError: Invalid test_types

**Solutions:**

1. Verify probe keys: `probes = client.list_probes()`
2. Check for typos
3. Ensure probes available in your tier

---

## 🌐 Environment Variables

| Variable                 | Required | Default        | Description                     |
| ------------------------ | -------- | -------------- | ------------------------------- |
| `MODELRED_API_KEY`       | ✅       | -              | Your ModelRed API key           |
| `MODELRED_BASE_URL`      | ❌       | Production URL | API base URL (dev only)         |
| `MODELRED_TIMEOUT`       | ❌       | `30`           | Request timeout (seconds)       |
| `MODELRED_MAX_RETRIES`   | ❌       | `3`            | Max retry attempts              |
| `MODELRED_RETRY_BACKOFF` | ❌       | `0.5`          | Initial backoff delay (seconds) |

---

## 📚 Resources

### Documentation

- 📖 [Main Docs](https://docs.modelred.ai)
- 🔗 [API Reference](https://docs.modelred.ai/api)
- 🔬 [Probe Catalog](https://app.modelred.ai/probes)

### Support

- 📧 Email: support@modelred.ai
- 💬 Discord: [Join Community](https://discord.gg/modelred)
- 🐛 GitHub: [Report Issues](https://github.com/modelred/python-sdk/issues)

### Links

- 🌐 [Dashboard](https://app.modelred.ai)
- 🔑 [API Keys](https://app.modelred.ai/api-keys)
- 📦 [PyPI Package](https://pypi.org/project/modelred)
- 💻 [Source Code](https://github.com/modelred/python-sdk)
- 📝 [Changelog](https://github.com/modelred/python-sdk/blob/main/CHANGELOG.md)

---

<div align="center">

**Built with ❤️ by the ModelRed Team**

[Website](https://modelred.ai) • [Dashboard](https://app.modelred.ai) • [GitHub](https://github.com/modelred)

</div>
