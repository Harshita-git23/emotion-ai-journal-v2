
from typing import Literal

from pydantic import BaseModel, ConfigDict


class EmotionFeedbackRequest(BaseModel):
    feedback_status: Literal["confirmed", "rejected"]


class EmotionFeedbackResponse(BaseModel):
    id: int
    experience_id: int
    emotion: str
    source: str
    score: float | None
    feedback_status: str

    model_config = ConfigDict(from_attributes=True)
