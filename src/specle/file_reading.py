"""Safe text reads for target-supplied validation inputs."""

from __future__ import annotations

import anyio


async def read_regular_text(path: anyio.Path) -> str:
    """Asynchronously read text only when *path* resolves to a regular file."""
    return (await read_regular_bytes(path)).decode()


async def read_regular_bytes(path: anyio.Path) -> bytes:
    """Asynchronously read bytes only when *path* resolves to a regular file."""
    if await path.is_symlink() and not await path.exists():
        raise OSError(f"{path}: not a regular file")
    if not await path.exists():
        raise FileNotFoundError(path)
    if not await path.is_file():
        raise OSError(f"{path}: not a regular file")
    return await path.read_bytes()
