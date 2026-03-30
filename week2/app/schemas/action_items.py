"""Action items API schemas."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ExtractRequest(BaseModel):
    """Request body for extracting action items from text."""

    text: str = Field(..., min_length=1, description="Text to extract action items from")
    save_note: bool = Field(default=False, description="Whether to save the text as a note")


class ExtractedItem(BaseModel):
    """Single extracted action item with assigned id."""

    id: int
    text: str


class ExtractResponse(BaseModel):
    """Response from action item extraction."""

    note_id: Optional[int] = None
    items: list[ExtractedItem]


class ActionItemResponse(BaseModel):
    """Response schema for a single action item."""

    id: int
    note_id: Optional[int] = None
    text: str
    done: bool
    created_at: str

    model_config = {"from_attributes": True}


class MarkDoneRequest(BaseModel):
    """Request body for marking an action item done/undone."""

    done: bool = Field(default=True, description="Whether the item is done")


class MarkDoneResponse(BaseModel):
    """Response after marking an action item done/undone."""

    id: int
    done: bool
