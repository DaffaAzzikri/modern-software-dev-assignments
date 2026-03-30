"""Database repository layer."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional

from ..config import get_settings
from ..errors import DatabaseError, NotFoundError
from .models import ActionItem, Note


@contextmanager
def _get_connection() -> Iterator[sqlite3.Connection]:
    """Create a database connection with proper configuration."""
    settings = get_settings()
    data_dir = settings.get_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    try:
        conn = sqlite3.connect(str(settings.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    except sqlite3.Error as e:
        raise DatabaseError("Database connection failed", cause=e) from e


def init_db() -> None:
    """Initialize database schema. Idempotent."""
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS action_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER,
                text TEXT NOT NULL,
                done INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (note_id) REFERENCES notes(id)
            );
            """
        )
        conn.commit()


def get_note_repository() -> "NoteRepository":
    """Return the note repository instance."""
    return NoteRepository()


def get_action_item_repository() -> "ActionItemRepository":
    """Return the action item repository instance."""
    return ActionItemRepository()


class NoteRepository:
    """Repository for note operations."""

    def insert(self, content: str) -> int:
        """Insert a note and return its id."""
        with _get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO notes (content) VALUES (?)", (content,))
                return int(cursor.lastrowid)
            except sqlite3.Error as e:
                raise DatabaseError("Failed to insert note", cause=e) from e

    def get_by_id(self, note_id: int) -> Optional[Note]:
        """Get a note by id."""
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, content, created_at FROM notes WHERE id = ?",
                (note_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return Note(
                id=row["id"],
                content=row["content"],
                created_at=row["created_at"],
            )

    def get_or_raise(self, note_id: int) -> Note:
        """Get a note by id or raise NotFoundError."""
        note = self.get_by_id(note_id)
        if note is None:
            raise NotFoundError("Note", note_id)
        return note

    def list_all(self) -> list[Note]:
        """List all notes ordered by id descending."""
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, content, created_at FROM notes ORDER BY id DESC"
            )
            return [
                Note(id=r["id"], content=r["content"], created_at=r["created_at"])
                for r in cursor.fetchall()
            ]


class ActionItemRepository:
    """Repository for action item operations."""

    def _row_to_model(self, row: sqlite3.Row) -> ActionItem:
        """Convert a database row to ActionItem model."""
        return ActionItem(
            id=row["id"],
            note_id=row["note_id"],
            text=row["text"],
            done=bool(row["done"]),
            created_at=row["created_at"],
        )

    def insert_many(self, items: list[str], note_id: Optional[int] = None) -> list[int]:
        """Bulk insert action items, return list of ids."""
        with _get_connection() as conn:
            cursor = conn.cursor()
            ids: list[int] = []
            try:
                for item in items:
                    cursor.execute(
                        "INSERT INTO action_items (note_id, text) VALUES (?, ?)",
                        (note_id, item),
                    )
                    ids.append(int(cursor.lastrowid))
                return ids
            except sqlite3.Error as e:
                raise DatabaseError("Failed to insert action items", cause=e) from e

    def list_all(self, note_id: Optional[int] = None) -> list[ActionItem]:
        """List action items, optionally filtered by note_id."""
        with _get_connection() as conn:
            cursor = conn.cursor()
            if note_id is None:
                cursor.execute(
                    "SELECT id, note_id, text, done, created_at "
                    "FROM action_items ORDER BY id DESC"
                )
            else:
                cursor.execute(
                    "SELECT id, note_id, text, done, created_at "
                    "FROM action_items WHERE note_id = ? ORDER BY id DESC",
                    (note_id,),
                )
            return [self._row_to_model(r) for r in cursor.fetchall()]

    def mark_done(self, action_item_id: int, done: bool) -> None:
        """Mark an action item as done or undone. Raises NotFoundError if not found."""
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE action_items SET done = ? WHERE id = ?",
                (1 if done else 0, action_item_id),
            )
            if cursor.rowcount == 0:
                raise NotFoundError("Action item", action_item_id)
