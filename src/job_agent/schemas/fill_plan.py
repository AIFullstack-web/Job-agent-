from __future__ import annotations

from pydantic import BaseModel, Field


class FieldAction(BaseModel):
    label: str = Field(description="Human-visible form label")
    value: str = Field(description="Grounded value to input")
    confidence: float = Field(ge=0, le=1)
    source_experience_id: str | None = None


class FillPlan(BaseModel):
    job_url: str
    actions: list[FieldAction] = Field(default_factory=list)
    requires_human_review: bool = False
