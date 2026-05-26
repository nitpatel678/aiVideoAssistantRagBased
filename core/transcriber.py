import glob
import os
import subprocess
import wave

import requests
import whisper


# Sarvam's sync STT-translate API rejects audio longer than 30s.
# We slice each chunk into 25s pieces before sending.
SARVAM_PIECE_SECONDS = 25

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_STT_TRANSLATE_URL = "https://api.sarvam.ai/speech-to-text-translate"
SARVAM_MODEL = os.getenv("SARVAM_STT_MODEL", "saaras:v2.5")

_model = None


def is_usable_audio(chunk_path: str, min_duration_ms: int = 500) -> bool:
    if not os.path.exists(chunk_path) or os.path.getsize(chunk_path) <= 44:
        print(f"Skipping empty audio chunk: {chunk_path}")
        return False

    try:
        with wave.open(chunk_path, "rb") as audio:
            frames = audio.getnframes()
            frame_rate = audio.getframerate()
            duration_ms = (frames / float(frame_rate)) * 1000 if frame_rate else 0
    except wave.Error:
        return True

    if duration_ms < min_duration_ms:
        print(f"Skipping short audio chunk: {chunk_path}")
        return False

    return True


def segment_wav(input_path: str, seconds: int, suffix: str) -> list[str]:
    pattern = f"{input_path}_{suffix}_%03d.wav"
    command = [
        "ffmpeg",
        "-y",
        "-i",
        input_path,
        "-f",
        "segment",
        "-segment_time",
        str(seconds),
        "-c",
        "copy",
        pattern,
    ]
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    return sorted(glob.glob(pattern.replace("%03d", "*")))


def load_model():
    global _model

    if _model is None:
        print(f"Loading Whisper model: {WHISPER_MODEL} ...")
        _model = whisper.load_model(WHISPER_MODEL)
        print("Whisper model loaded.")
    return _model


def transcribe_chunk_whisper(chunk_path: str) -> str:
    if not is_usable_audio(chunk_path):
        return ""

    model = load_model()

    try:
        result = model.transcribe(
            chunk_path,
            task="transcribe",
            fp16=False,
            condition_on_previous_text=False,
        )
    except RuntimeError as exc:
        if "cannot reshape tensor of 0 elements" in str(exc):
            print(f"Skipping undecodable audio chunk: {chunk_path}")
            return ""
        raise
    return result["text"]


def _send_to_sarvam(piece_path: str) -> str:
    headers = {"api-subscription-key": SARVAM_API_KEY}

    with open(piece_path, "rb") as f:
        files = {"file": (os.path.basename(piece_path), f, "audio/wav")}
        data = {"model": SARVAM_MODEL, "with_diarization": "false"}
        response = requests.post(
            SARVAM_STT_TRANSLATE_URL,
            headers=headers,
            files=files,
            data=data,
            timeout=120,
        )

    if not response.ok:
        print(f"\nSarvam returned {response.status_code}")
        print(f"Response body: {response.text}\n")
        response.raise_for_status()

    return response.json().get("transcript", "")


def transcribe_chunk_sarvam(chunk_path: str) -> str:
    """
    Sarvam sync API only accepts <=30s audio. We split this chunk into
    25-second pieces, send each separately, and join the transcripts.
    """
    if not SARVAM_API_KEY:
        raise RuntimeError("SARVAM_API_KEY is not set in environment / .env")
    if not is_usable_audio(chunk_path):
        return ""

    full_text = ""
    piece_paths = segment_wav(chunk_path, SARVAM_PIECE_SECONDS, "sv")
    total_pieces = len(piece_paths)

    for i, piece_path in enumerate(piece_paths):
        try:
            print(f"  Sarvam piece {i + 1}/{total_pieces} ...")
            full_text += _send_to_sarvam(piece_path) + " "
        finally:
            if os.path.exists(piece_path):
                os.remove(piece_path)

    return full_text.strip()


def transcribe_chunk(chunk_path: str, language: str = "english") -> str:
    """
    Route one chunk to Whisper or Sarvam depending on language choice.
    - english: Whisper local model
    - hinglish: Sarvam, translated to English while transcribing
    """
    if language.lower() == "hinglish":
        return transcribe_chunk_sarvam(chunk_path)
    return transcribe_chunk_whisper(chunk_path)


def transcribe_all(chunks: list, language: str = "english") -> str:
    full_transcript = ""

    engine = "Sarvam AI" if language.lower() == "hinglish" else "Whisper"
    print(f"Using {engine} for transcription.")

    for i, chunk in enumerate(chunks):
        print(f"Transcribing chunk {i + 1}/{len(chunks)}...")
        text = transcribe_chunk(chunk, language=language)

        if text.strip():
            full_transcript += text + " "

    print("Transcription complete.")

    transcript = full_transcript.strip()
    if not transcript:
        raise RuntimeError(
            "No speech could be transcribed. The audio may be silent, unsupported, "
            "blocked by the source, or too noisy for the selected transcription mode."
        )

    return transcript
