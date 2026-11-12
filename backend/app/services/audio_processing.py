
import subprocess
import tempfile
from pathlib import Path


MAX_AUDIO_DURATION_SECONDS = 300


def convert_to_model_audio(input_path: str) -> str:
    """
    Convert browser-recorded audio into mono, 16 kHz PCM WAV.

    Returns the path to a temporary WAV file.
    The caller is responsible for deleting it.
    """

    output_file = tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False,
    )
    output_path = output_file.name
    output_file.close()

    command = [
        "ffmpeg",
        "-nostdin",
        "-v", "error",
        "-i", input_path,
        "-map", "0:a:0",
        "-vn",
        "-ac", "1",
        "-ar", "16000",
        "-c:a", "pcm_s16le",
        "-t", str(MAX_AUDIO_DURATION_SECONDS),
        "-y",
        output_path,
    ]

    try:
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=60,
        )

        if not Path(output_path).is_file() or Path(output_path).stat().st_size == 0:
            raise ValueError("Audio conversion produced an empty file.")

        return output_path

    except subprocess.CalledProcessError as exc:
        raise ValueError(
            "Could not decode the uploaded audio recording."
        ) from exc

    except Exception:
        Path(output_path).unlink(missing_ok=True)
        raise
