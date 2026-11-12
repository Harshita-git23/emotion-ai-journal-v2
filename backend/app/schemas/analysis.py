
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AnalysisEmotionResponse(BaseModel):
    id: int
    emotion: str
    source: str
    score: float | None
    feedback_status: str

    model_config = ConfigDict(from_attributes=True)


class AnalysisRunResponse(BaseModel):
    id: int
    experience_id: int
    content_version: int
    is_outdated: bool
    model_type: str
    status: str
    model_version: str | None
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime

    emotion_observations: list[AnalysisEmotionResponse] = Field(
        default_factory=list
    )

    model_config = ConfigDict(from_attributes=True)
