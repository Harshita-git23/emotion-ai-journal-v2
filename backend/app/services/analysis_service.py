
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.analysis_run import AnalysisRun
from app.models.emotion import EmotionObservation
from app.models.experience import Experience
from app.services.nlp import predict_emotions


MODEL_VERSION = "go-emotions-tfidf-ovr-v1"
now = datetime.now(timezone.utc)

def analyze_experience_text(
    experience: Experience,
    db: Session,
    threshold: float = 0.30,
) -> dict:
    """
    Analyze a saved journal experience.

    Each attempt gets its own AnalysisRun.
    Previous observations are never deleted.
    """

    text_parts = [
        experience.content,
        experience.situation,
        experience.thoughts,
        experience.response,
    ]

    text = "\n".join(
        part.strip()
        for part in text_parts
        if part and part.strip()
    )

    if not text:
        raise ValueError("This journal entry has no text to analyze.")

    run = AnalysisRun(
        experience_id=experience.id,
        content_version=experience.content_version,
        model_type="text",
        status="running",
        model_version=MODEL_VERSION,
        started_at=now,
    )

    db.add(run)
    db.flush()

    try:
        result = predict_emotions(
            text=text,
            threshold=threshold,
        )

        observations = [
            EmotionObservation(
                experience_id=experience.id,
                analysis_run_id=run.id,
                emotion=item["emotion"],
                source="text_model",
                score=item["score"],
                feedback_status="pending",
            )
            for item in result["suggested_emotions"]
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
            "suggested_emotions": result["suggested_emotions"],
            "all_scores": result["all_scores"],
        }

    except Exception as exc:
        db.rollback()

        failed_run = AnalysisRun(
            experience_id=experience.id,
            model_type="text",
            status="failed",
            model_version=MODEL_VERSION,
            error_message=str(exc)[:2000],
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            content_version=experience.content_version,
        )

        db.add(failed_run)
        db.commit()

        raise
