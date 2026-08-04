"""Platform-neutral gameplay state used by renderers and tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
import random


class Action(Enum):
    NONE = auto()
    JUMP = auto()
    ATTACK = auto()
    DODGE = auto()
    SPECIAL = auto()


@dataclass(slots=True)
class PlayerState:
    health: int = 100
    vibe: int = 0
    score: int = 0
    combo: int = 0
    airborne_ms: int = 0
    dodge_ms: int = 0
    attack_ms: int = 0
    special_charge: int = 0


@dataclass(slots=True)
class EnemyState:
    kind: str
    x: float
    lane: int = 0
    health: int = 1
    telegraph_ms: int = 600
    active: bool = True


@dataclass(slots=True)
class GameModel:
    seed: int = 69
    speed: float = 75.0
    elapsed_ms: int = 0
    spawn_cooldown_ms: int = 900
    auto_spawn: bool = True
    player: PlayerState = field(default_factory=PlayerState)
    enemies: list[EnemyState] = field(default_factory=list)
    _rng: random.Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)

    def apply(self, action: Action) -> None:
        p = self.player
        if action is Action.JUMP and p.airborne_ms <= 0:
            p.airborne_ms = 520
        elif action is Action.ATTACK:
            p.attack_ms = 180
        elif action is Action.DODGE:
            p.dodge_ms = 360
        elif action is Action.SPECIAL and p.special_charge >= 100:
            p.special_charge = 0
            for enemy in self.enemies:
                if enemy.active:
                    enemy.active = False
                    p.score += 150

    def spawn_enemy(
        self,
        kind: str,
        *,
        x: float = 520.0,
        lane: int = 0,
        health: int = 1,
        telegraph_ms: int = 600,
    ) -> EnemyState:
        """Spawn a named enemy for a stage event and return it."""

        enemy = EnemyState(
            kind=kind,
            x=x,
            lane=lane,
            health=max(1, health),
            telegraph_ms=max(0, telegraph_ms),
        )
        self.enemies.append(enemy)
        return enemy

    def damage_player(self, amount: int) -> None:
        """Apply environmental damage while preserving normal combo penalties."""

        if amount <= 0:
            return
        p = self.player
        if p.airborne_ms > 0 or p.dodge_ms > 0:
            return
        p.health = max(0, p.health - amount)
        p.combo = 0
        p.vibe = max(0, p.vibe - 20)

    def update(self, dt_ms: int) -> None:
        if dt_ms < 0:
            raise ValueError("dt_ms cannot be negative")
        self.elapsed_ms += dt_ms
        p = self.player
        p.airborne_ms = max(0, p.airborne_ms - dt_ms)
        p.dodge_ms = max(0, p.dodge_ms - dt_ms)
        p.attack_ms = max(0, p.attack_ms - dt_ms)
        p.score += max(0, dt_ms // 50)

        distance = self.speed * (dt_ms / 1000.0)
        for enemy in self.enemies:
            if not enemy.active:
                continue
            enemy.x -= distance
            enemy.telegraph_ms = max(0, enemy.telegraph_ms - dt_ms)
            self._resolve_enemy(enemy)

        self.enemies = [enemy for enemy in self.enemies if enemy.active and enemy.x > -48]
        if not self.auto_spawn:
            return
        self.spawn_cooldown_ms -= dt_ms
        if self.spawn_cooldown_ms <= 0:
            self._spawn_random_enemy()
            self.spawn_cooldown_ms = self._rng.randint(700, 1300)

    def _spawn_random_enemy(self) -> None:
        kind = self._rng.choice(("neon_siren", "clout_leech", "bottle_knight"))
        self.spawn_enemy(kind)

    def _resolve_enemy(self, enemy: EnemyState) -> None:
        if not 65 <= enemy.x <= 125:
            return
        p = self.player
        if p.attack_ms > 0:
            enemy.health -= 1
            p.combo += 1
            p.vibe = min(100, p.vibe + 12)
            p.special_charge = min(100, p.special_charge + 18)
            p.score += 100 * max(1, p.combo)
            if enemy.health <= 0:
                enemy.active = False
            else:
                enemy.x = 145
                enemy.telegraph_ms = 300
            return
        if p.airborne_ms > 0 or p.dodge_ms > 0 or enemy.telegraph_ms > 0:
            return
        enemy.active = False
        p.health = max(0, p.health - 15)
        p.combo = 0
        p.vibe = max(0, p.vibe - 25)
