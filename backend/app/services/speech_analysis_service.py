
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.analysis_run import AnalysisRun
from app.models.emotion import EmotionObservation
from app.models.experience import Experience
from app.services.speech import predict_speech_emotions


MODEL_VERSION = "wav2vec2-multilayer-9-12-v1"


def analyze_experience_speech(
    experience: Experience,
    audio_path: str,
    db: Session,
) -> dict:
    """
    Analyze a saved journal experience using speech.

    Each attempt creates a separate AnalysisRun.
    Previous observations are never deleted.
    """

    experience_id = experience.id
    content_version = experience.content_version

    started_at = datetime.now(timezone.utc)

    run = AnalysisRun(
        experience_id=experience_id,
        content_version=content_version,
        model_type="speech",
        status="running",
        model_version=MODEL_VERSION,
        started_at=started_at,
    )

    db.add(run)
    db.flush()

    try:
        result = predict_speech_emotions(audio_path)

        observations = [
            EmotionObservation(
                experience_id=experience_id,
                analysis_run_id=run.id,
                emotion=emotion,
                source="speech_model",
                score=score,
                feedback_status="pending",
            )
            for emotion, score in result["scores"].items()
        ]

        db.add_all(observations)

        run.status = "completed"
        run.completed_at = datetime.now(timezone.utc)

        db.commit()

        return {
            "analysis_run_id": run.id,
            "status": run.status,
            "model_type": run.model_type,
            "model_version": run.model_version,
            "predicted_emotion": result["predicted_emotion"],
            "scores": result["scores"],
        }

    except Exception as exc:
        db.rollback()

        failed_at = datetime.now(timezone.utc)

        failed_run = AnalysisRun(
            experience_id=experience_id,
            content_version=content_version,
            model_type="speech",
            status="failed",
            model_version=MODEL_VERSION,
            error_message=str(exc)[:2000],
            started_at=started_at,
            completed_at=failed_at,
        )

        db.add(failed_run)
        db.commit()

        raise
