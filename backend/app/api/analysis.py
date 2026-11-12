import os
import tempfile

from fastapi import File, UploadFile

from app.services.audio_processing import convert_to_model_audio
from app.services.speech_analysis_service import analyze_experience_speech
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from app.models.analysis_run import AnalysisRun
from app.schemas.analysis import AnalysisRunResponse
from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.experience import Experience
from app.models.user import User
from app.services.analysis_service import analyze_experience_text
import logging

logger = logging.getLogger(__name__)
MAX_AUDIO_SIZE = 15 * 1024 * 1024  # 15 MB

ALLOWED_AUDIO_TYPES = {
    "audio/webm",
    "audio/ogg",
    "audio/mp4",
    "audio/wav",
    "audio/x-wav",
    "audio/mpeg",
    "video/webm",
    "video/mp4",
}
router = APIRouter(
    prefix="/experiences",
    tags=["Emotion Analysis"],
)


class TextAnalysisRequest(BaseModel):
    threshold: float = Field(default=0.30, ge=0, le=1)


@router.post("/{experience_id}/analyze/text")
def analyze_text(
    experience_id: int,
    payload: TextAnalysisRequest = TextAnalysisRequest(),
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

    try:
        return analyze_experience_text(
            experience=experience,
            db=db,
            threshold=payload.threshold,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )

    except Exception as exc:
        logger.exception(
            "Text analysis failed for experience %s",
            experience_id,
        )

        raise HTTPException(
            status_code=500,
            detail="Text analysis failed. Please check backend logs.",
        ) from exc


@router.post("/{experience_id}/analyze/speech")
def analyze_speech(
    experience_id: int,
    audio: UploadFile = File(...),
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

    content_type = (audio.content_type or "").split(";")[0].strip().lower()

    if content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Unsupported recording format.",
        )

    original_path = None
    converted_path = None

    try:
        contents = audio.file.read(MAX_AUDIO_SIZE + 1)

        if not contents:
            raise HTTPException(
                status_code=400,
                detail="Recording is empty.",
            )

        if len(contents) > MAX_AUDIO_SIZE:
            raise HTTPException(
                status_code=413,
                detail="Recording exceeds the 15 MB limit.",
            )

        with tempfile.NamedTemporaryFile(
            suffix=".audio",
            delete=False,
        ) as temp_file:
            temp_file.write(contents)
            original_path = temp_file.name

        converted_path = convert_to_model_audio(original_path)

        return analyze_experience_speech(
            experience=experience,
            audio_path=converted_path,
            db=db,
        )

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Speech analysis failed for experience %s",
            experience_id,
        )

        raise HTTPException(
            status_code=500,
            detail="Speech analysis failed. Please check backend logs.",
        ) from exc

    finally:
        audio.file.close()

        for path in (original_path, converted_path):
            if path and os.path.exists(path):
                os.remove(path)

@router.get(
    "/{experience_id}/analysis-runs",
    response_model=list[AnalysisRunResponse]
)

def get_analysis_runs(
    experience_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    experience = (
        db.query(Experience)
        .filter(
            Experience.id == experience_id,
            Experience.user_id == current_user.id
        )
        .first()
    )

    if not experience:
        raise HTTPException(
            status_code=404,
            detail="Experience not found."
        )

    analysis_runs = (
        db.query(AnalysisRun)
        .options(selectinload(AnalysisRun.emotion_observations))
        .filter(AnalysisRun.experience_id == experience_id)
        .order_by(AnalysisRun.created_at.desc())
        .all()
    )

    for run in analysis_runs:
        run.is_outdated = (
            run.content_version != experience.content_version
        )

    return analysis_runs