from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.nlp import predict_emotions


router = APIRouter(
    prefix="/analysis",
    tags=["Emotion Analysis"],
)


class TextAnalysisRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10000)
    threshold: float = Field(default=0.30, ge=0, le=1)


@router.post("/text")
def analyze_text(
    payload: TextAnalysisRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        result = predict_emotions(
            text=payload.text,
            threshold=payload.threshold,
        )

        return {
            "status": "success",
            "source": "text_model",
            "suggested_emotions": result["suggested_emotions"],
            "all_scores": result["all_scores"],
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )