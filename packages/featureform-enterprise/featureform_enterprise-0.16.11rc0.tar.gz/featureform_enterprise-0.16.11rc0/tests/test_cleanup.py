import logging
import sys
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Iterable, List, Set, Tuple
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, "client/src/")

from featureform.enums import ResourceType
from featureform.proto import metadata_pb2
from featureform.register import ResourceClient
from featureform.resources import FeatureView, ResourceVariant


@dataclass
class DummyVariant(ResourceVariant):
    name: str
    variant: str
    resource_type: ResourceType

    def get_resource_type(self) -> ResourceType:
        return self.resource_type

    def to_key(self) -> Tuple[ResourceType, str, str]:
        return self.resource_type, self.name, self.variant

    def name_variant(self) -> Tuple[str, str]:
        return self.name, self.variant


class DummyResourceState:
    def __init__(self, resources: List[object]):
        self._resources = resources

    def sorted_list(self) -> List[object]:
        return list(self._resources)


class DummyStub:
    def __init__(
            self,
            feature_views: Iterable[object],
            sources: Iterable[object],
            features: Iterable[object],
            labels: Iterable[object],
            training_sets: Iterable[object],
    ):
        self._feature_views = list(feature_views)
        self._sources = list(sources)
        self._features = list(features)
        self._labels = list(labels)
        self._training_sets = list(training_sets)
        self.requests: List[metadata_pb2.ListRequest] = []

    def ListFeatureViews(self, request: metadata_pb2.ListRequest):
        self.requests.append(request)
        return self._feature_views

    def ListSources(self, request: metadata_pb2.ListRequest):
        self.requests.append(request)
        return self._sources

    def ListFeatures(self, request: metadata_pb2.ListRequest):
        self.requests.append(request)
        return self._features

    def ListLabels(self, request: metadata_pb2.ListRequest):
        self.requests.append(request)
        return self._labels

    def ListTrainingSets(self, request: metadata_pb2.ListRequest):
        self.requests.append(request)
        return self._training_sets


@pytest.fixture
def resource_client():
    client = ResourceClient.__new__(ResourceClient)
    logger = MagicMock()
    logger.level = logging.INFO
    client.logger = logger
    client._stub = MagicMock()
    return client


def test_cleanup_invalid_mode_returns_empty_set(resource_client):
    resource_state = MagicMock()
    result = resource_client._cleanup(resource_state, mode="partial")

    assert result == set()
    resource_client.logger.error.assert_called_once_with(
        "Only 'total' mode is currently supported, got 'partial'"
    )


def test_cleanup_calls_execute_with_collected_resources(resource_client):
    resource_state = MagicMock()
    resources_to_keep: Set[Tuple[ResourceType, str, str]] = {
        (ResourceType.FEATURE_VARIANT, "keep", "v1")
    }
    resources_to_delete = [(ResourceType.FEATURE_VARIANT, "name", "v1")]

    resource_client._get_resources_to_keep = MagicMock(return_value=resources_to_keep)
    resource_client._find_resources_to_delete = MagicMock(
        return_value=resources_to_delete
    )
    resource_client._execute_cleanup = MagicMock(return_value={("deleted",)})

    result = resource_client._cleanup(
        resource_state, mode="total", asynchronous=True
    )

    assert result == {("deleted",)}
    resource_client._get_resources_to_keep.assert_called_once_with(resource_state)
    resource_client._find_resources_to_delete.assert_called_once_with(
        resources_to_keep
    )
    resource_client._execute_cleanup.assert_called_once_with(
        resources_to_delete, True
    )


def test_get_resources_to_keep_collects_variants_and_feature_views(resource_client):
    kept_feature = DummyVariant(
        name="feature", variant="v1", resource_type=ResourceType.FEATURE_VARIANT
    )
    kept_view = FeatureView(name="view", provider="offline")
    ignored_resource = object()

    state = DummyResourceState([kept_feature, kept_view, ignored_resource])

    result = resource_client._get_resources_to_keep(state)

    assert result == {
        (ResourceType.FEATURE_VARIANT, "feature", "v1"),
        (ResourceType.FEATURE_VIEW, "view", ""),
    }


def test_find_resources_to_delete_orders_feature_views_first(resource_client):
    stub = DummyStub(
        feature_views=[
            SimpleNamespace(name="fv_keep"),
            SimpleNamespace(name="fv_delete"),
        ],
        sources=[SimpleNamespace(name="source", variants=["keep", "delete"])],
        features=[
            SimpleNamespace(name="feature_keep", variants=["v1"]),
            SimpleNamespace(name="feature_delete", variants=["v1"]),
        ],
        labels=[SimpleNamespace(name="label", variants=["v1"])],
        training_sets=[SimpleNamespace(name="training", variants=["v1"])],
    )
    resource_client._stub = stub

    resources_to_keep = {
        (ResourceType.FEATURE_VIEW, "fv_keep", ""),
        (ResourceType.SOURCE_VARIANT, "source", "keep"),
        (ResourceType.FEATURE_VARIANT, "feature_keep", "v1"),
    }

    result = resource_client._find_resources_to_delete(resources_to_keep)

    assert result == [
        (ResourceType.FEATURE_VIEW, "fv_delete", ""),
        (ResourceType.SOURCE_VARIANT, "source", "delete"),
        (ResourceType.FEATURE_VARIANT, "feature_delete", "v1"),
        (ResourceType.LABEL_VARIANT, "label", "v1"),
        (ResourceType.TRAININGSET_VARIANT, "training", "v1"),
    ]


def test_execute_cleanup_skips_duplicates_and_missing_resources(resource_client):
    resource_client.delete = MagicMock(
        side_effect=[
            Exception("Could not find resource to delete fv_missing"),
            (("FEATURE_VIEW", "fv_present", ""), "task-2"),
        ]
    )
    resource_client.prune = MagicMock(
        return_value={("FEATURE_VARIANT", "feature", "v1"): "task-3"}
    )

    resources_to_delete = [
        (ResourceType.FEATURE_VIEW, "fv_missing", ""),
        (ResourceType.FEATURE_VIEW, "fv_present", ""),
        (ResourceType.FEATURE_VARIANT, "feature", "v1"),
    ]

    result = resource_client._execute_cleanup(resources_to_delete, asynchronous=False)

    assert result == {
        ("FEATURE_VIEW", "fv_present", ""),
        ("FEATURE_VARIANT", "feature", "v1"),
    }
    assert resource_client.delete.call_count == 2
    assert resource_client.prune.call_count == 1
    first_call_kwargs = resource_client.delete.call_args_list[0].kwargs
    assert first_call_kwargs["asynchronous"] is False
    assert first_call_kwargs["resource_type"] == ResourceType.FEATURE_VIEW
    prune_call_kwargs = resource_client.prune.call_args_list[0].kwargs
    assert prune_call_kwargs["asynchronous"] is False
    assert prune_call_kwargs["resource_type"] == ResourceType.FEATURE_VARIANT
    resource_client.logger.debug.assert_called_once()
