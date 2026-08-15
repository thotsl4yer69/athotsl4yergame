"""Gameplay state that remains independent of Pygame rendering."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum

from .stages import PickupKind, StageDefinition


class BossPhase(IntEnum):
    GUEST_LIST = 1
    FOLLOWER_FLOOD = 2
    SPARKLER_PITCH = 3
    FINAL_RECEIPT = 4
    DEFEATED = 5


@dataclass(slots=True)
class BossController:
    """The Promoter's four-phase, damage-threshold state machine."""

    health: int = 100

    @property
    def phase(self) -> BossPhase:
        if self.health <= 0:
            return BossPhase.DEFEATED
        if self.health <= 25:
            return BossPhase.FINAL_RECEIPT
        if self.health <= 50:
            return BossPhase.SPARKLER_PITCH
        if self.health <= 75:
            return BossPhase.FOLLOWER_FLOOD
        return BossPhase.GUEST_LIST

    def disrupt(self, damage: int) -> BossPhase:
        """Apply non-graphic disruption and return the resulting phase."""
        self.health = max(0, self.health - max(0, damage))
        return self.phase


@dataclass(slots=True)
class StageRun:
    """Mutable state for one stage, including its pigeon and hidden route."""

    stage: StageDefinition
    distance: float = 0.0
    checkpoint_distance: float = 0.0
    health: int = 100
    score: int = 0
    pigeon_met: bool = False
    hidden_pickup_found: bool = False
    inventory: list[PickupKind] = field(default_factory=list)
    boss: BossController | None = None

    def __post_init__(self) -> None:
        if self.stage.boss:
            self.boss = BossController()

    def advance(self, seconds: float, speed: float = 100.0) -> None:
        self.distance += max(0.0, seconds) * speed
        if self.distance >= 1200.0:
            self.checkpoint_distance = max(self.checkpoint_distance, 600.0)

    def restore_checkpoint(self) -> None:
        """Restore the safe halfway checkpoint after a failed run."""
        self.distance = self.checkpoint_distance
        self.health = 100

    def meet_pigeon(self) -> None:
        self.pigeon_met = True
        self.score += 100

    def retrieve_hidden_pickup(self) -> bool:
        """Let Packet Pidge retrieve this stage's one hidden route reward."""
        if not self.pigeon_met or self.hidden_pickup_found:
            return False
        self.hidden_pickup_found = True
        if len(self.inventory) < 2:
            self.inventory.append(self.stage.pickup)
        self.score += 250
        return True

    def use_pickup(self) -> PickupKind | None:
        if not self.inventory:
            return None
        pickup = self.inventory.pop(0)
        if pickup is PickupKind.KRN_CAN:
            self.health = min(100, self.health + 25)
        else:
            self.score += 150
        return pickup

    def complete(self) -> bool:
        """A boss also requires all four combat-distraction phase breaks."""
        return self.distance >= 2400.0 and (self.boss is None or self.boss.health == 0)
