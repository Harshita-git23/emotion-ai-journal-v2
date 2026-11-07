
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models.user import User
from app.models.experience import Experience
from app.models.emotion import EmotionObservation
from app.schemas.experience import (
    ExperienceCreate,
    ExperienceResponse
)
from app.api.dependencies import get_current_user


router = APIRouter(prefix="/experiences", tags=["Experiences"])


@router.post("/", response_model=ExperienceResponse, status_code=201)
def create_experience(
    data: ExperienceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    experience = Experience(
        user_id=current_user.id,
        title=data.title,
        situation=data.situation,
        thoughts=data.thoughts,
        response=data.response,
        helped=data.helped,
        occurred_at=data.occurred_at
    )

    db.add(experience)
    db.flush()

    for emotion in set(data.emotions):
        observation = EmotionObservation(
            experience_id=experience.id,
            emotion=emotion,
            source="user_reported",
            score=None,
            is_confirmed=True
        )
        db.add(observation)

    db.commit()

    saved = (
        db.query(Experience)
        .options(joinedload(Experience.emotions))
        .filter(
            Experience.id == experience.id,
            Experience.user_id == current_user.id
        )
        .first()
    )

    return saved


@router.get("/", response_model=list[ExperienceResponse])
def get_experiences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(Experience)
        .options(joinedload(Experience.emotions))
        .filter(Experience.user_id == current_user.id)
        .order_by(Experience.occurred_at.desc())
        .all()
    )


@router.get("/{experience_id}", response_model=ExperienceResponse)
def get_experience(
    experience_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    experience = (
        db.query(Experience)
        .options(joinedload(Experience.emotions))
        .filter(
            Experience.id == experience_id,
            Experience.user_id == current_user.id
        )
        .first()
    )

    if not experience:
        raise HTTPException(
            status_code=404,
            detail="Experience not found"
        )

    return experience


@router.delete("/{experience_id}", status_code=204)
def delete_experience(
    experience_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    experience = db.query(Experience).filter(
        Experience.id == experience_id,
        Experience.user_id == current_user.id
    ).first()

    if not experience:
        raise HTTPException(
            status_code=404,
            detail="Experience not found"
        )

    db.delete(experience)
    db.commit()

    return None
