"""Database domain models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Note:
    """Note domain model."""

    id: int
    content: str
    created_at: str


@dataclass
class ActionItem:
    """Action item domain model."""

    id: int
    note_id: Optional[int]
    text: str
    done: bool
    created_at: str
