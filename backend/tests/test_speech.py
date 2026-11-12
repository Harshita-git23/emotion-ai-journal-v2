import numpy as np
import pytest

from app.services.speech import (
    classifier,
    extract_speech_features,
    predict_speech_emotions,
)


SAMPLE_AUDIO = (
    "/Users/harshitasaxena/english-ser/"
    "data/raw/CREMA-D/data/AudioWAV/1022_ITS_ANG_XX.wav"
)


def test_extract_speech_features():
    features = extract_speech_features(SAMPLE_AUDIO)

    assert features.shape == (1, 3072)
    assert features.dtype == np.float32
    assert np.isfinite(features).all()


def test_predict_speech_emotions():
    result = predict_speech_emotions(SAMPLE_AUDIO)

    assert result["predicted_emotion"] in classifier.classes_
    assert len(result["scores"]) == 6
    assert result["model_version"] == "wav2vec2-multilayer-9-12-v1"


def test_prediction_scores_are_valid():
    result = predict_speech_emotions(SAMPLE_AUDIO)

    scores = result["scores"]

    assert all(0 <= score <= 1 for score in scores.values())
    assert sum(scores.values()) == pytest.approx(1.0, abs=1e-5)


def test_missing_audio_file():
    with pytest.raises((FileNotFoundError, OSError)):
        predict_speech_emotions("missing_audio_file.wav")