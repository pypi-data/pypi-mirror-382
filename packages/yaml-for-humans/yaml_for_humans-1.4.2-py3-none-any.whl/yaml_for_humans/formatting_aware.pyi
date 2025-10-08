"""
Type stubs for formatting_aware module.
"""

from typing import Any, Dict, List, Optional, Union, IO
import yaml
from yaml.composer import Composer
from yaml.constructor import SafeConstructor
from yaml.resolver import Resolver

class FormattingMetadata:
    """Stores formatting information for YAML nodes."""

    empty_lines_before: List[str]  # Now stores actual line content (empty lines and comments)
    empty_lines_after: int

    def __init__(
        self, empty_lines_before: Optional[Union[int, List[str]]] = ..., empty_lines_after: int = ...
    ) -> None: ...
    @property
    def empty_lines_before_count(self) -> int: ...  # Backward compatibility property
    def __repr__(self) -> str: ...

class FormattingAwareComposer(Composer):
    """Composer that captures empty line and comment information in nodes."""

    _end_line_cache: Dict[int, int]
    _metadata_pool: List[FormattingMetadata]
    _raw_lines: Optional[List[str]]  # For comment extraction

    def __init__(self) -> None: ...
    def _initialize_raw_lines(self, stream: Any) -> None: ...
    def _extract_lines_before(self, start_line: int, previous_end_line: int) -> List[str]: ...
    def compose_mapping_node(self, anchor: Optional[str]) -> yaml.MappingNode: ...  # type: ignore[override]
    def compose_sequence_node(self, anchor: Optional[str]) -> yaml.SequenceNode: ...  # type: ignore[override]
    def _add_mapping_formatting_metadata(self, node: yaml.MappingNode) -> None: ...
    def _add_sequence_formatting_metadata(self, node: yaml.SequenceNode) -> None: ...
    def _get_node_end_line(self, node: yaml.Node) -> int: ...
    def _calculate_end_line(self, node: yaml.Node) -> int: ...
    def _get_metadata_object(self, **kwargs: Any) -> FormattingMetadata: ...
    def _set_metadata(self, node: yaml.Node, **kwargs: Any) -> None: ...

class FormattingAwareConstructor(SafeConstructor):
    """Constructor that creates FormattingAware containers."""

    def construct_mapping(  # type: ignore[override]
        self, node: yaml.MappingNode, deep: bool = ...
    ) -> "FormattingAwareDict": ...
    def construct_sequence(
        self, node: yaml.SequenceNode, deep: bool = ...
    ) -> "FormattingAwareList": ...

class FormattingAwareDict(Dict[str, Any]):
    """Dictionary that preserves formatting metadata."""

    _formatting_metadata: Optional[FormattingMetadata]

    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class FormattingAwareList(List[Any]):
    """List that preserves formatting metadata."""

    _formatting_metadata: Optional[FormattingMetadata]

    def __init__(self, *args: Any) -> None: ...

class FormattingAwareLoader(
    FormattingAwareConstructor,
    FormattingAwareComposer,
    yaml.loader.SafeLoader,
    Resolver,
):
    """YAML loader that captures formatting metadata."""

    def __init__(self, stream: Union[str, bytes, IO[str], IO[bytes]]) -> None: ...
