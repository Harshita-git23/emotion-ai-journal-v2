from pathlib import Path

import joblib
import librosa
import numpy as np
import torch

from transformers import AutoFeatureExtractor, Wav2Vec2Model


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_DIR = PROJECT_ROOT / "ml" / "models"

MODEL_NAME = "facebook/wav2vec2-base"
CLASSIFIER_PATH = MODEL_DIR / "speech_multilayer_best.joblib"

LAYERS = [9, 10, 11, 12]

DEVICE = torch.device(
    "mps" if torch.backends.mps.is_available() else "cpu"
)

EMOTIONS = [
    "angry",
    "disgust",
    "fearful",
    "happy",
    "neutral",
    "sad",
]


feature_extractor = AutoFeatureExtractor.from_pretrained(MODEL_NAME)

encoder = Wav2Vec2Model.from_pretrained(MODEL_NAME)

encoder.to(DEVICE)
encoder.eval()

for parameter in encoder.parameters():
    parameter.requires_grad = False


classifier = joblib.load(CLASSIFIER_PATH)


def extract_speech_features(audio_path: str) -> np.ndarray:
    audio_path = Path(audio_path)

    if not audio_path.is_file():
        raise FileNotFoundError(
            f"Audio file not found: {audio_path}"
        )

    waveform, sr = librosa.load(
        audio_path,
        sr=16000,
        mono=True,
    )

    waveform = waveform.astype(np.float32)

    inputs = feature_extractor(
        waveform,
        sampling_rate=sr,
        return_tensors="pt",
    )

    input_values = inputs["input_values"].to(DEVICE)

    with torch.inference_mode():
        outputs = encoder(
            input_values,
            output_hidden_states=True,
        )

        hidden_states = outputs.hidden_states

        embeddings = [
            hidden_states[layer].mean(dim=1).squeeze(0).cpu().numpy()
            for layer in LAYERS
        ]

    combined = np.concatenate(embeddings).astype(np.float32)

    if combined.shape[0] != 3072:
        raise ValueError(
            f"Expected 3072 features, got {combined.shape[0]}"
        )

    return combined.reshape(1, -1)


def predict_speech_emotions(audio_path: str) -> dict:
    features = extract_speech_features(audio_path)

    probabilities = classifier.predict_proba(features)[0]
    classes = classifier.classes_

    scores = {
        str(emotion): float(score)
        for emotion, score in zip(classes, probabilities)
    }

    predicted_emotion = str(classes[np.argmax(probabilities)])

    return {
        "predicted_emotion": predicted_emotion,
        "scores": scores,
        "model_version": "wav2vec2-multilayer-9-12-v1",
    }