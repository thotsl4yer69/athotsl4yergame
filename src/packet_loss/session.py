"""High-level campaign session joining stage events to gameplay systems."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .model import GameModel
from .save import SaveData
from .stage import Campaign, StageEvent, StageRuntime
from .systems import EffectState, PidgeState, PickupKind, apply_pickup


@dataclass(slots=True)
class WorldPickup:
    kind: PickupKind
    x: float
    location: str
    event_id: str
    active: bool = True


@dataclass(slots=True)
class WorldHazard:
    kind: str
    x: float
    event_id: str
    damage: int = 10
    active: bool = True


@dataclass(slots=True)
class CampaignSession:
    campaign: Campaign
    save: SaveData
    stage_id: str = "d1_queue"
    model: GameModel = field(default_factory=lambda: GameModel(auto_spawn=False))
    effects: EffectState = field(default_factory=EffectState)
    pidge: PidgeState = field(default_factory=PidgeState)
    runtime: StageRuntime = field(init=False)
    pickups: list[WorldPickup] = field(default_factory=list)
    hazards: list[WorldHazard] = field(default_factory=list)
    message: str = ""
    message_ms: int = 0
    background_scene: str = ""
    boss_phase: str = ""
    dust_uses: int = 0
    next_stage: str | None = None

    def __post_init__(self) -> None:
        self.pidge.chips = self.save.pidge_chips
        self.pidge.scout = self.save.pidge_scout
        self.pidge.thief = self.save.pidge_thief
        self.pidge.menace = self.save.pidge_menace
        self.pidge.oracle = self.save.pidge_oracle
        self.start_stage(self.stage_id)

    @property
    def definition(self):  # type annotation omitted to avoid a runtime import cycle in old Python tools
        return self.runtime.definition

    def start_stage(self, stage_id: str) -> None:
        if stage_id not in self.save.unlocked_stages:
            raise ValueError(f"stage is locked: {stage_id}")
        self.stage_id = stage_id
        self.runtime = StageRuntime(self.campaign.stage(stage_id))
        self.model = GameModel(seed=69, auto_spawn=False)
        self.effects = EffectState()
        self.pickups.clear()
        self.hazards.clear()
        self.message = self.definition.name.upper()
        self.message_ms = 1800
        self.background_scene = self.definition.environment
        self.boss_phase = ""
        self.dust_uses = 0
        self.next_stage = None

    def update(self, dt_ms: int) -> None:
        self.message_ms = max(0, self.message_ms - dt_ms)
        self.effects.update(dt_ms)
        self.pidge.update(dt_ms)
        for event in self.runtime.advance(dt_ms):
            self._dispatch(event)
        speed = self.model.speed * (0.65 if self.effects.thinking_ms > 0 else 1.0)
        world_distance = speed * (dt_ms / 1000.0)
        for pickup in self.pickups:
            if pickup.active:
                pickup.x -= world_distance
        for hazard in self.hazards:
            if hazard.active:
                hazard.x -= world_distance
        self._resolve_world_objects()
        original_speed = self.model.speed
        self.model.speed = speed
        self.model.update(dt_ms)
        self.model.speed = original_speed

    def _dispatch(self, event: StageEvent) -> None:
        payload = event.payload
        if event.kind == "enemy":
            enemy = str(payload.get("enemy", "neon_siren"))
            health = 3 if enemy in {"the_promoter", "bottle_service_empress"} else 1
            self.model.spawn_enemy(enemy, health=health)
        elif event.kind == "pickup":
            self.pickups.append(
                WorldPickup(
                    kind=PickupKind(str(payload["pickup"])),
                    x=500.0,
                    location=str(payload.get("location", "floor")),
                    event_id=event.event_id,
                )
            )
        elif event.kind == "hazard":
            self.hazards.append(
                WorldHazard(
                    kind=str(payload.get("hazard", "club_debris")),
                    x=500.0,
                    event_id=event.event_id,
                    damage=int(payload.get("damage", 10)),
                )
            )
        elif event.kind == "bark":
            self._say(str(payload.get("text", "")), 2600)
        elif event.kind == "background":
            self.background_scene = str(payload.get("scene", self.definition.environment))
        elif event.kind == "pigeon":
            self._pidge_action(str(payload.get("action", "tutorial")), payload)
        elif event.kind == "boss_phase":
            self.boss_phase = str(payload.get("phase", "unknown"))
            self._say(f"BOSS PHASE: {self.boss_phase.replace('_', ' ').upper()}", 2200)
        elif event.kind == "finish":
            next_value = payload.get("next")
            self.next_stage = str(next_value) if next_value else None
            self.save.complete(self.stage_id, next_stage=self.next_stage, score=self.model.player.score)
            self._sync_pidge_save()
            self._say("STAGE CLEARED", 5000)

    def _resolve_world_objects(self) -> None:
        for pickup in self.pickups:
            if not pickup.active:
                continue
            if pickup.x < 50:
                pickup.active = False
                if self.pidge.retrieve_missed_pickup():
                    self._collect_pickup(pickup)
            elif 70 <= pickup.x <= 125:
                pickup.active = False
                self._collect_pickup(pickup)
        for hazard in self.hazards:
            if not hazard.active:
                continue
            if hazard.x < 50:
                hazard.active = False
            elif 70 <= hazard.x <= 125:
                hazard.active = False
                self.model.damage_player(hazard.damage)
                self._say(f"HIT BY {hazard.kind.replace('_', ' ').upper()}", 1200)
        self.pickups = [pickup for pickup in self.pickups if pickup.active]
        self.hazards = [hazard for hazard in self.hazards if hazard.active]

    def _collect_pickup(self, pickup: WorldPickup) -> None:
        if pickup.kind is PickupKind.THINKING_DUST:
            self.dust_uses += 1
        result = apply_pickup(pickup.kind, self.effects, dust_uses=self.dust_uses)
        player = self.model.player
        player.health = max(0, min(100, player.health + result.health_delta))
        player.vibe = max(0, min(100, player.vibe + result.vibe_delta))
        self.pidge.chips += result.chips_delta
        player.score += int(250 * self.effects.score_multiplier)
        self._say(result.message, 1900)

    def _pidge_action(self, action: str, payload: dict[str, Any]) -> None:
        if action == "tutorial":
            self._say(str(payload.get("text", "PIDGE IS JUDGING YOU.")), 3000)
        elif action == "retrieve_missed_pickup":
            if self.pickups and self.pidge.retrieve_missed_pickup():
                pickup = next((item for item in self.pickups if item.active), None)
                if pickup is not None:
                    pickup.active = False
                    self._collect_pickup(pickup)
        elif action == "interrupt_enemy":
            enemy = next((item for item in self.model.enemies if item.active), None)
            if enemy is not None and (self.pidge.interrupt_enemy() or self.pidge.menace == 0):
                enemy.telegraph_ms += 1200
                self._say("PIDGE HAS CHOSEN VIOLENCE", 1600)
        elif action == "reveal_hidden_route":
            self._say("PIDGE FOUND SOMETHING SHINY", 1800)
            self.model.player.score += 300
        elif action == "warn_fake_hazard":
            self._say("PIDGE: THAT WARNING IS FAKE", 1800)
        elif action == "steal_guest_list_tablet":
            self.model.player.special_charge = min(
                100, self.model.player.special_charge + 35 + self.pidge.boss_steal_power()
            )
            self._say("PIDGE STOLE THE GUEST LIST", 2200)
        else:
            self._say("PIDGE REFUSES TO EXPLAIN ITSELF", 1500)

    def _say(self, text: str, duration_ms: int) -> None:
        self.message = text
        self.message_ms = duration_ms

    def _sync_pidge_save(self) -> None:
        self.save.pidge_chips = self.pidge.chips
        self.save.pidge_scout = self.pidge.scout
        self.save.pidge_thief = self.pidge.thief
        self.save.pidge_menace = self.pidge.menace
        self.save.pidge_oracle = self.pidge.oracle
