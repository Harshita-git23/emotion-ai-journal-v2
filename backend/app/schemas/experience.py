
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


EmotionName = Literal[
    "happy",
    "calm",
    "excited",
    "grateful",
    "sad",
    "anxious",
    "angry",
    "overwhelmed",
    "lonely",
    "confused",
    "frustrated",
    "hopeful",
    "embarrassed"
]


class ExperienceCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    situation: str = Field(min_length=1)
    thoughts: str | None = None
    response: str | None = None
    helped: str | None = None
    occurred_at: datetime
    emotions: list[EmotionName] = Field(default_factory=list, max_length=12)


class EmotionResponse(BaseModel):
    emotion: str
    source: str
    score: float | None
    is_confirmed: bool

    model_config = ConfigDict(from_attributes=True)


class ExperienceResponse(BaseModel):
    id: int
    title: str
    situation: str
    thoughts: str | None
    response: str | None
    helped: str | None
    occurred_at: datetime
    created_at: datetime
    emotions: list[EmotionResponse]

    model_config = ConfigDict(from_attributes=True)
