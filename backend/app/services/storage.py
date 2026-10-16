import os
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile


# Local development defaults to storage/uploads.
# In production, set UPLOAD_DIR to the Render Persistent Disk mount path.
UPLOAD_DIR = Path(
    os.getenv("UPLOAD_DIR", "storage/uploads")
)


async def save_upload(file: UploadFile) -> tuple[str, int]:
    """Save an uploaded file and return its path and size."""

    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    extension = Path(file.filename or "").suffix
    unique_name = f"{uuid4().hex}{extension}"
    file_path = UPLOAD_DIR / unique_name

    size = 0

    try:
        with file_path.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                output.write(chunk)
                size += len(chunk)
    except Exception:
        file_path.unlink(missing_ok=True)
        raise
    finally:
        await file.close()

    return str(file_path.resolve()), size


def delete_file(file_path: str) -> None:
    """Delete a stored file if it exists."""

    path = Path(file_path)

    if path.exists() and path.is_file():
        path.unlink()


save_upload_file = save_upload