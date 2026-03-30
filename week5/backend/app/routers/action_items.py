from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ActionItem
from ..schemas import ActionItemCreate, ActionItemRead, BulkCompleteRequest

router = APIRouter(prefix="/action-items", tags=["action_items"])


@router.get("/", response_model=list[ActionItemRead])
def list_items(
    completed: bool | None = Query(None, description="Filter by completion status"),
    db: Session = Depends(get_db),
) -> list[ActionItemRead]:
    stmt = select(ActionItem)
    if completed is not None:
        stmt = stmt.where(ActionItem.completed == completed)
    rows = db.execute(stmt).scalars().all()
    return [ActionItemRead.model_validate(row) for row in rows]


@router.post("/", response_model=ActionItemRead, status_code=201)
def create_item(payload: ActionItemCreate, db: Session = Depends(get_db)) -> ActionItemRead:
    item = ActionItem(description=payload.description, completed=False)
    db.add(item)
    db.flush()
    db.refresh(item)
    return ActionItemRead.model_validate(item)


@router.post("/bulk-complete", response_model=list[ActionItemRead])
def bulk_complete(
    payload: BulkCompleteRequest, db: Session = Depends(get_db)
) -> list[ActionItemRead]:
    """Mark multiple action items as completed in a single transaction.

    Raises 400 if no IDs are provided, or 404 (with full rollback) if any ID
    does not exist.
    """
    if not payload.ids:
        raise HTTPException(status_code=400, detail="No IDs provided")

    items = []
    for item_id in payload.ids:
        item = db.get(ActionItem, item_id)
        if not item:
            raise HTTPException(
                status_code=404, detail=f"Action item {item_id} not found"
            )
        item.completed = True
        items.append(item)

    db.flush()
    for item in items:
        db.refresh(item)
    return [ActionItemRead.model_validate(item) for item in items]


@router.put("/{item_id}/complete", response_model=ActionItemRead)
def complete_item(item_id: int, db: Session = Depends(get_db)) -> ActionItemRead:
    item = db.get(ActionItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    item.completed = True
    db.add(item)
    db.flush()
    db.refresh(item)
    return ActionItemRead.model_validate(item)
