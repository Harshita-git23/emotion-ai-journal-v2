
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.emotion import EmotionObservation
from app.models.experience import Experience
from app.models.user import User
from app.schemas.experience import (
    ExperienceCreate,
    ExperienceUpdate,
    ExperienceResponse,
)


router = APIRouter(prefix="/experiences", tags=["Experiences"])


def get_owned_experience(
    experience_id: int,
    user_id: int,
    db: Session,
) -> Experience:
    experience = (
        db.query(Experience)
        .options(selectinload(Experience.emotion_observations))
        .filter(
            Experience.id == experience_id,
            Experience.user_id == user_id,
        )
        .first()
    )

    if not experience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found",
        )

    return experience


@router.post(
    "/",
    response_model=ExperienceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_experience(
    data: ExperienceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Save a journal entry immediately.

    AI analysis is deliberately not triggered here.
    """

    experience = Experience(
        user_id=current_user.id,
        title=data.title,
        content=data.content,
        situation=data.situation,
        thoughts=data.thoughts,
        response=data.response,
        input_mode=data.input_mode,
        occurred_at=data.occurred_at or datetime.now(timezone.utc),
    )

    try:
        db.add(experience)
        db.flush()

        # Store the user's own emotion selections separately.
        unique_emotions = dict.fromkeys(data.emotions)

        for emotion in unique_emotions:
            observation = EmotionObservation(
                experience_id=experience.id,
                emotion=emotion,
                source="user_reported",
                score=None,
                feedback_status="not_applicable",
            )
            db.add(observation)

        db.commit()

    except Exception:
        db.rollback()
        raise

    return get_owned_experience(
        experience_id=experience.id,
        user_id=current_user.id,
        db=db,
    )


@router.get(
    "/",
    response_model=list[ExperienceResponse],
)
def get_experiences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Experience)
        .options(selectinload(Experience.emotion_observations))
        .filter(Experience.user_id == current_user.id)
        .order_by(Experience.occurred_at.desc())
        .all()
    )


@router.get(
    "/{experience_id}",
    response_model=ExperienceResponse,
)
def get_experience(
    experience_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_owned_experience(
        experience_id=experience_id,
        user_id=current_user.id,
        db=db,
    )


@router.patch(
    "/{experience_id}",
    response_model=ExperienceResponse,
)
def update_experience(
    experience_id: int,
    data: ExperienceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    experience = get_owned_experience(
        experience_id=experience_id,
        user_id=current_user.id,
        db=db,
    )

    updates = data.model_dump(exclude_unset=True)

    if (
        "occurred_at" in updates
        and updates["occurred_at"] is None
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="occurred_at cannot be null",
        )

    # Validate the resulting entry, not just the changed fields.
    new_content = updates.get("content", experience.content)
    new_situation = updates.get("situation", experience.situation)

    if not any(
        value and value.strip()
        for value in [new_content, new_situation]
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="An entry must contain content or a situation.",
        )

    analysis_fields = {
        "content",
        "situation",
        "thoughts",
        "response",
    }

    content_changed = any(
        field in updates and updates[field] != getattr(experience, field)
        for field in analysis_fields
    )

    if content_changed:
        experience.content_version += 1

    for field, value in updates.items():
        setattr(experience, field, value)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return get_owned_experience(
        experience_id=experience.id,
        user_id=current_user.id,
        db=db,
    )


@router.delete(
    "/{experience_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_experience(
    experience_id: int,
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found",
        )

    db.delete(experience)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
