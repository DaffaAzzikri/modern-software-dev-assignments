from datetime import datetime

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100, description="Category name")


class CategoryRead(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NoteCreate(BaseModel):
    title: str = Field(min_length=3, max_length=100, description="Note title")
    content: str = Field(min_length=1, description="Note content")
    category_id: int | None = None


class NoteRead(BaseModel):
    id: int
    title: str
    content: str
    category_id: int | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotePatch(BaseModel):
    title: str | None = Field(None, min_length=3, max_length=100, description="Note title")
    content: str | None = Field(None, min_length=1, description="Note content")
    category_id: int | None = None


class ActionItemCreate(BaseModel):
    description: str


class ActionItemRead(BaseModel):
    id: int
    description: str
    completed: bool
    assignee: str | None = None
    priority: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ActionItemPatch(BaseModel):
    description: str | None = None
    completed: bool | None = None
    assignee: str | None = None
    priority: str | None = None