"""
Multi-document YAML dumper with human-friendly formatting.

This module provides functionality for dumping multiple YAML documents
to a single stream while maintaining the human-friendly formatting
for sequences and key ordering.
"""

from io import StringIO
from typing import Any, TextIO, Iterable

import yaml
from .emitter import HumanFriendlyDumper


class MultiDocumentDumper:
    """
    Dumper for multiple YAML documents with human-friendly formatting.

    Handles document separators (---) and document end markers (...)
    while applying human-friendly formatting to each document.
    """

    def __init__(self, stream: TextIO | None = None, **dumper_kwargs: Any) -> None:
        """
        Initialize the multi-document dumper.

        Args:
            stream: Output stream (defaults to StringIO for dumps_all)
            **dumper_kwargs: Additional arguments passed to HumanFriendlyDumper
        """
        self.stream = stream or StringIO()
        self.dumper_kwargs = {
            "default_flow_style": False,
            "indent": 2,
            "sort_keys": False,
            "width": 120,
            "explicit_start": True,  # Add --- separators
            "explicit_end": False,  # Don't add ... end markers by default
            **dumper_kwargs,
        }
        self._first_document = True

    def dump_document(self, data: Any) -> None:
        """
        Dump a single document to the stream.

        Args:
            data: Python object to serialize as a YAML document
        """
        # For first document, don't add separator at start
        if self._first_document:
            # First document: no explicit start separator
            dumper_kwargs = dict(self.dumper_kwargs)
            dumper_kwargs["explicit_start"] = False
            yaml.dump(data, self.stream, Dumper=HumanFriendlyDumper, **dumper_kwargs)
            self._first_document = False
        else:
            # Subsequent documents: add newline and separator
            self.stream.write("\n---\n")
            # Don't use explicit_start for subsequent docs since we manually add separator
            dumper_kwargs = dict(self.dumper_kwargs)
            dumper_kwargs["explicit_start"] = False
            yaml.dump(data, self.stream, Dumper=HumanFriendlyDumper, **dumper_kwargs)

    def dump_all(self, documents: Iterable[Any]) -> None:
        """
        Dump multiple documents to the stream.

        Args:
            documents: Iterable of Python objects to serialize
        """
        for document in documents:
            self.dump_document(document)

    def getvalue(self) -> str:
        """
        Get the dumped YAML as a string (only works if stream is StringIO).

        Returns:
            str: The complete multi-document YAML string
        """
        if hasattr(self.stream, "getvalue"):
            return self.stream.getvalue()
        else:
            raise ValueError("Stream does not support getvalue()")


def dump_all(documents: Iterable[Any], stream: TextIO, **kwargs: Any) -> None:
    """
    Serialize multiple Python objects to YAML documents in a stream.

    Args:
        documents: Iterable of Python objects to serialize
        stream: File-like object to write to
        **kwargs: Additional arguments passed to MultiDocumentDumper

    Example:
        documents = [
            {'apiVersion': 'v1', 'kind': 'ConfigMap'},
            {'apiVersion': 'v1', 'kind': 'Service'},
            {'apiVersion': 'apps/v1', 'kind': 'Deployment'}
        ]
        with open('multi.yaml', 'w') as f:
            dump_all(documents, f)
    """
    dumper = MultiDocumentDumper(stream, **kwargs)
    dumper.dump_all(documents)


def dumps_all(documents: Iterable[Any], **kwargs: Any) -> str:
    """
    Serialize multiple Python objects to a multi-document YAML string.

    Args:
        documents: Iterable of Python objects to serialize
        **kwargs: Additional arguments passed to MultiDocumentDumper

    Returns:
        str: Multi-document YAML string

    Example:
        documents = [
            {'kind': 'ConfigMap', 'data': {'key': 'value'}},
            {'kind': 'Service', 'spec': {'ports': [80, 443]}}
        ]
        yaml_str = dumps_all(documents)
        print(yaml_str)
    """
    dumper = MultiDocumentDumper(**kwargs)
    dumper.dump_all(documents)
    return dumper.getvalue()


class KubernetesManifestDumper(MultiDocumentDumper):
    """
    Specialized multi-document dumper for Kubernetes manifests.

    Provides additional functionality specific to Kubernetes YAML files,
    such as automatic resource ordering and validation.
    """

    # Kubernetes resource ordering (CRDs and namespaces first, etc.)
    RESOURCE_ORDER = [
        "CustomResourceDefinition",
        "Namespace",
        "ServiceAccount",
        "ClusterRole",
        "ClusterRoleBinding",
        "Role",
        "RoleBinding",
        "ConfigMap",
        "Secret",
        "PersistentVolume",
        "PersistentVolumeClaim",
        "Service",
        "Ingress",
        "NetworkPolicy",
        "Deployment",
        "StatefulSet",
        "DaemonSet",
        "Job",
        "CronJob",
        "Pod",
    ]

    # Precomputed priorities for O(1) lookups instead of O(n) list.index()
    RESOURCE_PRIORITIES = {kind: i for i, kind in enumerate(RESOURCE_ORDER)}
    UNKNOWN_PRIORITY = len(RESOURCE_ORDER)

    def __init__(self, stream=None, sort_resources=True, **kwargs):
        """
        Initialize Kubernetes manifest dumper.

        Args:
            stream: Output stream
            sort_resources: Whether to sort resources by kind
            **kwargs: Additional dumper arguments
        """
        super().__init__(stream, **kwargs)
        self.sort_resources = sort_resources

    def dump_all(self, documents: Iterable[Any]) -> None:
        """
        Dump Kubernetes manifests with optional resource ordering.

        Args:
            documents: Iterable of Kubernetes resource objects
        """
        if self.sort_resources:
            documents = self._sort_resources(documents)

        super().dump_all(documents)

    def _sort_resources(self, documents):
        """
        Sort Kubernetes resources by kind according to best practices.

        Args:
            documents: Iterable of Kubernetes resource objects

        Returns:
            List of sorted documents
        """

        def get_kind_priority(doc):
            """Get sorting priority for a document based on its kind."""
            kind = doc.get("kind", "Unknown")
            return self.RESOURCE_PRIORITIES.get(kind, self.UNKNOWN_PRIORITY)

        return sorted(documents, key=get_kind_priority)


def dump_kubernetes_manifests(manifests, stream, **kwargs):
    """
    Dump Kubernetes manifests with proper resource ordering.

    Args:
        manifests: Iterable of Kubernetes resource objects
        stream: File-like object to write to
        **kwargs: Additional arguments

    Example:
        manifests = [
            {'apiVersion': 'apps/v1', 'kind': 'Deployment', ...},
            {'apiVersion': 'v1', 'kind': 'Service', ...},
            {'apiVersion': 'v1', 'kind': 'ConfigMap', ...}
        ]
        with open('k8s-manifests.yaml', 'w') as f:
            dump_kubernetes_manifests(manifests, f)
    """
    dumper = KubernetesManifestDumper(stream, **kwargs)
    dumper.dump_all(manifests)


def get_k8s_resource_prefix(document):
    """
    Get a 2-digit prefix for a Kubernetes resource based on its kind.

    Uses the same ordering as KubernetesManifestDumper to ensure consistency
    between multi-document YAML and directory output ordering.

    Args:
        document: Kubernetes resource dictionary

    Returns:
        str: 2-digit prefix (e.g. "00", "01", "99" for unknown)

    Example:
        >>> get_k8s_resource_prefix({"kind": "Namespace"})
        "01"
        >>> get_k8s_resource_prefix({"kind": "Deployment"})
        "14"
        >>> get_k8s_resource_prefix({"kind": "Unknown"})
        "99"
    """
    if not isinstance(document, dict):
        return "99"

    kind = document.get("kind", "")
    priority = KubernetesManifestDumper.RESOURCE_PRIORITIES.get(
        kind, KubernetesManifestDumper.UNKNOWN_PRIORITY
    )

    return f"{priority:02d}"


def dumps_kubernetes_manifests(manifests, **kwargs):
    """
    Serialize Kubernetes manifests to a multi-document YAML string.

    Args:
        manifests: Iterable of Kubernetes resource objects
        **kwargs: Additional arguments

    Returns:
        str: Multi-document YAML string with proper resource ordering
    """
    dumper = KubernetesManifestDumper(**kwargs)
    dumper.dump_all(manifests)
    return dumper.getvalue()
