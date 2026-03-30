"""Note API schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class NoteCreateRequest(BaseModel):
    """Request body for creating a note."""

    content: str = Field(..., min_length=1, description="Note content")


class NoteResponse(BaseModel):
    """Response schema for a single note."""

    id: int
    content: str
    created_at: str

    model_config = {"from_attributes": True}
