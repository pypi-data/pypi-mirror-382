import logging

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

__version__ = "0.1.34"

from .client import AsyncModelRedClient, ModelRedClient
from .config import DEFAULT_BASE_URL, load_settings
from .exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    ModelRedError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ServerError,
    SubscriptionLimitError,
    ValidationError,
)
from .resources.assessments import (
    Assessment as _ResourceAssessment,
    AssessmentPriority as _ResourcePriority,
    AssessmentStatus as _ResourceStatus,
)
from .resources.models import Model as _ResourceModel, ModelList as _ResourceModelList
from .resources.probes import Probe as Probe, ProbeIndex as ProbesIndex

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
logger = logging.getLogger("modelred")
if not logger.handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(h)
logger.setLevel(logging.INFO)

# -----------------------------------------------------------------------------
# Constants / Enums
# -----------------------------------------------------------------------------
BASE_URL = DEFAULT_BASE_URL


class ModelProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
    HUGGINGFACE = "huggingface"
    REST = "rest"
    BEDROCK = "bedrock"
    SAGEMAKER = "sagemaker"
    GOOGLE = "google"
    GROK = "grok"
    OPENROUTER = "openrouter"


AssessmentStatus = _ResourceStatus
Priority = _ResourcePriority


# -----------------------------------------------------------------------------
# Data classes
# -----------------------------------------------------------------------------
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
class ModelList:
    """List of models with pagination metadata."""

    models: List[Model]
    page: int
    pageSize: int
    total: int
    totalPages: int


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


# -----------------------------------------------------------------------------
# Provider config helpers
# -----------------------------------------------------------------------------
class ProviderConfig:
    """Factory methods for creating provider-specific configuration dictionaries.

    Each provider has different requirements:
    - OpenAI: api_key, model_name, optional base_url, optional organization
    - Anthropic: api_key, model_name
    - Azure: api_key, endpoint, deployment_name, api_version
    - OpenRouter: api_key, model_name, optional base_url
    - Google (Gemini): api_key, model_name, optional generation_config/safety_settings
    - Grok (xAI): api_key, model_name
    - HuggingFace: model_name, api_key, use_inference_api, endpoint_url, optional task
    - REST: uri, method, timeout, api_key, headers, ratelimit_codes, skip_codes, request/response templates
    - Bedrock: region, model_id, AWS credentials (access_key_id, secret_access_key), optional session_token/temperature/max_tokens
    - SageMaker: region, endpoint_name, AWS credentials (access_key_id, secret_access_key), optional content_type/accept/timeout_ms, request/response templates

    All methods return a Dict[str, Any] that can be passed as providerConfig
    when creating a model.
    """

    @staticmethod
    def openai(
        api_key: str,
        model_name: str = "gpt-4o-mini",
        organization: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """OpenAI configuration.

        Args:
            api_key: OpenAI API key (starts with sk-)
            model_name: Model identifier (e.g. "gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo")
            organization: Optional organization ID
            base_url: Optional base URL for API endpoint (for OpenAI-compatible APIs)
        """
        cfg = {"api_key": api_key, "model_name": model_name}
        if organization:
            cfg["organization"] = organization
        if base_url:
            cfg["base_url"] = base_url
        return cfg

    @staticmethod
    def anthropic(
        api_key: str, model_name: str = "claude-3-5-sonnet-20241022"
    ) -> Dict[str, Any]:
        """Anthropic Claude configuration.

        Args:
            api_key: Anthropic API key
            model_name: Model identifier (e.g. "claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022")
        """
        return {"api_key": api_key, "model_name": model_name}

    @staticmethod
    def azure(
        api_key: str,
        endpoint: str,
        deployment_name: str,
        api_version: str = "2024-06-01",
    ) -> Dict[str, Any]:
        """Azure OpenAI configuration.

        Args:
            api_key: Azure OpenAI API key
            endpoint: Azure OpenAI endpoint URL (e.g. "https://YOUR_RESOURCE.openai.azure.com")
            deployment_name: Azure deployment name
            api_version: Azure API version (default: "2024-06-01")
        """
        return {
            "api_key": api_key,
            "endpoint": endpoint,
            "deployment_name": deployment_name,
            "api_version": api_version,
        }

    @staticmethod
    def openrouter(
        api_key: str,
        model_name: str,
        base_url: str = "https://openrouter.ai/api/v1",
    ) -> Dict[str, Any]:
        """OpenRouter configuration.

        Args:
            api_key: OpenRouter API key
            model_name: Model identifier (e.g. "anthropic/claude-3.5-sonnet", "google/gemini-pro-1.5")
            base_url: OpenRouter API base URL (default: "https://openrouter.ai/api/v1")
        """
        return {
            "api_key": api_key,
            "model_name": model_name,
            "base_url": base_url,
        }

    @staticmethod
    def grok(
        api_key: str,
        model_name: str = "grok-beta",
    ) -> Dict[str, Any]:
        """xAI Grok configuration.

        Args:
            api_key: xAI API key
            model_name: Model identifier (default: "grok-beta")
        """
        return {
            "api_key": api_key,
            "model_name": model_name,
        }

    @staticmethod
    def google(
        model_name: str,
        api_key: str,
        *,
        generation_config: Optional[Dict[str, Any]] = None,
        safety_settings: Optional[List[Dict[str, Any]]] = None,
        # legacy args kept for compatibility but ignored:
        project_id: Optional[str] = None,
        location: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Google Gemini (Developer API) configuration.

        Args:
            model_name: Model identifier (e.g. "gemini-2.0-flash-exp", "gemini-1.5-pro")
            api_key: Google AI Studio / Developer API key
            generation_config: Optional generation configuration dict
            safety_settings: Optional safety settings list

        Notes:
            - Vertex AI params (project_id, location) are ignored in current version
        """
        if not api_key:
            raise ValidationError("Google (Developer API) requires api_key")

        # Gentle warning if legacy Vertex hints are supplied
        if project_id or location:
            logger.warning(
                "ProviderConfig.google: ignoring Vertex params (project_id/location) "
                "because SDK is in Developer API mode."
            )

        cfg: Dict[str, Any] = {
            "model_name": model_name,
            "api_key": api_key,
        }
        if generation_config is not None:
            cfg["generation_config"] = generation_config
        if safety_settings is not None:
            cfg["safety_settings"] = safety_settings
        return cfg

    @staticmethod
    def huggingface(
        model_name: str,
        api_key: str = "",
        *,
        use_inference_api: bool = True,
        endpoint_url: str = "https://api-inference.huggingface.co/models",
        task: str = "text-generation",
    ) -> Dict[str, Any]:
        """HuggingFace configuration.

        Args:
            model_name: Model identifier (e.g. "meta-llama/Llama-2-7b-chat-hf")
            api_key: HuggingFace API token (optional for public models)
            use_inference_api: Whether to use HF Inference API (default: True)
            endpoint_url: Inference API endpoint URL
            task: Task type (default: "text-generation")

        Returns:
            Configuration dict for HuggingFace models
        """
        return {
            "api_key": api_key,
            "model_name": model_name,
            "use_inference_api": use_inference_api,
            "endpoint_url": endpoint_url,
            "task": task,
        }

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
        request_timeout: int = 20,
        ratelimit_codes: Optional[List[int]] = None,
        skip_codes: Optional[List[int]] = None,
        verify_ssl: bool = True,
        proxies: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Custom REST API configuration.

        Args:
            uri: API endpoint URL
            api_key: Optional API key
            method: HTTP method (default: "POST")
            headers: Optional HTTP headers dict
            req_template: Request template string where $INPUT is replaced (default: "$INPUT")
            req_template_json_object: Optional JSON request template
            response_json: Whether response is JSON (default: True)
            response_json_field: JSON field containing response text (default: "text")
            request_timeout: Request timeout in seconds (default: 20)
            ratelimit_codes: HTTP codes to treat as rate limits (default: [429])
            skip_codes: HTTP codes to skip (default: [])
            verify_ssl: Whether to verify SSL certificates (default: True)
            proxies: Optional proxy configuration

        Returns:
            Configuration dict for custom REST APIs

        Example:
            config = ProviderConfig.rest(
                uri="https://api.example.com/generate",
                api_key="your-key",
                headers={"Content-Type": "application/json"},
                req_template_json_object={"prompt": "$INPUT", "max_tokens": 100}
            )
        """
        cfg: Dict[str, Any] = {
            "uri": uri,
            "method": method,
            "req_template": req_template,
            "response_json": response_json,
            "response_json_field": response_json_field,
            "request_timeout": request_timeout,
            "ratelimit_codes": ratelimit_codes or [429],
            "skip_codes": skip_codes or [],
            "verify_ssl": verify_ssl,
            "headers": headers or {},
        }
        if api_key:
            cfg["api_key"] = api_key
        if req_template_json_object:
            cfg["req_template_json_object"] = req_template_json_object
        if proxies:
            cfg["proxies"] = proxies
        return cfg

    @staticmethod
    def bedrock(
        region: str,
        model_id: str,
        access_key_id: str,
        secret_access_key: str,
        *,
        session_token: Optional[str] = None,
        temperature: float = 0,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """AWS Bedrock configuration.

        Args:
            region: AWS region (e.g. "us-east-1")
            model_id: Bedrock model ID (e.g. "anthropic.claude-v2")
            access_key_id: AWS access key ID
            secret_access_key: AWS secret access key
            session_token: Optional AWS session token
            temperature: Model temperature (default: 0)
            max_tokens: Maximum tokens to generate (default: 1024)

        Returns:
            Configuration dict for AWS Bedrock

        Example:
            config = ProviderConfig.bedrock(
                region="us-east-1",
                model_id="anthropic.claude-v2",
                access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"]
            )
        """
        cfg: Dict[str, Any] = {
            "region": region,
            "model_id": model_id,
            "access_key_id": access_key_id,
            "secret_access_key": secret_access_key,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if session_token:
            cfg["session_token"] = session_token
        return cfg

    @staticmethod
    def sagemaker(
        region: str,
        endpoint_name: str,
        access_key_id: str,
        secret_access_key: str,
        *,
        session_token: Optional[str] = None,
        content_type: str = "application/json",
        accept: str = "application/json",
        request_json_template: Optional[Dict[str, Any]] = None,
        request_text_template: Optional[str] = None,
        response_json_field: str = "generated_text",
        timeout_ms: int = 20000,
    ) -> Dict[str, Any]:
        """AWS SageMaker configuration.

        Args:
            region: AWS region (e.g. "us-east-1")
            endpoint_name: SageMaker endpoint name
            access_key_id: AWS access key ID
            secret_access_key: AWS secret access key
            session_token: Optional AWS session token
            content_type: Request content type (default: "application/json")
            accept: Accept header (default: "application/json")
            request_json_template: Optional JSON request template
            request_text_template: Optional text request template
            response_json_field: JSON field containing response (default: "generated_text")
            timeout_ms: Request timeout in milliseconds (default: 20000)

        Returns:
            Configuration dict for AWS SageMaker

        Example:
            config = ProviderConfig.sagemaker(
                region="us-west-2",
                endpoint_name="my-model-endpoint",
                access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
                request_json_template={"inputs": "$INPUT"}
            )
        """
        cfg: Dict[str, Any] = {
            "region": region,
            "endpoint_name": endpoint_name,
            "access_key_id": access_key_id,
            "secret_access_key": secret_access_key,
            "content_type": content_type,
            "accept": accept,
            "response_json_field": response_json_field,
            "timeout_ms": timeout_ms,
        }
        if session_token:
            cfg["session_token"] = session_token
        if request_json_template:
            cfg["request_json_template"] = request_json_template
        if request_text_template:
            cfg["request_text_template"] = request_text_template
        return cfg


# -----------------------------------------------------------------------------
# Base client
# -----------------------------------------------------------------------------
class ModelRed:
    """Synchronous ModelRed SDK client.

    Security features:
    - DELETE operations are disabled for user safety
    - Base URL is only configurable via MODELRED_BASE_URL environment variable
    - API keys must be provided explicitly or via MODELRED_API_KEY environment variable
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = 30,
        *,
        _client: Optional[ModelRedClient] = None,
    ) -> None:
        """Initialize ModelRed client.

        Args:
            api_key: Your ModelRed API key (or set MODELRED_API_KEY environment variable)
            timeout: Request timeout in seconds (default: 30)

        Security Note:
            The base_url is ONLY configurable via MODELRED_BASE_URL environment variable.
            This prevents malicious code from redirecting your API traffic.
        """
        settings = load_settings(timeout=timeout)
        self._client = _client or ModelRedClient(api_key=api_key, settings=settings)
        self.timeout = timeout
        self.logger = logger
        self.api_key = self._client.api_key

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"ModelRed-PythonSDK/{__version__}",
        }

    # Models
    def create_model(
        self,
        *,
        modelId: str,
        provider: Union[str, ModelProvider],
        displayName: str,
        providerConfig: Dict[str, Any],
        description: Optional[str] = None,
    ) -> Model:
        """Create a new model configuration.

        Args:
            modelId: Unique identifier for this model
            provider: Model provider (use ModelProvider enum)
            displayName: Human-readable display name
            providerConfig: Provider-specific configuration (use ProviderConfig helper methods)
            description: Optional model description

        Returns:
            Created Model object

        Example:
            model = client.create_model(
                modelId="my-gpt4",
                provider=ModelProvider.OPENAI,
                displayName="GPT-4",
                providerConfig=ProviderConfig.openai(
                    api_key=os.environ["OPENAI_API_KEY"],
                    model_name="gpt-4o-mini"
                )
            )
        """
        provider_value = (
            provider.value if isinstance(provider, ModelProvider) else str(provider)
        )
        resource = self._client.models.create(
            model_id=modelId,
            provider=provider_value,
            display_name=displayName,
            provider_config=providerConfig,
            description=description,
        )
        return _to_legacy_model(resource)

    def list_models(
        self,
        *,
        page: int = 1,
        page_size: int = 100,
        search: Optional[str] = None,
        provider: Optional[str] = None,
        status: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_dir: Optional[str] = None,
    ) -> ModelList:
        """List all models in your organization with pagination and filtering.

        Args:
            page: Page number (default: 1)
            page_size: Number of models per page (default: 100, max: 100)
            search: Search term for filtering models by name/ID
            provider: Filter by provider (openai, anthropic, azure, huggingface, rest,
                     bedrock, sagemaker, google, grok, openrouter)
            status: Filter by status ('active', 'inactive', 'both')
            sort_by: Sort field (displayName, provider, modelId, modelName, isActive,
                    testCount, lastTested, createdAt)
            sort_dir: Sort direction ('asc' or 'desc')

        Returns:
            ModelList object containing models and pagination metadata

        Example:
            # Get first page of active OpenAI models
            result = client.list_models(
                page=1,
                page_size=20,
                provider="openai",
                status="active"
            )
            print(f"Found {result.total} models, showing page {result.page}/{result.totalPages}")
            for model in result.models:
                print(f"- {model.displayName}")
        """
        resource_list = self._client.models.list(
            page=page,
            page_size=page_size,
            search=search,
            provider=provider,
            status=status,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        return ModelList(
            models=[_to_legacy_model(m) for m in resource_list.models],
            page=resource_list.page,
            pageSize=resource_list.page_size,
            total=resource_list.total,
            totalPages=resource_list.total_pages,
        )

    def get_model(self, model_identifier: str) -> Model:
        """Retrieve a specific model by ID or modelId.

        Args:
            model_identifier: Model ID or modelId

        Returns:
            Model object
        """
        resource = self._client.models.retrieve(model_identifier)
        return _to_legacy_model(resource)

    # Assessments
    def create_assessment(
        self,
        *,
        model: str,
        test_types: Optional[List[str]] = None,
        preset: Optional[str] = None,
        category: Optional[str] = None,
        severity: Optional[str] = None,
        priority: Union[str, Priority] = Priority.NORMAL,
    ) -> Assessment:
        """Create a new security assessment.

        Args:
            model: Model ID or modelId to assess
            test_types: List of probe keys (mutually exclusive with preset/category/severity)
            preset: Preset collection - "quick", "standard", "extended", "comprehensive"
                   (mutually exclusive with test_types/category/severity)
            category: Filter probes by category (mutually exclusive with preset/test_types)
            severity: Filter probes by severity (mutually exclusive with preset/test_types)
            priority: Assessment priority (default: Priority.NORMAL)

        Returns:
            Created Assessment object (status will be QUEUED initially)

        Presets:
            - quick: 20 critical/high severity probes (~5-10 min)
            - standard: 50% of available critical/high probes (~30-45 min)
            - extended: 75% of available critical/high/medium probes (~60-90 min)
            - comprehensive: All available probes (~2-3 hours)

        Examples:
            # Using preset
            assessment = client.create_assessment(
                model="my-gpt4",
                preset="quick"
            )

            # Using category filter
            assessment = client.create_assessment(
                model="my-gpt4",
                category="medical_ethics"
            )

            # Using severity filter
            assessment = client.create_assessment(
                model="my-gpt4",
                severity="critical"
            )

            # Combining category + severity
            assessment = client.create_assessment(
                model="my-gpt4",
                category="medical_ethics",
                severity="critical"
            )

            # Using custom probes
            assessment = client.create_assessment(
                model="my-gpt4",
                test_types=["reverse_psychology", "role_swap"],
                priority=Priority.NORMAL
            )
        """
        # Validate parameters - only one selection method allowed
        selection_methods = sum(
            [bool(preset), bool(test_types), bool(category or severity)]
        )

        if selection_methods == 0:
            raise ValueError(
                "Must specify one of: 'preset', 'test_types', or 'category/severity'"
            )

        if selection_methods > 1:
            raise ValueError(
                "Cannot mix 'preset', 'test_types', and 'category/severity'. "
                "Choose only one selection method."
            )

        # Handle preset
        if preset:
            test_types = self._get_preset_probes(preset)

        # Handle category/severity filtering
        elif category or severity:
            probes = self.list_probes(category=category, severity=severity)
            test_types = [p.key for p in probes.probes]

            if not test_types:
                raise ValueError(
                    f"No probes found for category='{category}', severity='{severity}'. "
                    f"Check available probes with list_probes()."
                )

        priority_value = _normalise_priority(priority)
        resource = self._client.assessments.create(
            model=model,
            test_types=test_types,
            priority=priority_value,
        )
        return _to_legacy_assessment(resource)

    def get_assessment(self, assessment_id: str) -> Assessment:
        """Retrieve assessment status and results.

        Args:
            assessment_id: Assessment ID

        Returns:
            Assessment object with current status and results (if completed)
        """
        resource = self._client.assessments.retrieve(assessment_id)
        return _to_legacy_assessment(resource)

    def list_assessments(self, limit: Optional[int] = None) -> List[Assessment]:
        """List recent assessments.

        Args:
            limit: Maximum number of assessments to return (optional)

        Returns:
            List of Assessment objects
        """
        resources = self._client.assessments.list(limit=limit)
        return [_to_legacy_assessment(a) for a in resources]

    def wait_for_completion(
        self,
        assessment_id: str,
        *,
        timeout_minutes: int = 60,
        poll_interval: int = 10,
        progress_callback: Optional[Callable[[Assessment], None]] = None,
    ) -> Assessment:
        """Wait for assessment to complete, polling for status updates.

        Args:
            assessment_id: Assessment ID
            timeout_minutes: Maximum time to wait (default: 60)
            poll_interval: Seconds between status checks (default: 10)
            progress_callback: Optional callback function called on status changes

        Returns:
            Completed Assessment object with results

        Example:
            def on_progress(assessment):
                print(f"Status: {assessment.status} - Progress: {assessment.progress}%")

            result = client.wait_for_completion(
                assessment_id,
                timeout_minutes=15,
                progress_callback=on_progress
            )
        """
        wrapped = _wrap_sync_callback(progress_callback)
        resource = self._client.assessments.wait_for_completion(
            assessment_id,
            timeout_seconds=timeout_minutes * 60,
            poll_interval=poll_interval,
            progress_callback=wrapped,
        )
        return _to_legacy_assessment(resource)

    # Probes
    def list_probes(
        self,
        *,
        category: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> ProbesIndex:
        """List all security probes available for your subscription.

        Probes are automatically filtered based on your subscription level.
        You cannot manually filter by tier - this is handled server-side.

        Args:
            category: Optional category filter (e.g. "universal", "medical_ethics",
                     "legal_ethics", "financial_compliance", "cyber_operations")
            severity: Optional severity filter ("critical", "high", "medium", "low")

        Returns:
            ProbesIndex containing available probes and metadata

        Example:
            # Get all available probes for your subscription
            probes = client.list_probes()

            # Filter by category
            medical_probes = client.list_probes(category="medical_ethics")

            # Filter by severity
            critical_probes = client.list_probes(severity="critical")

            # Combine filters
            critical_medical = client.list_probes(
                category="medical_ethics",
                severity="critical"
            )

            # Use probe keys in assessment
            probe_keys = [p.key for p in probes.probes[:5]]
            assessment = client.create_assessment(
                model="my-model",
                test_types=probe_keys
            )
        """
        # Tier filtering is handled server-side based on authenticated user's subscription
        return self._client.probes.list(
            category=category,
            tier=None,  # Always None - server determines from API key
            severity=severity,
        )

    def _get_preset_probes(self, preset: str) -> List[str]:
        """Get probe keys for a preset based on user's subscription.

        Presets are intelligent and adapt to the user's subscription tier:
        - quick: 20 critical/high severity probes
        - standard: 50% of critical/high probes (at least 20)
        - extended: 75% of critical/high/medium probes
        - comprehensive: All available probes

        Args:
            preset: Preset name ("quick", "standard", "extended", "comprehensive")

        Returns:
            List of probe keys

        Raises:
            ValueError: If preset is invalid
        """
        valid_presets = ["quick", "standard", "extended", "comprehensive"]
        if preset not in valid_presets:
            raise ValueError(
                f"Invalid preset: {preset}. "
                f"Must be one of: {', '.join(valid_presets)}"
            )

        # Get all available probes for this user's subscription
        all_probes = self.list_probes()

        if preset == "quick":
            # Top 20 critical/high severity probes
            critical_high = [
                p for p in all_probes.probes if p.severity in ["critical", "high"]
            ]
            # Sort by severity (critical first, then high)
            sorted_probes = sorted(
                critical_high,
                key=lambda p: (0 if p.severity == "critical" else 1, p.key),
            )
            return [p.key for p in sorted_probes[:20]]

        elif preset == "standard":
            # 50% of critical/high severity probes (minimum 20)
            critical_high = [
                p for p in all_probes.probes if p.severity in ["critical", "high"]
            ]
            sorted_probes = sorted(
                critical_high,
                key=lambda p: (0 if p.severity == "critical" else 1, p.key),
            )
            count = max(20, int(len(sorted_probes) * 0.5))
            return [p.key for p in sorted_probes[:count]]

        elif preset == "extended":
            # 75% of critical/high/medium severity probes
            chm = [
                p
                for p in all_probes.probes
                if p.severity in ["critical", "high", "medium"]
            ]
            severity_order = {"critical": 0, "high": 1, "medium": 2}
            sorted_probes = sorted(
                chm, key=lambda p: (severity_order.get(p.severity, 3), p.key)
            )
            count = int(len(sorted_probes) * 0.75)
            return [p.key for p in sorted_probes[:count]]

        elif preset == "comprehensive":
            # All available probes for this user's subscription
            return [p.key for p in all_probes.probes]

        # Should never reach here due to validation above
        raise ValueError(f"Unknown preset: {preset}")

    def redacted_api_key(self) -> str:
        return self._client.redacted_api_key()

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "ModelRed":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


class AsyncModelRed:
    """Async ModelRed SDK client.

    Security features:
    - DELETE operations are disabled for user safety
    - Base URL is only configurable via MODELRED_BASE_URL environment variable
    - API keys must be provided explicitly or via MODELRED_API_KEY environment variable
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = 30,
        *,
        _client: Optional[AsyncModelRedClient] = None,
    ) -> None:
        """Initialize async ModelRed client.

        Args:
            api_key: Your ModelRed API key (or set MODELRED_API_KEY environment variable)
            timeout: Request timeout in seconds (default: 30)

        Security Note:
            The base_url is ONLY configurable via MODELRED_BASE_URL environment variable.
            This prevents malicious code from redirecting your API traffic.
        """
        settings = load_settings(timeout=timeout)
        self._client = _client or AsyncModelRedClient(
            api_key=api_key, settings=settings
        )
        self.timeout = timeout
        self.logger = logger
        self.api_key = self._client.api_key

    # Models
    async def create_model(
        self,
        *,
        modelId: str,
        provider: Union[str, ModelProvider],
        displayName: str,
        providerConfig: Dict[str, Any],
        description: Optional[str] = None,
    ) -> Model:
        """Create a new model configuration (async).

        See ModelRed.create_model() for full documentation.
        """
        provider_value = (
            provider.value if isinstance(provider, ModelProvider) else str(provider)
        )
        resource = await self._client.models.create(
            model_id=modelId,
            provider=provider_value,
            display_name=displayName,
            provider_config=providerConfig,
            description=description,
        )
        return _to_legacy_model(resource)

    async def list_models(
        self,
        *,
        page: int = 1,
        page_size: int = 100,
        search: Optional[str] = None,
        provider: Optional[str] = None,
        status: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_dir: Optional[str] = None,
    ) -> ModelList:
        """List all models in your organization with pagination and filtering (async).

        See ModelRed.list_models() for full documentation.
        """
        resource_list = await self._client.models.list(
            page=page,
            page_size=page_size,
            search=search,
            provider=provider,
            status=status,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        return ModelList(
            models=[_to_legacy_model(m) for m in resource_list.models],
            page=resource_list.page,
            pageSize=resource_list.page_size,
            total=resource_list.total,
            totalPages=resource_list.total_pages,
        )

    async def get_model(self, model_identifier: str) -> Model:
        """Retrieve a specific model by ID or modelId (async)."""
        resource = await self._client.models.retrieve(model_identifier)
        return _to_legacy_model(resource)

    # Assessments
    async def create_assessment(
        self,
        *,
        model: str,
        test_types: Optional[List[str]] = None,
        preset: Optional[str] = None,
        category: Optional[str] = None,
        severity: Optional[str] = None,
        priority: Union[str, Priority] = Priority.NORMAL,
    ) -> Assessment:
        """Create a new security assessment (async).

        See ModelRed.create_assessment() for full documentation.
        """
        # Validate parameters - only one selection method allowed
        selection_methods = sum(
            [bool(preset), bool(test_types), bool(category or severity)]
        )

        if selection_methods == 0:
            raise ValueError(
                "Must specify one of: 'preset', 'test_types', or 'category/severity'"
            )

        if selection_methods > 1:
            raise ValueError(
                "Cannot mix 'preset', 'test_types', and 'category/severity'. "
                "Choose only one selection method."
            )

        # Handle preset
        if preset:
            test_types = await self._get_preset_probes(preset)

        # Handle category/severity filtering
        elif category or severity:
            probes = await self.list_probes(category=category, severity=severity)
            test_types = [p.key for p in probes.probes]

            if not test_types:
                raise ValueError(
                    f"No probes found for category='{category}', severity='{severity}'. "
                    f"Check available probes with list_probes()."
                )

        priority_value = _normalise_priority(priority)
        resource = await self._client.assessments.create(
            model=model,
            test_types=test_types,
            priority=priority_value,
        )
        return _to_legacy_assessment(resource)

    async def get_assessment(self, assessment_id: str) -> Assessment:
        """Retrieve assessment status and results (async)."""
        resource = await self._client.assessments.retrieve(assessment_id)
        return _to_legacy_assessment(resource)

    async def list_assessments(self, limit: Optional[int] = None) -> List[Assessment]:
        """List recent assessments (async)."""
        resources = await self._client.assessments.list(limit=limit)
        return [_to_legacy_assessment(a) for a in resources]

    async def wait_for_completion(
        self,
        assessment_id: str,
        *,
        timeout_minutes: int = 60,
        poll_interval: int = 10,
        progress_callback: Optional[Callable[[Assessment], None]] = None,
    ) -> Assessment:
        """Wait for assessment to complete (async).

        See ModelRed.wait_for_completion() for full documentation.
        """
        wrapped = _wrap_async_callback(progress_callback)
        resource = await self._client.assessments.wait_for_completion(
            assessment_id,
            timeout_seconds=timeout_minutes * 60,
            poll_interval=poll_interval,
            progress_callback=wrapped,
        )
        return _to_legacy_assessment(resource)

    async def list_probes(
        self,
        *,
        category: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> ProbesIndex:
        """List all security probes available for your subscription (async).

        See ModelRed.list_probes() for full documentation.
        """
        # Tier filtering is handled server-side based on authenticated user's subscription
        return await self._client.probes.list(
            category=category,
            tier=None,  # Always None - server determines from API key
            severity=severity,
        )

    async def _get_preset_probes(self, preset: str) -> List[str]:
        """Get probe keys for a preset based on user's subscription (async).

        See ModelRed._get_preset_probes() for full documentation.
        """
        valid_presets = ["quick", "standard", "extended", "comprehensive"]
        if preset not in valid_presets:
            raise ValueError(
                f"Invalid preset: {preset}. "
                f"Must be one of: {', '.join(valid_presets)}"
            )

        # Get all available probes for this user's subscription
        all_probes = await self.list_probes()

        if preset == "quick":
            # Top 20 critical/high severity probes
            critical_high = [
                p for p in all_probes.probes if p.severity in ["critical", "high"]
            ]
            sorted_probes = sorted(
                critical_high,
                key=lambda p: (0 if p.severity == "critical" else 1, p.key),
            )
            return [p.key for p in sorted_probes[:20]]

        elif preset == "standard":
            # 50% of critical/high severity probes (minimum 20)
            critical_high = [
                p for p in all_probes.probes if p.severity in ["critical", "high"]
            ]
            sorted_probes = sorted(
                critical_high,
                key=lambda p: (0 if p.severity == "critical" else 1, p.key),
            )
            count = max(20, int(len(sorted_probes) * 0.5))
            return [p.key for p in sorted_probes[:count]]

        elif preset == "extended":
            # 75% of critical/high/medium severity probes
            chm = [
                p
                for p in all_probes.probes
                if p.severity in ["critical", "high", "medium"]
            ]
            severity_order = {"critical": 0, "high": 1, "medium": 2}
            sorted_probes = sorted(
                chm, key=lambda p: (severity_order.get(p.severity, 3), p.key)
            )
            count = int(len(sorted_probes) * 0.75)
            return [p.key for p in sorted_probes[:count]]

        elif preset == "comprehensive":
            # All available probes for this user's subscription
            return [p.key for p in all_probes.probes]

        raise ValueError(f"Unknown preset: {preset}")

    def redacted_api_key(self) -> str:
        return self._client.redacted_api_key()

    async def close(self) -> None:
        await self._client.close()

    async def __aenter__(self) -> "AsyncModelRed":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self._client.__aexit__(exc_type, exc, tb)


def _normalise_priority(priority: Union[str, Priority]) -> Priority:
    if isinstance(priority, Priority):
        return priority
    return Priority(str(priority).lower())


def _to_legacy_model(model: _ResourceModel) -> Model:
    return Model(
        id=model.id,
        modelId=model.model_id,
        provider=model.provider,
        modelName=model.model_name,
        displayName=model.display_name,
        description=model.description,
        isActive=model.is_active,
        lastTested=model.last_tested,
        testCount=model.test_count,
        createdAt=model.created_at,
        updatedAt=model.updated_at,
        createdByUser=None,
    )


def _to_legacy_assessment(assessment: _ResourceAssessment) -> Assessment:
    return Assessment(
        id=assessment.id,
        modelId=assessment.model_id,
        status=assessment.status,
        testTypes=assessment.test_types,
        priority=assessment.priority,
        progress=assessment.progress,
        results=None,
        errorMessage=None,
        createdAt=assessment.created_at,
        completedAt=assessment.completed_at,
        estimatedDuration=None,
        detailedReport=assessment.detailed_report,
    )


def _wrap_sync_callback(
    callback: Optional[Callable[[Assessment], None]],
) -> Optional[Callable[[_ResourceAssessment], None]]:
    if callback is None:
        return None

    def _inner(resource_assessment: _ResourceAssessment) -> None:
        callback(_to_legacy_assessment(resource_assessment))

    return _inner


def _wrap_async_callback(
    callback: Optional[Callable[[Assessment], None]],
) -> Optional[Callable[[_ResourceAssessment], None]]:
    if callback is None:
        return None

    def _inner(resource_assessment: _ResourceAssessment) -> None:
        callback(_to_legacy_assessment(resource_assessment))

    return _inner


# -----------------------------------------------------------------------------
# Display Helper Functions
# -----------------------------------------------------------------------------
def print_header(title: str, width: int = 80) -> None:
    """Print a formatted header for display output.

    Args:
        title: The title text to display
        width: Width of the header line (default: 80)

    Example:
        print_header("ASSESSMENT RESULTS")
    """
    print("\n" + "=" * width)
    print(f"📊 {title}")
    print("=" * width)


def print_assessment_summary(assessment: Assessment) -> None:
    """Print assessment summary in a formatted table.

    Args:
        assessment: Assessment object to display

    Example:
        assessment = client.get_assessment("assess_123")
        print_assessment_summary(assessment)
    """
    print_header("ASSESSMENT SUMMARY")

    print(f"\n{'Metric':<30} {'Value':<50}")
    print("-" * 80)
    print(f"{'Assessment ID':<30} {assessment.id:<50}")
    print(f"{'Model':<30} {assessment.modelId:<50}")
    print(f"{'Status':<30} {assessment.status:<50}")
    print(f"{'Priority':<30} {assessment.priority:<50}")
    print(f"{'Progress':<30} {assessment.progress}%")
    print(f"{'Total Probes':<30} {len(assessment.testTypes):<50}")
    print(f"{'Created At':<30} {str(assessment.createdAt or 'N/A'):<50}")
    print(f"{'Completed At':<30} {str(assessment.completedAt or 'N/A'):<50}")


def print_detailed_report(report: Optional[Dict[str, Any]]) -> None:
    """Print detailed assessment report in a formatted table.

    Args:
        report: Detailed report dictionary from assessment

    Example:
        assessment = client.get_assessment("assess_123")
        print_detailed_report(assessment.detailedReport)
    """
    if not report:
        print("\n⚠️  No detailed report available yet")
        return

    print_header("DETAILED REPORT")

    print(f"\n{'Metric':<40} {'Value':<40}")
    print("-" * 80)

    # Try snake_case first (current API format), then fall back to camelCase (legacy)
    overall_score = report.get("overall_score") or report.get("overallScore", "N/A")
    total_tests = report.get("total_tests") or report.get("totalTests", "N/A")
    passed_tests = report.get("passed_tests") or report.get("passedTests", "N/A")
    failed_tests = report.get("failed_tests") or report.get("failedTests", "N/A")

    print(f"{'Overall Score':<40} {overall_score:<40}")
    print(f"{'Total Tests':<40} {total_tests:<40}")
    print(f"{'Passed Tests':<40} {passed_tests:<40}")
    print(f"{'Failed Tests':<40} {failed_tests:<40}")

    # These fields may not be in the current API response, but keep for compatibility
    critical_issues = report.get("critical_issues") or report.get(
        "criticalIssues", "N/A"
    )
    high_severity = report.get("high_severity_issues") or report.get(
        "highSeverityIssues", "N/A"
    )
    medium_severity = report.get("medium_severity_issues") or report.get(
        "mediumSeverityIssues", "N/A"
    )
    low_severity = report.get("low_severity_issues") or report.get(
        "lowSeverityIssues", "N/A"
    )

    print(f"{'Critical Issues':<40} {critical_issues:<40}")
    print(f"{'High Severity Issues':<40} {high_severity:<40}")
    print(f"{'Medium Severity Issues':<40} {medium_severity:<40}")
    print(f"{'Low Severity Issues':<40} {low_severity:<40}")


def print_assessments_list(
    assessments: List[Assessment], title: str = "ALL ASSESSMENTS"
) -> None:
    """Print a list of assessments in a formatted table.

    Args:
        assessments: List of Assessment objects to display
        title: Title for the table (default: "ALL ASSESSMENTS")

    Example:
        assessments = client.list_assessments(model="my-model")
        print_assessments_list(assessments, "ASSESSMENTS FOR MY MODEL")
    """
    print_header(title)

    print(
        f"\n{'ID':<25} {'Status':<15} {'Progress':<10} {'Probes':<10} {'Priority':<10}"
    )
    print("-" * 80)
    for a in assessments:
        print(
            f"{a.id:<25} {a.status:<15} {a.progress:>8}% {len(a.testTypes):>8} {a.priority:<10}"
        )


def print_model_info(model: Model) -> None:
    """Print model information in a formatted table.

    Args:
        model: Model object to display

    Example:
        model = client.get_model("my-model")
        print_model_info(model)
    """
    print_header("MODEL INFORMATION")

    print(f"\n{'Field':<30} {'Value':<50}")
    print("-" * 80)
    print(f"{'Model ID':<30} {model.modelId:<50}")
    print(f"{'Display Name':<30} {model.displayName:<50}")
    print(f"{'Provider':<30} {model.provider:<50}")
    print(f"{'Model Name':<30} {model.modelName or 'N/A':<50}")
    print(f"{'Description':<30} {model.description or 'N/A':<50}")
    print(f"{'Active':<30} {'✅ Yes' if model.isActive else '❌ No':<50}")
    print(f"{'Test Count':<30} {model.testCount:<50}")


def progress_tracker(assessment: Assessment) -> None:
    """Simple progress callback for wait_for_completion.

    Args:
        assessment: Current assessment state

    Example:
        client.wait_for_completion(
            assessment_id,
            timeout_minutes=30,
            poll_interval=5,
            progress_callback=progress_tracker
        )
    """
    status_emoji = {"queued": "⏳", "running": "🔄", "completed": "✅", "failed": "❌"}
    emoji = status_emoji.get(assessment.status, "📊")
    print(f"   {emoji} Progress: {assessment.progress}% - Status: {assessment.status}")


def print_full_results(client: "ModelRed", assessment_id: str) -> None:
    """Print complete assessment results with all details.

    Args:
        client: ModelRed client instance
        assessment_id: Assessment ID to fetch and display

    Example:
        print_full_results(client, "assess_123")
    """
    assessment = client.get_assessment(assessment_id)

    print_assessment_summary(assessment)

    if assessment.detailedReport:
        print_detailed_report(assessment.detailedReport)

    print("\n" + "=" * 80)


# -----------------------------------------------------------------------------
# Public exports
# -----------------------------------------------------------------------------
__all__ = [
    "ModelRed",
    "AsyncModelRed",
    "ModelRedClient",
    "AsyncModelRedClient",
    "Model",
    "ModelList",
    "Assessment",
    "ModelProvider",
    "AssessmentStatus",
    "Priority",
    "ProviderConfig",
    # Display helpers
    "print_header",
    "print_assessment_summary",
    "print_detailed_report",
    "print_assessments_list",
    "print_model_info",
    "progress_tracker",
    "print_full_results",
    # Exceptions
    "ModelRedError",
    "AuthenticationError",
    "AuthorizationError",
    "SubscriptionLimitError",
    "ValidationError",
    "NotFoundError",
    "ConflictError",
    "RateLimitError",
    "ServerError",
    "NetworkError",
]
