"""Shared models."""

from abc import ABC
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

from .util import remove_punctuation


@dataclass
class MatchEntity:
    """Named entity that has been matched from a {slot_list}"""

    name: str
    """Name of the entity."""

    value: Any
    """Value of the entity."""

    text: str
    """Original value text."""

    metadata: Optional[Dict[str, Any]] = None
    """Entity metadata."""

    is_wildcard: bool = False
    """True if entity is a wildcard."""

    is_wildcard_open: bool = True
    """While True, wildcard can continue matching."""

    is_wildcard_end_of_word: bool = True
    """True if wildcard {list} is followed by whitespace."""

    @property
    def text_clean(self) -> str:
        """Trimmed text with punctuation removed."""
        return remove_punctuation(self.text).strip()


@dataclass
class UnmatchedEntity(ABC):
    """Base class for unmatched entities."""

    name: str
    """Name of entity that should have matched."""


@dataclass
class UnmatchedTextEntity(UnmatchedEntity):
    """Text entity that should have matched."""

    text: str
    """Text that failed to match slot values."""

    is_open: bool = True
    """While True, entity can continue matching."""


@dataclass
class UnmatchedRangeEntity(UnmatchedEntity):
    """Range entity that should have matched."""

    value: Union[int, float]
    """Value of entity that was out of range."""


@dataclass
class MatchCapture:
    """Captured text from {list_name:@capture_name}"""

    name: str
    """Name of capture."""

    text: str
    """Original value text."""
