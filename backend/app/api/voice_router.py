"""Voice endpoints to be mounted in the existing FastAPI app."""
import asyncio
import os
import subprocess
import tempfile
import uuid
from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.graph_adapter import GraphNotConfigured, answer_with_existing_graph

router = APIRouter(prefix="/api/voice", tags=["HERwell Voice"])
MAX_AUDIO_BYTES = 20 * 1024 * 1024
VOICE_DIR = Path(os.getenv("HERWELL_VOICE_TMP", tempfile.gettempdir())) / "herwell_voice"
VOICE_DIR.mkdir(parents=True, exist_ok=True)
_whisper_model = None
_whisper_model_name = None


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    session_id: str = Field(default="herwell-session", min_length=1, max_length=128)


def _get_whisper_model():
    global _whisper_model, _whisper_model_name
    from faster_whisper import WhisperModel
    name = os.getenv("WHISPER_MODEL", "base")
    if _whisper_model is None or _whisper_model_name != name:
        _whisper_model = WhisperModel(name, device="cpu", compute_type="int8")
        _whisper_model_name = name
    return _whisper_model


def _transcribe(path: str) -> str:
    model = _get_whisper_model()
    segments, _ = model.transcribe(path, beam_size=1, vad_filter=True)
    return " ".join(segment.text.strip() for segment in segments).strip()


def _synthesize(text: str, output_path: Path) -> None:
    binary = os.getenv("PIPER_BIN", "piper")
    model = os.getenv("PIPER_MODEL", "").strip()
    if not model or not Path(model).is_file():
        raise RuntimeError("PIPER_MODEL must point to a downloaded local Piper .onnx model.")
    try:
        proc = subprocess.run(
            [binary, "--model", model, "--output_file", str(output_path)],
            input=text, text=True, capture_output=True, timeout=120, check=False
        )
    except FileNotFoundError as exc:
        raise RuntimeError("Piper executable not found; configure PIPER_BIN.") from exc
    if proc.returncode or not output_path.exists() or output_path.stat().st_size == 0:
        raise RuntimeError((proc.stderr or proc.stdout or "Piper failed")[-1000:])


@router.post("/transcribe")
async def transcribe_voice(file: UploadFile = File(...)):
    suffix = Path(file.filename or "recording.webm").suffix.lower()
    if suffix not in {".webm", ".wav", ".mp3", ".m4a", ".ogg", ".mp4"}:
        suffix = ".webm"
    path = VOICE_DIR / f"input-{uuid.uuid4().hex}{suffix}"
    try:
        data = await file.read()
        if not data:
            raise HTTPException(400, "Audio file is empty.")
        if len(data) > MAX_AUDIO_BYTES:
            raise HTTPException(413, "Audio file exceeds 20 MB.")
        path.write_bytes(data)
        text = await asyncio.to_thread(_transcribe, str(path))
        if not text:
            raise HTTPException(422, "No speech detected. Try again.")
        return {"text": text, "engine": "faster-whisper-local"}
    except HTTPException:
        raise
    except ImportError as exc:
        raise HTTPException(503, "Install faster-whisper in the existing backend environment.") from exc
    except Exception as exc:
        raise HTTPException(500, f"Local transcription failed: {exc}") from exc
    finally:
        path.unlink(missing_ok=True)


@router.post("/chat")
async def chat_with_voice(payload: ChatRequest):
    try:
        answer = await asyncio.to_thread(
            answer_with_existing_graph, payload.message.strip(), payload.session_id
        )
    except GraphNotConfigured as exc:
        raise HTTPException(503, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(502, f"HERwell graph failed: {exc}") from exc

    # Return text response instead of audio for now (TTS not configured)
    from fastapi.responses import JSONResponse
    return JSONResponse({
        "answer": answer,
        "text": answer
    }, headers={"X-Herwell-Answer": answer, "Cache-Control": "no-store"})
