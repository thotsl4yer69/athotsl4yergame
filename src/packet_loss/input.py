"""Single-touch gesture classification for XPT2046 and desktop mouse input."""

from __future__ import annotations

from dataclasses import dataclass

from .model import Action


@dataclass(frozen=True, slots=True)
class TouchSample:
    start_x: int
    start_y: int
    end_x: int
    end_y: int
    duration_ms: int


def classify_touch(sample: TouchSample, width: int = 480, swipe_px: int = 42) -> Action:
    dx = sample.end_x - sample.start_x
    dy = sample.end_y - sample.start_y
    if abs(dy) >= swipe_px and abs(dy) > abs(dx):
        return Action.SPECIAL if dy < 0 else Action.DODGE
    if sample.duration_ms <= 450 and abs(dx) < swipe_px and abs(dy) < swipe_px:
        return Action.JUMP if sample.end_x < width // 2 else Action.ATTACK
    return Action.NONE
