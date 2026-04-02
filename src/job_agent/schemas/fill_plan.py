from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class FieldAction(BaseModel):
    label: str = Field(description="Human-visible form label")
    value: str = Field(description="Grounded value to input")
    confidence: float = Field(ge=0, le=1)
    source_experience_id: str | None = None
    field_type: Literal["text", "textarea", "select", "radio", "checkbox", "date", "file"] = "text"
    options: list[str] = Field(default_factory=list)


class FillPlan(BaseModel):
    job_url: str
    actions: list[FieldAction] = Field(default_factory=list)
    requires_human_review: bool = False
    submit_after_fill: bool = False
