from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query

from ..db import get_action_item_repository, get_note_repository
from ..schemas import (
    ActionItemResponse,
    ExtractRequest,
    ExtractResponse,
    ExtractedItem,
    MarkDoneRequest,
    MarkDoneResponse,
)
from ..services.extract import extract_action_items, extract_action_items_llm


router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post("/extract", response_model=ExtractResponse)
def extract(request: ExtractRequest) -> ExtractResponse:
    """Extract action items from text, optionally saving as a note."""
    note_id: Optional[int] = None
    if request.save_note:
        note_id = get_note_repository().insert(request.text)

    items = extract_action_items(request.text)
    ids = get_action_item_repository().insert_many(items, note_id=note_id)
    return ExtractResponse(
        note_id=note_id,
        items=[ExtractedItem(id=i, text=t) for i, t in zip(ids, items)],
    )


@router.post("/extract-llm", response_model=ExtractResponse)
def extract_llm(request: ExtractRequest) -> ExtractResponse:
    """Extract action items from text using LLM, optionally saving as a note."""
    note_id: Optional[int] = None
    if request.save_note:
        note_id = get_note_repository().insert(request.text)

    items = extract_action_items_llm(request.text)
    ids = get_action_item_repository().insert_many(items, note_id=note_id)
    return ExtractResponse(
        note_id=note_id,
        items=[ExtractedItem(id=i, text=t) for i, t in zip(ids, items)],
    )


@router.get("", response_model=list[ActionItemResponse])
def list_all(
    note_id: Optional[int] = Query(default=None, description="Filter by note id"),
) -> list[ActionItemResponse]:
    """List all action items, optionally filtered by note_id."""
    items = get_action_item_repository().list_all(note_id=note_id)
    return [
        ActionItemResponse(
            id=item.id,
            note_id=item.note_id,
            text=item.text,
            done=item.done,
            created_at=item.created_at,
        )
        for item in items
    ]


@router.post("/{action_item_id}/done", response_model=MarkDoneResponse)
def mark_done(action_item_id: int, request: MarkDoneRequest) -> MarkDoneResponse:
    """Mark an action item as done or undone."""
    get_action_item_repository().mark_done(action_item_id, request.done)
    return MarkDoneResponse(id=action_item_id, done=request.done)


