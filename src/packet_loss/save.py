"""Atomic local progression and high-score persistence."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
import os
from pathlib import Path
import tempfile
from typing import Any


@dataclass(slots=True)
class SaveData:
    version: int = 1
    high_score: int = 0
    unlocked_stages: list[str] = field(default_factory=lambda: ["d1_queue"])
    completed_stages: list[str] = field(default_factory=list)
    pidge_chips: int = 0
    pidge_scout: int = 0
    pidge_thief: int = 0
    pidge_menace: int = 0
    pidge_oracle: int = 0

    def unlock(self, stage_id: str) -> None:
        if stage_id and stage_id not in self.unlocked_stages:
            self.unlocked_stages.append(stage_id)

    def complete(self, stage_id: str, *, next_stage: str | None, score: int) -> None:
        if stage_id not in self.completed_stages:
            self.completed_stages.append(stage_id)
        if next_stage and next_stage != "district_2":
            self.unlock(next_stage)
        self.high_score = max(self.high_score, score)


def default_save_path() -> Path:
    root = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return root / "thotsl4yer69" / "save.json"


def _from_dict(raw: Any) -> SaveData:
    if not isinstance(raw, dict):
        raise ValueError("save root must be an object")
    save = SaveData()
    save.version = int(raw.get("version", 1))
    save.high_score = max(0, int(raw.get("high_score", 0)))
    save.unlocked_stages = [str(value) for value in raw.get("unlocked_stages", ["d1_queue"])]
    save.completed_stages = [str(value) for value in raw.get("completed_stages", [])]
    save.pidge_chips = max(0, int(raw.get("pidge_chips", 0)))
    for attr in ("pidge_scout", "pidge_thief", "pidge_menace", "pidge_oracle"):
        setattr(save, attr, max(0, min(3, int(raw.get(attr, 0)))))
    if "d1_queue" not in save.unlocked_stages:
        save.unlocked_stages.insert(0, "d1_queue")
    return save


def load_save(path: str | Path | None = None) -> SaveData:
    save_path = Path(path) if path is not None else default_save_path()
    try:
        return _from_dict(json.loads(save_path.read_text(encoding="utf-8")))
    except (FileNotFoundError, json.JSONDecodeError, OSError, TypeError, ValueError):
        return SaveData()


def write_save(save: SaveData, path: str | Path | None = None) -> Path:
    save_path = Path(path) if path is not None else default_save_path()
    save_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(asdict(save), indent=2, sort_keys=True) + "\n"
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=save_path.parent, delete=False, prefix=".save-"
        ) as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
            temporary = Path(handle.name)
        os.replace(temporary, save_path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink(missing_ok=True)
    return save_path
