from __future__ import annotations

from pydantic import BaseModel, Field


# ── Request models ──────────────────────────────────────────────


class NoteCreate(BaseModel):
    content: str = Field(min_length=1)


class ExtractRequest(BaseModel):
    text: str = Field(min_length=1)
    save_note: bool = False


class MarkDoneRequest(BaseModel):
    done: bool = True


# ── Response models ─────────────────────────────────────────────


class NoteResponse(BaseModel):
    id: int
    content: str
    created_at: str


class ActionItemBrief(BaseModel):
    id: int
    text: str


class ExtractResponse(BaseModel):
    note_id: int | None
    items: list[ActionItemBrief]


class ActionItemResponse(BaseModel):
    id: int
    note_id: int | None
    text: str
    done: bool
    created_at: str


class MarkDoneResponse(BaseModel):
    id: int
    done: bool
