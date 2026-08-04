"""Single-pointer gesture handling for touchscreens and desktop mice."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class GestureKind(StrEnum):
    JUMP = "jump"
    ATTACK = "attack"
    DODGE = "dodge"
    SPECIAL = "special"
    TAP = "tap"


@dataclass(frozen=True, slots=True)
class Gesture:
    kind: GestureKind
    x: float
    y: float
    latency_ms: int


class GestureInput:
    """Classify one-finger gesture samples; mouse samples use this exact path."""

    def __init__(self, width: int, swipe_threshold: float = 28.0) -> None:
        self.width = width
        self.swipe_threshold = swipe_threshold
        self._start: tuple[float, float, int] | None = None
        self.last_gesture: Gesture | None = None

    def begin(self, x: float, y: float, timestamp_ms: int) -> None:
        self._start = (x, y, timestamp_ms)

    def end(self, x: float, y: float, timestamp_ms: int) -> Gesture | None:
        """Finish the active pointer gesture, returning its common classification."""
        if self._start is None:
            return None
        _start_x, start_y, start_time = self._start
        self._start = None
        delta_y = y - start_y
        if delta_y <= -self.swipe_threshold:
            kind = GestureKind.SPECIAL
        elif delta_y >= self.swipe_threshold:
            kind = GestureKind.DODGE
        elif x < self.width / 2:
            kind = GestureKind.JUMP
        else:
            kind = GestureKind.ATTACK
        self.last_gesture = Gesture(kind, x, y, max(0, timestamp_ms - start_time))
        return self.last_gesture
