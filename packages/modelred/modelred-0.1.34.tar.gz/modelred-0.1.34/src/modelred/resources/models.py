"""Model metadata helpers for the ModelRed Python SDK."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..utils import parse_iso_datetime
from ..http import RequestOptions
from ..exceptions import NotFoundError
from .base import SyncAPIResource, AsyncAPIResource


@dataclass(slots=True)
class Model:
    """Lightweight representation of a registered model."""

    id: str
    model_id: str
    provider: str
    model_name: Optional[str]
    display_name: str
    description: Optional[str]
    is_active: bool
    last_tested: Optional[datetime]
    test_count: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


@dataclass(slots=True)
class ModelList:
    """List of models with pagination metadata."""

    models: List[Model]
    page: int
    page_size: int
    total: int
    total_pages: int


def parse_model(payload: Dict[str, Any]) -> Model:
    """Convert an API payload into a :class:`Model` instance."""

    return Model(
        id=payload["id"],
        model_id=payload.get("modelId", ""),
        provider=payload.get("provider", ""),
        model_name=payload.get("modelName"),
        display_name=payload.get("displayName", ""),
        description=payload.get("description"),
        is_active=payload.get("isActive", True),
        last_tested=parse_iso_datetime(payload.get("lastTested")),
        test_count=payload.get("testCount", 0),
        created_at=parse_iso_datetime(payload.get("createdAt")),
        updated_at=parse_iso_datetime(payload.get("updatedAt")),
    )


class ModelsClient(SyncAPIResource):
    """Synchronous helper for `/models` endpoints."""

    _RESOURCE_PATH = "/models"

    def list(
        self,
        *,
        page: int = 1,
        page_size: int = 100,
        search: Optional[str] = None,
        provider: Optional[str] = None,
        status: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_dir: Optional[str] = None,
        options: Optional[RequestOptions] = None,
    ) -> ModelList:
        """List all models in the organization with pagination and filtering.

        Args:
            page: Page number (default: 1)
            page_size: Number of models per page (default: 100, max: 100)
            search: Search term for filtering models by name/ID
            provider: Filter by provider (openai, anthropic, azure, huggingface, rest, bedrock, sagemaker, google, grok, openrouter)
            status: Filter by status ('active', 'inactive', 'both')
            sort_by: Sort field (displayName, provider, modelId, modelName, isActive, testCount, lastTested, createdAt)
            sort_dir: Sort direction ('asc' or 'desc')
            options: Additional request options

        Returns:
            ModelList containing models and pagination metadata
        """
        params: Dict[str, Any] = {
            "page": str(page),
            "pageSize": str(min(page_size, 100)),  # Cap at 100 as per API
        }

        if search:
            params["search"] = search
        if provider:
            params["provider"] = provider
        if status:
            params["status"] = status
        if sort_by:
            params["sortBy"] = sort_by
        if sort_dir:
            params["sortDir"] = sort_dir

        payload = self._request(
            "GET", self._RESOURCE_PATH, params=params, options=options
        )

        data = payload.get("data", [])
        models = [parse_model(item) for item in data]

        return ModelList(
            models=models,
            page=payload.get("page", page),
            page_size=payload.get("pageSize", page_size),
            total=payload.get("total", len(models)),
            total_pages=payload.get("totalPages", 1),
        )

    def retrieve(
        self, identifier: str, *, options: Optional[RequestOptions] = None
    ) -> Model:
        try:
            payload = self._request(
                "GET", f"{self._RESOURCE_PATH}/{identifier}", options=options
            )
        except NotFoundError:
            # Fallback: attempt to resolve by external modelId
            model_list = self.list(options=options)
            for model in model_list.models:
                if model.model_id == identifier:
                    return model
            raise
        return parse_model(payload.get("data", payload))

    def create(
        self,
        *,
        model_id: str,
        provider: str,
        display_name: str,
        provider_config: Dict[str, Any],
        description: Optional[str] = None,
        options: Optional[RequestOptions] = None,
    ) -> Model:
        body: Dict[str, Any] = {
            "modelId": model_id,
            "provider": provider,
            "displayName": display_name,
            "providerConfig": provider_config,
        }
        if description:
            body["description"] = description

        payload = self._request("POST", self._RESOURCE_PATH, json=body, options=options)
        return parse_model(payload.get("data", payload))

    def delete(
        self, identifier: str, *, options: Optional[RequestOptions] = None
    ) -> bool:
        model = self.retrieve(identifier, options=options)
        payload = self._request(
            "DELETE", f"{self._RESOURCE_PATH}/{model.id}", options=options
        )
        return bool(payload.get("success", True))


class AsyncModelsClient(AsyncAPIResource):
    """Async helper for `/models` endpoints."""

    _RESOURCE_PATH = "/models"

    async def list(
        self,
        *,
        page: int = 1,
        page_size: int = 100,
        search: Optional[str] = None,
        provider: Optional[str] = None,
        status: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_dir: Optional[str] = None,
        options: Optional[RequestOptions] = None,
    ) -> ModelList:
        """List all models in the organization with pagination and filtering (async).

        Args:
            page: Page number (default: 1)
            page_size: Number of models per page (default: 100, max: 100)
            search: Search term for filtering models by name/ID
            provider: Filter by provider (openai, anthropic, azure, huggingface, rest, bedrock, sagemaker, google, grok, openrouter)
            status: Filter by status ('active', 'inactive', 'both')
            sort_by: Sort field (displayName, provider, modelId, modelName, isActive, testCount, lastTested, createdAt)
            sort_dir: Sort direction ('asc' or 'desc')
            options: Additional request options

        Returns:
            ModelList containing models and pagination metadata
        """
        params: Dict[str, Any] = {
            "page": str(page),
            "pageSize": str(min(page_size, 100)),  # Cap at 100 as per API
        }

        if search:
            params["search"] = search
        if provider:
            params["provider"] = provider
        if status:
            params["status"] = status
        if sort_by:
            params["sortBy"] = sort_by
        if sort_dir:
            params["sortDir"] = sort_dir

        payload = await self._request(
            "GET", self._RESOURCE_PATH, params=params, options=options
        )

        data = payload.get("data", [])
        models = [parse_model(item) for item in data]

        return ModelList(
            models=models,
            page=payload.get("page", page),
            page_size=payload.get("pageSize", page_size),
            total=payload.get("total", len(models)),
            total_pages=payload.get("totalPages", 1),
        )

    async def retrieve(
        self, identifier: str, *, options: Optional[RequestOptions] = None
    ) -> Model:
        try:
            payload = await self._request(
                "GET", f"{self._RESOURCE_PATH}/{identifier}", options=options
            )
        except NotFoundError:
            model_list = await self.list(options=options)
            for model in model_list.models:
                if model.model_id == identifier:
                    return model
            raise
        return parse_model(payload.get("data", payload))

    async def create(
        self,
        *,
        model_id: str,
        provider: str,
        display_name: str,
        provider_config: Dict[str, Any],
        description: Optional[str] = None,
        options: Optional[RequestOptions] = None,
    ) -> Model:
        body: Dict[str, Any] = {
            "modelId": model_id,
            "provider": provider,
            "displayName": display_name,
            "providerConfig": provider_config,
        }
        if description:
            body["description"] = description

        payload = await self._request(
            "POST", self._RESOURCE_PATH, json=body, options=options
        )
        return parse_model(payload.get("data", payload))

    async def delete(
        self, identifier: str, *, options: Optional[RequestOptions] = None
    ) -> bool:
        model = await self.retrieve(identifier, options=options)
        payload = await self._request(
            "DELETE", f"{self._RESOURCE_PATH}/{model.id}", options=options
        )
        return bool(payload.get("success", True))
