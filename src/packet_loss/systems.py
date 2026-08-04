"""Shared pickup and Packet Pidge companion systems."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PickupKind(str, Enum):
    KRN_CAN = "krn_can"
    THINKING_DUST = "thinking_dust"
    SERVO_KEBAB = "servo_kebab"
    PIDGE_CHIPS = "pidge_chips"
    MYSTERY_WRISTBAND = "mystery_wristband"


class PidgeBranch(str, Enum):
    SCOUT = "scout"
    THIEF = "thief"
    MENACE = "menace"
    ORACLE = "oracle"


@dataclass(slots=True)
class EffectState:
    confidence_ms: int = 0
    thinking_ms: int = 0
    paranoia: int = 0
    digestion_ms: int = 0
    score_multiplier: float = 1.0

    def update(self, dt_ms: int) -> None:
        self.confidence_ms = max(0, self.confidence_ms - dt_ms)
        self.thinking_ms = max(0, self.thinking_ms - dt_ms)
        self.digestion_ms = max(0, self.digestion_ms - dt_ms)
        if self.thinking_ms <= 0:
            self.score_multiplier = 1.0


@dataclass(slots=True)
class PickupResult:
    health_delta: int = 0
    vibe_delta: int = 0
    chips_delta: int = 0
    message: str = ""


def apply_pickup(kind: PickupKind, effects: EffectState, *, dust_uses: int = 0) -> PickupResult:
    """Apply deterministic arcade effects; callers clamp health and Vibe."""

    if kind is PickupKind.KRN_CAN:
        effects.confidence_ms = max(effects.confidence_ms, 9000)
        return PickupResult(health_delta=18, vibe_delta=8, message="BEER CONFIDENCE ONLINE")
    if kind is PickupKind.THINKING_DUST:
        effects.thinking_ms = max(effects.thinking_ms, 7000)
        effects.score_multiplier = 2.0
        effects.paranoia = min(3, dust_uses // 2)
        return PickupResult(vibe_delta=12, message="THE ALGORITHM MAKES SENSE NOW")
    if kind is PickupKind.SERVO_KEBAB:
        effects.digestion_ms = max(effects.digestion_ms, 5000)
        return PickupResult(health_delta=45, message="GARLIC SAUCE RESTORED YOUR SOUL")
    if kind is PickupKind.PIDGE_CHIPS:
        return PickupResult(chips_delta=1, message="PIDGE ACCEPTS YOUR TRIBUTE")
    if kind is PickupKind.MYSTERY_WRISTBAND:
        return PickupResult(vibe_delta=5, message="WRISTBAND STATUS: PROBABLY VIP")
    raise ValueError(f"unsupported pickup: {kind}")


@dataclass(slots=True)
class PidgeState:
    chips: int = 0
    scout: int = 0
    thief: int = 0
    menace: int = 0
    oracle: int = 0
    retrieve_cooldown_ms: int = 0
    interrupt_cooldown_ms: int = 0

    def update(self, dt_ms: int) -> None:
        self.retrieve_cooldown_ms = max(0, self.retrieve_cooldown_ms - dt_ms)
        self.interrupt_cooldown_ms = max(0, self.interrupt_cooldown_ms - dt_ms)

    def level(self, branch: PidgeBranch) -> int:
        return int(getattr(self, branch.value))

    def upgrade_cost(self, branch: PidgeBranch) -> int:
        return 2 + self.level(branch) * 2

    def upgrade(self, branch: PidgeBranch) -> bool:
        cost = self.upgrade_cost(branch)
        if self.chips < cost or self.level(branch) >= 3:
            return False
        self.chips -= cost
        setattr(self, branch.value, self.level(branch) + 1)
        return True

    def can_retrieve(self) -> bool:
        return self.retrieve_cooldown_ms <= 0

    def retrieve_missed_pickup(self) -> bool:
        if not self.can_retrieve():
            return False
        self.retrieve_cooldown_ms = max(9000, 18000 - self.scout * 2500)
        return True

    def can_interrupt(self) -> bool:
        return self.menace > 0 and self.interrupt_cooldown_ms <= 0

    def interrupt_enemy(self) -> bool:
        if not self.can_interrupt():
            return False
        self.interrupt_cooldown_ms = max(7000, 15000 - self.menace * 2000)
        return True

    def hidden_route_radius(self) -> int:
        return 48 + self.scout * 28

    def fake_hazard_accuracy(self) -> float:
        return min(1.0, 0.35 + self.oracle * 0.2)

    def boss_steal_power(self) -> int:
        return self.thief * 10
