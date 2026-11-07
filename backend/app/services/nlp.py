from pathlib import Path
import pickle

import numpy as np


# --------------------------------------------------
# Model configuration
# --------------------------------------------------

GO_EMOTIONS_LABELS = [
    "admiration",
    "amusement",
    "anger",
    "annoyance",
    "approval",
    "caring",
    "confusion",
    "curiosity",
    "desire",
    "disappointment",
    "disapproval",
    "disgust",
    "embarrassment",
    "excitement",
    "fear",
    "gratitude",
    "grief",
    "joy",
    "love",
    "nervousness",
    "optimism",
    "pride",
    "realization",
    "relief",
    "remorse",
    "sadness",
    "surprise",
    "neutral",
]


# Project root / ml / models
PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_DIR = PROJECT_ROOT / "ml" / "models"


# --------------------------------------------------
# Load models once when the service is imported
# --------------------------------------------------

def load_models():
    required_files = [
        "emotion_model_2.pkl",
        "emotion_vectorizer.pkl",
        "emotion_mlb.pkl",
    ]

    for filename in required_files:
        if not (MODEL_DIR / filename).exists():
            raise FileNotFoundError(
                f"Missing model file: {MODEL_DIR / filename}"
            )

    with open(MODEL_DIR / "emotion_model_2.pkl", "rb") as f:
        model = pickle.load(f)

    with open(MODEL_DIR / "emotion_vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)

    with open(MODEL_DIR / "emotion_mlb.pkl", "rb") as f:
        mlb = pickle.load(f)

    # Ensure the numeric model outputs match the
    # official GO Emotions label ordering.
    expected_ids = np.arange(len(GO_EMOTIONS_LABELS))

    if not np.array_equal(mlb.classes_, expected_ids):
        raise ValueError(
            "Unexpected emotion label IDs. "
            "Check the training label mapping."
        )

    if len(model.estimators_) != len(GO_EMOTIONS_LABELS):
        raise ValueError("Model does not contain 28 emotion estimators.")

    return model, vectorizer


emotion_model, emotion_vectorizer = load_models()


# --------------------------------------------------
# Text emotion prediction
# --------------------------------------------------

def predict_emotions(text: str, threshold: float = 0.30):
    """
    Predict emotion labels from journal text.

    Returns independent model scores.
    These scores are not percentages that sum to 100.
    """

    if not isinstance(text, str) or not text.strip():
        raise ValueError("Text cannot be empty.")

    if not 0 <= threshold <= 1:
        raise ValueError("Threshold must be between 0 and 1.")

    features = emotion_vectorizer.transform([text.strip()])

    probabilities = emotion_model.predict_proba(features)[0]

    if len(probabilities) != len(GO_EMOTIONS_LABELS):
        raise ValueError("Unexpected number of model predictions.")

    all_scores = [
        {
            "emotion": emotion,
            "score": round(float(score), 4),
            "source": "text_model",
        }
        for emotion, score in zip(
            GO_EMOTIONS_LABELS,
            probabilities
        )
    ]

    all_scores.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    suggested_emotions = [
        item for item in all_scores
        if item["score"] >= threshold
    ]

    return {
        "suggested_emotions": suggested_emotions,
        "all_scores": all_scores,
    }