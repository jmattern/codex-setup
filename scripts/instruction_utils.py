#!/usr/bin/env python3
"""Shared helpers for building and installing the instruction bundle."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parent.parent
RULES = (
    "session.md",
    "engineering.md",
    "communication.md",
    "permissions.md",
    "orchestration.md",
)
OUTPUT = ROOT / "build" / "AGENTS.md"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_content() -> bytes:
    parts = [
        "# Global Codex instructions\n\n"
        "This file is assembled from the maintained instruction sources. "
        "It is self-contained; repository-specific conventions belong in project guidance.\n"
    ]
    for name in RULES:
        source = ROOT / "rules" / name
        parts.append(f"\n---\n\n<!-- Source: rules/{name} -->\n\n")
        parts.append(source.read_text(encoding="utf-8").rstrip() + "\n")
    return "".join(parts).encode("utf-8")


def atomic_write(path: Path, data: bytes, mode: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if mode is not None:
            temp_path.chmod(mode)
        os.replace(temp_path, path)
    except BaseException:
        try:
            temp_path.unlink()
        except FileNotFoundError:
            pass
        raise

