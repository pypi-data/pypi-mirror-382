from fastapi import APIRouter, HTTPException
from pathlib import Path
import os

from backend.rendering import render_text_content

router = APIRouter(prefix="/api/files", tags=["files"])

# Maximum file size to read (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

def get_project_root() -> Path:
    """Get configurable project root. Defaults to current working directory."""
    # Can be configured via environment variable
    root = os.getenv("VIBE_READER_ROOT", os.getcwd())
    return Path(root).resolve()

def resolve_and_validate_path(path: str, must_be_dir: bool = False, must_be_file: bool = False) -> Path:
    """Resolve path and validate it's within project root."""
    project_root = get_project_root()
    target_path = Path(path).resolve()

    # Security check: ensure path is within project root
    try:
        target_path.relative_to(project_root)
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied: path outside project root")

    if not target_path.exists():
        raise HTTPException(status_code=404, detail="Path not found")

    if must_be_dir and not target_path.is_dir():
        raise HTTPException(status_code=400, detail="Path is not a directory")

    if must_be_file and target_path.is_dir():
        raise HTTPException(status_code=400, detail="Path is a directory")

    return target_path

@router.get("")
async def list_files(path: str = "."):
    """List files in a directory"""
    try:
        target_path = resolve_and_validate_path(path, must_be_dir=True)
        project_root = get_project_root()

        files = []
        for item in sorted(target_path.iterdir()):
            # Return paths relative to project root for display
            try:
                relative_path = item.relative_to(project_root)
                display_path = str(relative_path)
            except ValueError:
                display_path = str(item)

            files.append({
                "name": item.name,
                "path": display_path,
                "is_dir": item.is_dir()
            })
        return files
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content")
async def get_file_content(path: str, highlight: bool = True):
    """Get content of a file"""
    try:
        target_path = resolve_and_validate_path(path, must_be_file=True)
        project_root = get_project_root()

        # Check file size before reading
        file_size = target_path.stat().st_size
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"File too large (max {MAX_FILE_SIZE // 1024 // 1024}MB)")

        content = target_path.read_text()
        render_result = render_text_content(target_path, content, enable_highlighting=highlight)

        # Return path relative to project root
        try:
            relative_path = target_path.relative_to(project_root)
            display_path = str(relative_path)
        except ValueError:
            display_path = str(target_path)

        return {
            "path": display_path,
            "render_mode": render_result.mode,
            "html": render_result.html,
            "metadata": render_result.metadata,
        }
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Cannot read binary file")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
