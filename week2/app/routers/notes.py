from __future__ import annotations

from fastapi import APIRouter

from ..db import get_note_repository
from ..schemas import NoteCreateRequest, NoteResponse


router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("", response_model=list[NoteResponse])
def list_notes() -> list[NoteResponse]:
    """Retrieve all notes."""
    notes = get_note_repository().list_all()
    return [
        NoteResponse(id=n.id, content=n.content, created_at=n.created_at)
        for n in notes
    ]


@router.post("", response_model=NoteResponse)
def create_note(request: NoteCreateRequest) -> NoteResponse:
    """Create a new note."""
    repo = get_note_repository()
    note_id = repo.insert(request.content)
    note = repo.get_or_raise(note_id)
    return NoteResponse(id=note.id, content=note.content, created_at=note.created_at)


@router.get("/{note_id}", response_model=NoteResponse)
def get_single_note(note_id: int) -> NoteResponse:
    """Get a note by id."""
    note = get_note_repository().get_or_raise(note_id)
    return NoteResponse(id=note.id, content=note.content, created_at=note.created_at)


