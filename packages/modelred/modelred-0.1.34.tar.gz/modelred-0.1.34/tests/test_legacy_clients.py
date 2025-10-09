"""Unit tests for legacy ModelRed wrappers to ensure they delegate to the new clients."""

from __future__ import annotations

import asyncio
import pathlib
import sys
import unittest
from typing import Any, List, Optional

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[3]
SRC_PATH = PROJECT_ROOT / "packages" / "python" / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from modelred import AsyncModelRed, ModelRed, Priority  # type: ignore[import]
from modelred.resources.assessments import (  # type: ignore[import]
    Assessment as ResourceAssessment,
    AssessmentPriority,
    AssessmentStatus,
)
from modelred.resources.models import Model as ResourceModel  # type: ignore[import]
from modelred.resources.probes import Probe, ProbeIndex  # type: ignore[import]


class StubModelsClient:
    def __init__(self) -> None:
        self.created_payloads: List[dict[str, Any]] = []
        self.deleted: Optional[str] = None

    def create(
        self,
        *,
        model_id: str,
        provider: str,
        display_name: str,
        provider_config: dict[str, Any],
        description: Optional[str] = None,
    ) -> ResourceModel:
        self.created_payloads.append(
            {
                "model_id": model_id,
                "provider": provider,
                "display_name": display_name,
                "provider_config": provider_config,
                "description": description,
            }
        )
        return ResourceModel(
            id="model_123",
            model_id=model_id,
            provider=provider,
            model_name=provider_config.get("model_name"),
            display_name=display_name,
            description=description,
            is_active=True,
            last_tested=None,
            test_count=1,
            created_at=None,
            updated_at=None,
        )

    def list(self, *, limit: Optional[int] = None) -> list[ResourceModel]:
        models = [
            ResourceModel(
                id="model_1",
                model_id="alpha",
                provider="openai",
                model_name="gpt",
                display_name="Alpha",
                description=None,
                is_active=True,
                last_tested=None,
                test_count=3,
                created_at=None,
                updated_at=None,
            ),
            ResourceModel(
                id="model_2",
                model_id="beta",
                provider="anthropic",
                model_name="claude",
                display_name="Beta",
                description=None,
                is_active=False,
                last_tested=None,
                test_count=5,
                created_at=None,
                updated_at=None,
            ),
        ]
        return models[:limit] if limit is not None else models

    def retrieve(self, identifier: str) -> ResourceModel:
        return ResourceModel(
            id=identifier,
            model_id=identifier,
            provider="openai",
            model_name="gpt",
            display_name="Alpha",
            description=None,
            is_active=True,
            last_tested=None,
            test_count=3,
            created_at=None,
            updated_at=None,
        )

    def delete(self, identifier: str) -> bool:
        self.deleted = identifier
        return True


class StubAssessmentsClient:
    def __init__(self) -> None:
        self.created: list[dict[str, Any]] = []

    def create(
        self,
        *,
        model: str,
        test_types: List[str],
        priority: AssessmentPriority,
    ) -> ResourceAssessment:
        self.created.append(
            {"model": model, "test_types": test_types, "priority": priority}
        )
        return ResourceAssessment(
            id="a_123",
            model_id=model,
            status=AssessmentStatus.QUEUED,
            test_types=list(test_types),
            priority=priority,
            progress=0,
            created_at=None,
            completed_at=None,
            detailed_report=None,
        )

    def retrieve(self, assessment_id: str) -> ResourceAssessment:
        return ResourceAssessment(
            id=assessment_id,
            model_id="alpha",
            status=AssessmentStatus.COMPLETED,
            test_types=["jailbreak"],
            priority=AssessmentPriority.NORMAL,
            progress=100,
            created_at=None,
            completed_at=None,
            detailed_report=None,
        )

    def list(self, *, limit: Optional[int] = None) -> list[ResourceAssessment]:
        assessments = [
            self.retrieve("a_1"),
            self.retrieve("a_2"),
        ]
        return assessments[:limit] if limit is not None else assessments

    def wait_for_completion(
        self,
        assessment_id: str,
        *,
        timeout_seconds: int,
        poll_interval: int,
        progress_callback=None,
    ) -> ResourceAssessment:
        assessment = self.retrieve(assessment_id)
        if progress_callback:
            progress_callback(assessment)
        return assessment


class StubProbesClient:
    def list(
        self,
        *,
        category: Optional[str] = None,
        tier: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> ProbeIndex:
        probes = [
            Probe(
                id="p1",
                key="probe.one",
                display_name="Probe One",
                description="",
                estimated_time="1m",
                tags=[],
                category=category or "general",
                tier=tier or "free",
                severity=severity or "low",
                is_active=True,
                version="1",
            )
        ]
        return ProbeIndex(
            probes=probes,
            probe_categories={},
            tier_definitions={},
            severity_levels={},
        )


class StubSyncCompositeClient:
    def __init__(self) -> None:
        self.models = StubModelsClient()
        self.assessments = StubAssessmentsClient()
        self.probes = StubProbesClient()
        self.closed = False

    api_key = "mr_stub"

    def redacted_api_key(self) -> str:
        return "mr_s…stub"

    def close(self) -> None:
        self.closed = True


class StubAsyncModelsClient(StubModelsClient):
    async def create(self, **kwargs: Any) -> ResourceModel:  # type: ignore[override]
        return super().create(**kwargs)

    async def list(self, *, limit: Optional[int] = None) -> list[ResourceModel]:  # type: ignore[override]
        return super().list(limit=limit)

    async def retrieve(self, identifier: str) -> ResourceModel:  # type: ignore[override]
        return super().retrieve(identifier)

    async def delete(self, identifier: str) -> bool:  # type: ignore[override]
        return super().delete(identifier)


class StubAsyncAssessmentsClient(StubAssessmentsClient):
    async def create(self, **kwargs: Any) -> ResourceAssessment:  # type: ignore[override]
        return super().create(**kwargs)

    async def retrieve(self, assessment_id: str) -> ResourceAssessment:  # type: ignore[override]
        return super().retrieve(assessment_id)

    async def list(self, *, limit: Optional[int] = None) -> list[ResourceAssessment]:  # type: ignore[override]
        return super().list(limit=limit)

    async def wait_for_completion(
        self,
        assessment_id: str,
        *,
        timeout_seconds: int,
        poll_interval: int,
        progress_callback=None,
    ) -> ResourceAssessment:  # type: ignore[override]
        assessment = await self.retrieve(assessment_id)
        if progress_callback:
            progress_callback(assessment)
        return assessment


class StubAsyncProbesClient(StubProbesClient):
    async def list(self, **kwargs: Any) -> ProbeIndex:  # type: ignore[override]
        return super().list(**kwargs)


class StubAsyncCompositeClient:
    def __init__(self) -> None:
        self.models = StubAsyncModelsClient()
        self.assessments = StubAsyncAssessmentsClient()
        self.probes = StubAsyncProbesClient()
        self.closed = False

    api_key = "mr_stub"

    def redacted_api_key(self) -> str:
        return "mr_s…stub"

    async def close(self) -> None:
        self.closed = True

    async def __aenter__(self) -> "StubAsyncCompositeClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()


class ModelRedDelegationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.stub = StubSyncCompositeClient()
        self.client = ModelRed(_client=self.stub)

    def test_list_models_converts_to_legacy_dataclass(self) -> None:
        models = self.client.list_models()
        self.assertEqual(len(models), 2)
        first = models[0]
        self.assertEqual(first.modelId, "alpha")
        self.assertEqual(first.displayName, "Alpha")

    def test_create_assessment_normalises_priority(self) -> None:
        assessment = self.client.create_assessment(
            model="alpha",
            test_types=["jailbreak"],
            priority="high",
        )
        self.assertEqual(assessment.priority, Priority.HIGH)
        self.assertEqual(self.stub.assessments.created[0]["priority"], Priority.HIGH)

    def test_get_probes_delegates_to_resource_client(self) -> None:
        probes_index = self.client.get_probes(tier="free")
        self.assertEqual(len(probes_index.probes), 1)
        self.assertTrue(self.stub.closed is False)

    def test_close_closes_underlying_client(self) -> None:
        self.client.close()
        self.assertTrue(self.stub.closed)


class AsyncModelRedDelegationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.stub = StubAsyncCompositeClient()
        self.client = AsyncModelRed(_client=self.stub)

    async def test_list_models(self) -> None:
        models = await self.client.list_models()
        self.assertEqual(models[1].modelId, "beta")

    async def test_wait_for_completion_wraps_callback(self) -> None:
        called = asyncio.Event()

        def on_progress(assessment):
            self.assertEqual(assessment.status, AssessmentStatus.COMPLETED)
            called.set()

        result = await self.client.wait_for_completion(
            "a_123",
            timeout_minutes=1,
            poll_interval=1,
            progress_callback=on_progress,
        )
        await asyncio.wait_for(called.wait(), timeout=1)
        self.assertEqual(result.status, AssessmentStatus.COMPLETED)

    async def asyncTearDown(self) -> None:
        await self.client.close()
        self.assertTrue(self.stub.closed)


if __name__ == "__main__":
    unittest.main()
