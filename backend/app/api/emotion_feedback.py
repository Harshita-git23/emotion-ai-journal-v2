
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.emotion import EmotionObservation
from app.models.experience import Experience
from app.models.user import User
from app.schemas.emotion import (
    EmotionFeedbackRequest,
    EmotionFeedbackResponse,
)


router = APIRouter(
    prefix="/experiences",
    tags=["Emotion Feedback"],
)


@router.patch(
    "/{experience_id}/emotions/{emotion_id}/feedback",
    response_model=EmotionFeedbackResponse,
)
def update_emotion_feedback(
    experience_id: int,
    emotion_id: int,
    payload: EmotionFeedbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    experience = (
        db.query(Experience)
        .filter(
            Experience.id == experience_id,
            Experience.user_id == current_user.id,
        )
        .first()
    )

    if not experience:
        raise HTTPException(
            status_code=404,
            detail="Experience not found",
        )

    observation = (
        db.query(EmotionObservation)
        .filter(
            EmotionObservation.id == emotion_id,
            EmotionObservation.experience_id == experience_id,
        )
        .first()
    )

    if not observation:
        raise HTTPException(
            status_code=404,
            detail="Emotion observation not found",
        )

    if observation.source == "user_reported":
        raise HTTPException(
            status_code=400,
            detail="User-reported emotions cannot be reviewed as AI suggestions.",
        )

    try:
        observation.feedback_status = payload.feedback_status
        db.commit()
        db.refresh(observation)
    except Exception:
        db.rollback()
        raise

    return observation
