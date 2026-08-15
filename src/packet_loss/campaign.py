"""Campaign flow, isolated from the renderer for deterministic headless tests."""

from __future__ import annotations

from dataclasses import dataclass, field

from .entities import StageRun
from .input import Gesture, GestureKind
from .persistence import Progress
from .stages import DISTRICT_1_STAGES


@dataclass(slots=True)
class Campaign:
    """District 1 stage selection, completion, and in-stage interactions."""

    progress: Progress = field(default_factory=Progress)
    stage_index: int | None = None
    run: StageRun | None = None

    def select_stage(self, stage_index: int) -> bool:
        if not 0 <= stage_index < len(DISTRICT_1_STAGES) or stage_index > self.progress.unlocked_stage:
            return False
        self.stage_index = stage_index
        self.run = StageRun(DISTRICT_1_STAGES[stage_index])
        return True

    def handle_gesture(self, gesture: Gesture) -> None:
        """Apply the context-sensitive action used by touch and mouse input."""
        if self.run is None:
            return
        if gesture.kind is GestureKind.ATTACK and self.run.distance >= 400:
            self.run.meet_pigeon()
        elif gesture.kind is GestureKind.SPECIAL:
            self.run.retrieve_hidden_pickup()
            if self.run.boss is not None and self.run.pigeon_met:
                self.run.boss.disrupt(25)
        elif gesture.kind is GestureKind.DODGE:
            self.run.health = min(100, self.run.health + 2)

    def restore_checkpoint(self) -> bool:
        if self.run is None or self.run.checkpoint_distance == 0:
            return False
        self.run.restore_checkpoint()
        return True

    def finish_current_stage(self) -> bool:
        """Record a completed stage and unlock only its immediate successor."""
        if self.run is None or self.stage_index is None or not self.run.complete():
            return False
        completed = tuple(dict.fromkeys((*self.progress.completed_ids, self.run.stage.id)))
        self.progress = Progress(
            unlocked_stage=min(len(DISTRICT_1_STAGES) - 1, self.stage_index + 1),
            completed_ids=completed,
        )
        return True
