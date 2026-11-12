
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


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
    "embarrassed",
]


class ExperienceCreate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    input_mode: Literal["text", "voice"] = "text"
    content: str | None = None
    situation: str | None = None
    thoughts: str | None = None
    response: str | None = None

    occurred_at: datetime | None = None

    emotions: list[EmotionName] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_journal_content(self):
        if self.input_mode == "voice":
            return self

        if not any(
            value and value.strip()
            for value in [self.content, self.situation]
        ):
            raise ValueError(
                "Provide journal content or a situation."
            )

        return self


class ExperienceUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    content: str | None = None
    situation: str | None = None
    thoughts: str | None = None
    response: str | None = None
    occurred_at: datetime | None = None


class EmotionResponse(BaseModel):
    id: int
    emotion: str
    source: str
    score: float | None
    feedback_status: str

    model_config = ConfigDict(from_attributes=True)


class ExperienceResponse(BaseModel):
    id: int
    title: str | None
    content: str | None
    situation: str | None
    thoughts: str | None
    response: str | None

    input_mode: str
    content_version: int
    occurred_at: datetime
    created_at: datetime
    updated_at: datetime

    emotion_observations: list[EmotionResponse] = Field(
        default_factory=list
    )

    model_config = ConfigDict(from_attributes=True)
