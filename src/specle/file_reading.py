"""Safe text reads for target-supplied validation inputs."""

from __future__ import annotations

from pathlib import Path


def read_regular_text(path: Path) -> str:
    """Read text only when *path* resolves to a regular file."""
    return read_regular_bytes(path).decode()


def read_regular_bytes(path: Path) -> bytes:
    """Read bytes only when *path* resolves to a regular file."""
    if path.is_symlink() and not path.exists():
        raise OSError(f"{path}: not a regular file")
    if not path.exists():
        raise FileNotFoundError(path)
    if not path.is_file(follow_symlinks=True):
        raise OSError(f"{path}: not a regular file")
    return path.read_bytes()
