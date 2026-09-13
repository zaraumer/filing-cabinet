import os
import uuid
from pathlib import Path

# Local directory for uploaded files
DEFAULT_UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"

# Supported upload types
ALLOWED_CONTENT_TYPES = {
    "application/pdf": ".pdf",
    "image/png": ".png",
    "image/jpeg": ".jpg",
}

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

# Process uploads in 1 MB chunks
CHUNK_SIZE_BYTES = 1024 * 1024


def get_upload_dir() -> Path:
    configured = os.getenv("UPLOAD_DIR")
    upload_dir = Path(configured) if configured else DEFAULT_UPLOAD_DIR

    upload_dir.mkdir(parents=True, exist_ok=True)

    return upload_dir


def build_stored_filename(content_type: str) -> str:
    return f"{uuid.uuid4().hex}{ALLOWED_CONTENT_TYPES[content_type]}"


def clean_original_filename(filename: str | None) -> str:
    if not filename:
        return "upload"

    # Remove any directory path from the filename
    base_name = filename.replace("\\", "/").split("/")[-1].strip()

    if not base_name or base_name in {".", ".."}:
        return "upload"

    return base_name[:255]


def resolve_stored_path(stored_filename: str) -> Path | None:
    upload_dir = get_upload_dir().resolve()
    candidate = (upload_dir / stored_filename).resolve()

    # Keep file access inside the upload directory
    if candidate.parent != upload_dir or not candidate.is_file():
        return None

    return candidate