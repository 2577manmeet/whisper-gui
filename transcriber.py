from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Callable, Optional, Dict, Any, List

import whisper


def check_ffmpeg() -> bool:
    """Return True if ffmpeg is available on PATH."""
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except Exception:
        return False


def format_timestamp(seconds: float) -> str:
    """Format seconds as SRT timestamp: HH:MM:SS,mmm."""
    if seconds < 0:
        seconds = 0
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02}:{minutes:02}:{secs:06.3f}".replace(".", ",")


def segments_to_srt(segments: List[Dict[str, Any]]) -> str:
    """Convert segment dicts into SRT string."""
    lines = []
    for i, seg in enumerate(segments, start=1):
        start = format_timestamp(seg["start"])
        end = format_timestamp(seg["end"])
        text = seg["text"].strip()
        lines.append(str(i))
        lines.append(f"{start} --> {end}")
        lines.append(text)
        lines.append("")
    return "\n".join(lines)


def transcribe_file(
    file_path: str,
    model_name: str = "base",
    language: Optional[str] = None,
    log: Optional[Callable[[str], None]] = None,
    progress: Optional[Callable[[int, int], None]] = None,
) -> Dict[str, Any]:
    """
    Transcribe a single media file with Whisper (transcribe only).

    progress(current, total) is called while building segments/SRT,
    based on segment count.
    """

    def _log(msg: str):
        if log:
            log(msg)

    def _progress(cur: int, total: int):
        if progress:
            progress(cur, total)

    src = Path(file_path)
    if not src.is_file():
        raise FileNotFoundError(f"Input file not found: {src}")

    if not check_ffmpeg():
        raise RuntimeError(
            "ffmpeg is not available on PATH. "
            "Install it and make sure 'ffmpeg' runs in your terminal."
        )

    _log(f"Loading Whisper model '{model_name}'...")
    model = whisper.load_model(model_name)

    opts: Dict[str, Any] = {}
    if language:
        opts["language"] = language

    _log("Transcribing… this may take a while on CPU.")
    result = model.transcribe(str(src), **opts)

    raw_segments = result.get("segments", []) or []
    total_segments = len(raw_segments) or 1  # avoid division by zero
    segments: List[Dict[str, Any]] = []

    # Build our segments and report progress based on count
    for idx, seg in enumerate(raw_segments, start=1):
        segments.append(
            {
                "start": float(seg.get("start", 0.0)),
                "end": float(seg.get("end", 0.0)),
                "text": str(seg.get("text", "")).strip(),
            }
        )
        _progress(idx, total_segments)

    text = result.get("text", "").strip()

    out_dir = Path("output")
    out_dir.mkdir(exist_ok=True)

    base_name = src.stem
    txt_path = out_dir / f"{base_name}.txt"
    srt_path = out_dir / f"{base_name}.srt"

    txt_path.write_text(text, encoding="utf-8")
    srt_content = segments_to_srt(segments)
    srt_path.write_text(srt_content, encoding="utf-8")

    _log(f"Saved transcript: {txt_path}")
    _log(f"Saved subtitles: {srt_path}")

    # Ensure progress ends at 100%
    _progress(total_segments, total_segments)

    return {
        "text": text,
        "segments": segments,
        "output_txt": txt_path,
        "output_srt": srt_path,
    }
