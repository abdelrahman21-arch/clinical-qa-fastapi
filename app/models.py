from typing import List, Literal

from pydantic import BaseModel, Field


class NoteRequest(BaseModel):
    note_text: str = Field(..., min_length=1)
    note_type: str = Field(..., min_length=1)
    date_of_service: str = Field(..., min_length=1)
    date_of_injury: str = Field(..., min_length=1)


class QAFlag(BaseModel):
    severity: Literal["critical", "major", "minor"]
    why_it_matters: str = Field(..., min_length=1)
    suggested_edit: str = Field(..., min_length=1, max_length=400)


class NoteResponse(BaseModel):
    score: int = Field(..., ge=0, le=100)
    grade: Literal["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D"]
    flags: List[QAFlag] = Field(..., min_length=3, max_length=5)
