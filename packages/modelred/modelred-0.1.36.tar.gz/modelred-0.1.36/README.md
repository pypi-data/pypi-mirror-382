# ModelRed Python SDK

[![PyPI version](https://badge.fury.io/py/modelred.svg)](https://badge.fury.io/py/modelred)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Production-ready Python SDK for the **ModelRed** AI security testing platform. Register models, run red-team style security assessments, and retrieve standardized probe catalogs — with both synchronous and asynchronous APIs.

---

## Highlights

- **Two clients**: `ModelRed` (sync) and `AsyncModelRed` (async)
- **New modular clients**: `ModelRedClient` / `AsyncModelRedClient` expose the refactored resource services
- **Simple auth**: API key header; no extra plumbing required
- **Model registry**: One-line helpers for popular providers
- **Assessments**: Create, poll, and fetch detailed results
- **Probes API**: Discover probe keys, categories, tiers, and severities
- **Typed errors**: Precise exceptions with structured response data
- **Zero config URLs**: No endpoint juggling — just use the SDK

---

## Installation

```bash
pip install modelred
Python 3.8+ is supported. The SDK uses requests for sync and aiohttp for async.

Authentication
Create an API key in the ModelRed dashboard and either export it:

bash
Copy code
export MODELRED_API_KEY="mr_your_api_key"
or provide it to the client:

python
Copy code
from modelred_sdk import ModelRed
client = ModelRed(api_key="mr_your_api_key")
Quick Start
1) Register a model
python
Copy code
from modelred_sdk import ModelRed, ModelProvider, ProviderConfig

client = ModelRed()

cfg = ProviderConfig.openai(
    api_key="sk-openai",
    model_name="gpt-4o-mini",
)

model = client.create_model(
    modelId="cust-support-prod",     # your human-friendly slug, unique in your workspace
    provider=ModelProvider.OPENAI,
    displayName="Customer Support (Prod)",
    providerConfig=cfg,
    description="Production support model",
)

print(model.id, model.modelId, model.provider, model.modelName)
2) Run an assessment
python
Copy code
from modelred_sdk import Priority

assessment = client.create_assessment(
    model="cust-support-prod",       # use the slug OR the DB id
    test_types=["jailbreak", "prompt_injection"],
    priority=Priority.HIGH,
)

print(assessment.id, assessment.status.value)
3) Wait for completion with progress
python
Copy code
def on_progress(a):
    print(f"[{a.id}] {a.status.value} {a.progress}%")

final = client.wait_for_completion(
    assessment_id=assessment.id,
    timeout_minutes=45,
    poll_interval=10,
    progress_callback=on_progress,
)

print("Final:", final.status.value)
print("Failed tests:", (final.results or {}).get("failed_tests"))
Async Usage
python
Copy code
import asyncio
from modelred_sdk import AsyncModelRed, ModelProvider, ProviderConfig, Priority

async def main():
    async with AsyncModelRed() as client:
        cfg = ProviderConfig.anthropic(
            api_key="sk-ant",
            model_name="claude-3-sonnet-20240229",
        )

        model = await client.create_model(
            modelId="claude-support",
            provider=ModelProvider.ANTHROPIC,
            displayName="Claude Support",
            providerConfig=cfg,
        )

        a = await client.create_assessment(
            model="claude-support",                # slug or DB id
            test_types=["jailbreak", "toxicity"],
            priority=Priority.NORMAL,
        )

        done = await client.wait_for_completion(a.id, timeout_minutes=30, poll_interval=5)
        print("Assessment:", done.status.value)

asyncio.run(main())
Providers
Create a providerConfig using the helpers below. These mirror server-side validation and keep your code portable across environments.

python
Copy code
from modelred_sdk import ProviderConfig

# OpenAI
openai_cfg = ProviderConfig.openai(
    api_key="sk-openai",
    model_name="gpt-4o-mini",
    # organization="org_abc"  # optional
)

# Anthropic
anthropic_cfg = ProviderConfig.anthropic(
    api_key="sk-ant",
    model_name="claude-3-sonnet-20240229",
)

# Azure OpenAI
azure_cfg = ProviderConfig.azure(
    api_key="azure-key",
    endpoint="https://your-resource.openai.azure.com",
    deployment_name="gpt-4o",
    api_version="2024-06-01",
)

# Hugging Face (Inference API or custom endpoint)
hf_cfg = ProviderConfig.huggingface(
    model_name="mistralai/Mistral-7B-Instruct",
    api_key="hf_...",
    use_inference_api=True,
    task="text-generation",
    # endpoint_url="https://.../your-hf-endpoint"  # optional for private endpoints
)

# Custom REST API
rest_cfg = ProviderConfig.rest(
    uri="https://api.example.com/v1/chat",
    headers={"Authorization": "Bearer TOKEN"},
    req_template_json_object={
        "model": "x",
        "messages": [{"role": "user", "content": "$INPUT"}],
        "max_tokens": 256,
    },
    response_json_field="choices.0.message.content",
    request_timeout=30,
)

# AWS Bedrock
bedrock_cfg = ProviderConfig.bedrock(
    region="us-east-1",
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    access_key_id="AKIA...",
    secret_access_key="...",
    # session_token="..."  # optional
)

# AWS SageMaker
sagemaker_cfg = ProviderConfig.sagemaker(
    region="us-east-1",
    endpoint_name="my-sagemaker-endpoint",
    access_key_id="AKIA...",
    secret_access_key="...",
    request_json_template={"inputs": "$INPUT"},
    response_json_field="0.generated_text",
)
Use the same create_model call regardless of provider; only providerConfig changes.

Probes API
Discover which probes are available to you and how they’re categorized:

python
Copy code
index = client.get_probes(tier="free")  # optional filters: category, tier, severity

print("Total probes:", len(index.probes))
for p in index.probes[:5]:
    print(p.key, p.display_name, p.category, p.tier, p.severity)
The response includes:

probes: list of probe records (key, display_name, description, estimated_time, tags, category, tier, severity, version)

probe_categories: map of category metadata

tier_definitions: map of tier metadata

severity_levels: map of severity metadata

Use probe keys when creating assessments (test_types=[...]).

Public API (Sync)
Models

create_model(modelId, provider, displayName, providerConfig, description=None) -> Model

list_models() -> List[Model]

get_model(model_identifier) -> Model (slug or DB id)

delete_model(model_identifier) -> bool (slug or DB id)

Assessments

create_assessment(model, test_types, priority=Priority.NORMAL) -> Assessment (model is slug or DB id)

get_assessment(assessment_id) -> Assessment

list_assessments(limit=None) -> List[Assessment]

wait_for_completion(assessment_id, timeout_minutes=60, poll_interval=10, progress_callback=None) -> Assessment

Probes

get_probes(category=None, tier=None, severity=None) -> ProbesIndex

The async client (AsyncModelRed) exposes the same surface with await.

Data Models
python
Copy code
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

class AssessmentStatus(Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Priority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Model:
    id: str
    modelId: str
    provider: str
    modelName: Optional[str]
    displayName: str
    description: Optional[str]
    isActive: bool
    lastTested: Optional[datetime]
    testCount: int
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdByUser: Optional[Dict[str, Any]] = None

@dataclass
class Assessment:
    id: str
    modelId: str
    status: AssessmentStatus
    testTypes: List[str]
    priority: Priority
    progress: int = 0
    results: Optional[Dict[str, Any]] = None
    errorMessage: Optional[str] = None
    createdAt: Optional[datetime] = None
    completedAt: Optional[datetime] = None
    estimatedDuration: Optional[int] = None
    detailedReport: Optional[Dict[str, Any]] = None
Error Handling
Errors map cleanly to exception types:

AuthenticationError (401)

AuthorizationError (403)

SubscriptionLimitError (403 with tier info)

ValidationError (422/400)

NotFoundError (404)

ConflictError (409)

RateLimitError (429)

ServerError (5xx)

NetworkError (transport issues)

ModelRedError (catch-all)

Example:

python
Copy code
from modelred_sdk import (
    ModelRedError, AuthenticationError, ValidationError,
    SubscriptionLimitError, NotFoundError, RateLimitError
)

try:
    ...
except AuthenticationError as e:
    print("Auth failed:", e.message)
except SubscriptionLimitError as e:
    print("Plan limit:", e.tier, "-", e.message)
except ValidationError as e:
    print("Bad input:", e.message)
except RateLimitError:
    print("Back off and retry")
except ModelRedError as e:
    print("API error:", e.status_code, e.message)
Practical Patterns
Progress reporting
python
Copy code
def progress(a):
    print(f"{a.status.value} {a.progress}%")

assess = client.create_assessment(
    model="cust-support-prod",
    test_types=["comprehensive_security"],
)

final = client.wait_for_completion(
    assessment_id=assess.id,
    timeout_minutes=60,
    progress_callback=progress,
)
Concurrent async assessments
python
Copy code
import asyncio
from modelred_sdk import AsyncModelRed, Priority

async def run():
    async with AsyncModelRed() as client:
        ids = ["cust-support-prod", "claude-support", "my-rest-model"]
        tasks = [client.create_assessment(model=i, test_types=["jailbreak"], priority=Priority.HIGH) for i in ids]
        assessments = await asyncio.gather(*tasks)

        finals = await asyncio.gather(*[
            client.wait_for_completion(a.id, timeout_minutes=30) for a in assessments
        ])
        return finals

asyncio.run(run())
```
