import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ActionItem
from ..schemas import ActionItemCreate, ActionItemPatch, ActionItemRead

router = APIRouter(prefix="/action-items", tags=["action_items"])


def extract_assignee(description: str) -> tuple[Optional[str], str]:
    """Extract assignee from description (e.g., @john) and return (assignee, cleaned_description)."""
    match = re.search(r'@(\w+)', description)
    assignee = match.group(1) if match else None
    cleaned = re.sub(r'@\w+', '', description) if match else description
    return assignee, cleaned.strip()


def extract_priority(description: str) -> tuple[Optional[str], str]:
    """Extract priority from description (e.g., [HIGH]) and return (priority, cleaned_description)."""
    match = re.search(r'\[([A-Za-z]+)\]', description)
    priority = match.group(1).upper() if match else None
    cleaned = re.sub(r'\[[A-Za-z]+\]', '', description) if match else description
    return priority, cleaned.strip()


@router.get("/", response_model=list[ActionItemRead])
def list_items(
    db: Session = Depends(get_db),
    completed: Optional[bool] = None,
    skip: int = 0,
    limit: int = Query(50, le=200),
    sort: str = Query("-created_at"),
) -> list[ActionItemRead]:
    stmt = select(ActionItem)
    if completed is not None:
        stmt = stmt.where(ActionItem.completed.is_(completed))

    sort_field = sort.lstrip("-")
    order_fn = desc if sort.startswith("-") else asc
    if hasattr(ActionItem, sort_field):
        stmt = stmt.order_by(order_fn(getattr(ActionItem, sort_field)))
    else:
        stmt = stmt.order_by(desc(ActionItem.created_at))

    rows = db.execute(stmt.offset(skip).limit(limit)).scalars().all()
    return [ActionItemRead.model_validate(row) for row in rows]


@router.post("/", response_model=ActionItemRead, status_code=201)
def create_item(payload: ActionItemCreate, db: Session = Depends(get_db)) -> ActionItemRead:
    # Extract assignee and priority from description
    assignee, description_after_assignee = extract_assignee(payload.description)
    priority, cleaned_description = extract_priority(description_after_assignee)
    
    # Create ActionItem with extracted values
    item = ActionItem(
        description=cleaned_description,
        completed=False,
        assignee=assignee,
        priority=priority
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return ActionItemRead.model_validate(item)


@router.put("/{item_id}/complete", response_model=ActionItemRead)
def complete_item(item_id: int, db: Session = Depends(get_db)) -> ActionItemRead:
    item = db.get(ActionItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    item.completed = True
    db.add(item)
    db.commit()
    db.refresh(item)
    return ActionItemRead.model_validate(item)


@router.patch("/{item_id}", response_model=ActionItemRead)
def patch_item(item_id: int, payload: ActionItemPatch, db: Session = Depends(get_db)) -> ActionItemRead:
    item = db.get(ActionItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    if payload.description is not None:
        # Re-extract if description is patched
        assignee, description_after_assignee = extract_assignee(payload.description)
        priority, cleaned_description = extract_priority(description_after_assignee)
        item.description = cleaned_description
        item.assignee = assignee
        item.priority = priority
    if payload.completed is not None:
        item.completed = payload.completed
    if payload.assignee is not None:
        item.assignee = payload.assignee
    if payload.priority is not None:
        item.priority = payload.priority
    db.add(item)
    db.commit()
    db.refresh(item)
    return ActionItemRead.model_validate(item)