"""Corruption-tolerant local progression storage."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile


@dataclass(frozen=True, slots=True)
class Progress:
    unlocked_stage: int = 0
    completed_ids: tuple[str, ...] = ()


def load_progress(path: Path) -> Progress:
    """Load a save or return safe defaults for missing/corrupted data."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        completed = tuple(item for item in data["completed_ids"] if isinstance(item, str))
        return Progress(max(0, int(data["unlocked_stage"])), completed)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        return Progress()


def save_progress(path: Path, progress: Progress) -> None:
    """Atomically replace the local save file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(
        {"unlocked_stage": progress.unlocked_stage, "completed_ids": list(progress.completed_ids)}
    )
    with NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as temporary:
        temporary.write(payload)
        temporary.flush()
        os.fsync(temporary.fileno())
        temporary_path = Path(temporary.name)
    os.replace(temporary_path, path)
