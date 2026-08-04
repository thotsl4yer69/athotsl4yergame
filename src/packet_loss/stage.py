"""Validated, deterministic campaign and stage runtime.

The data model deliberately stays renderer-neutral so Raspberry Pi and ESP32-S3
builds can consume the same stage IDs, event timing, and balance names.
"""

from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass, field
from importlib import resources
import json
from pathlib import Path
from typing import Any, Iterable


ALLOWED_EVENT_KINDS = frozenset(
    {
        "enemy",
        "pickup",
        "hazard",
        "pigeon",
        "checkpoint",
        "bark",
        "background",
        "boss_phase",
        "finish",
    }
)


class CampaignDataError(ValueError):
    """Raised when campaign JSON is malformed or internally inconsistent."""


@dataclass(frozen=True, slots=True)
class StageEvent:
    at_ms: int
    kind: str
    event_id: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class StageDefinition:
    stage_id: str
    district_id: str
    name: str
    duration_ms: int
    environment: str
    pi_enabled: bool
    esp32_enabled: bool
    events: tuple[StageEvent, ...]


@dataclass(frozen=True, slots=True)
class Campaign:
    campaign_id: str
    version: int
    stages: tuple[StageDefinition, ...]

    def stage(self, stage_id: str) -> StageDefinition:
        for stage in self.stages:
            if stage.stage_id == stage_id:
                return stage
        raise KeyError(stage_id)


def _as_bool(value: Any, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise CampaignDataError(f"{field_name} must be a boolean")
    return value


def _parse_event(raw: Any, *, stage_id: str, index: int) -> StageEvent:
    if not isinstance(raw, dict):
        raise CampaignDataError(f"{stage_id}.events[{index}] must be an object")
    try:
        at_ms = int(raw["at_ms"])
        kind = str(raw["kind"])
        event_id = str(raw["id"])
    except (KeyError, TypeError, ValueError) as exc:
        raise CampaignDataError(f"invalid event at {stage_id}.events[{index}]") from exc
    if at_ms < 0:
        raise CampaignDataError(f"{event_id}: at_ms cannot be negative")
    if kind not in ALLOWED_EVENT_KINDS:
        raise CampaignDataError(f"{event_id}: unsupported kind {kind!r}")
    if not event_id:
        raise CampaignDataError(f"{stage_id}.events[{index}] has an empty id")
    payload = raw.get("payload", {})
    if not isinstance(payload, dict):
        raise CampaignDataError(f"{event_id}: payload must be an object")
    return StageEvent(at_ms=at_ms, kind=kind, event_id=event_id, payload=dict(payload))


def campaign_from_dict(raw: Any) -> Campaign:
    """Parse and validate a campaign dictionary."""

    if not isinstance(raw, dict):
        raise CampaignDataError("campaign root must be an object")
    try:
        campaign_id = str(raw["campaign_id"])
        version = int(raw["version"])
        raw_stages = raw["stages"]
    except (KeyError, TypeError, ValueError) as exc:
        raise CampaignDataError("campaign is missing required fields") from exc
    if not campaign_id or version < 1:
        raise CampaignDataError("campaign_id must be set and version must be >= 1")
    if not isinstance(raw_stages, list) or not raw_stages:
        raise CampaignDataError("stages must be a non-empty list")

    stage_ids: set[str] = set()
    event_ids: set[str] = set()
    stages: list[StageDefinition] = []
    for stage_index, stage_raw in enumerate(raw_stages):
        if not isinstance(stage_raw, dict):
            raise CampaignDataError(f"stages[{stage_index}] must be an object")
        try:
            stage_id = str(stage_raw["id"])
            district_id = str(stage_raw["district_id"])
            name = str(stage_raw["name"])
            duration_ms = int(stage_raw["duration_ms"])
            environment = str(stage_raw["environment"])
            raw_events = stage_raw["events"]
        except (KeyError, TypeError, ValueError) as exc:
            raise CampaignDataError(f"invalid stage at index {stage_index}") from exc
        if not stage_id or stage_id in stage_ids:
            raise CampaignDataError(f"duplicate or empty stage id: {stage_id!r}")
        if duration_ms <= 0:
            raise CampaignDataError(f"{stage_id}: duration_ms must be positive")
        if not isinstance(raw_events, list):
            raise CampaignDataError(f"{stage_id}.events must be a list")

        events = tuple(
            _parse_event(event_raw, stage_id=stage_id, index=event_index)
            for event_index, event_raw in enumerate(raw_events)
        )
        times = [event.at_ms for event in events]
        if times != sorted(times):
            raise CampaignDataError(f"{stage_id}: events must be ordered by at_ms")
        for event in events:
            if event.at_ms > duration_ms:
                raise CampaignDataError(f"{event.event_id}: occurs after stage duration")
            if event.event_id in event_ids:
                raise CampaignDataError(f"duplicate event id: {event.event_id}")
            event_ids.add(event.event_id)

        stage_ids.add(stage_id)
        stages.append(
            StageDefinition(
                stage_id=stage_id,
                district_id=district_id,
                name=name,
                duration_ms=duration_ms,
                environment=environment,
                pi_enabled=_as_bool(stage_raw.get("pi_enabled", True), f"{stage_id}.pi_enabled"),
                esp32_enabled=_as_bool(
                    stage_raw.get("esp32_enabled", False), f"{stage_id}.esp32_enabled"
                ),
                events=events,
            )
        )
    return Campaign(campaign_id=campaign_id, version=version, stages=tuple(stages))


def load_campaign(path: str | Path | None = None) -> Campaign:
    """Load campaign data from a path or the bundled District 1 manifest."""

    if path is None:
        text = (
            resources.files("packet_loss")
            .joinpath("data/district_1.json")
            .read_text(encoding="utf-8")
        )
    else:
        text = Path(path).read_text(encoding="utf-8")
    try:
        raw = json.loads(text)
    except json.JSONDecodeError as exc:
        raise CampaignDataError(f"invalid JSON: {exc}") from exc
    return campaign_from_dict(raw)


@dataclass(slots=True)
class StageRuntime:
    """Advance a stage clock and emit each scheduled event exactly once."""

    definition: StageDefinition
    elapsed_ms: int = 0
    checkpoint_ms: int = 0
    complete: bool = False
    _cursor: int = 0

    def advance(self, dt_ms: int) -> list[StageEvent]:
        if dt_ms < 0:
            raise ValueError("dt_ms cannot be negative")
        if self.complete:
            return []
        self.elapsed_ms = min(self.definition.duration_ms, self.elapsed_ms + dt_ms)
        emitted: list[StageEvent] = []
        events = self.definition.events
        while self._cursor < len(events) and events[self._cursor].at_ms <= self.elapsed_ms:
            event = events[self._cursor]
            emitted.append(event)
            self._cursor += 1
            if event.kind == "checkpoint":
                self.checkpoint_ms = event.at_ms
            elif event.kind == "finish":
                self.complete = True
        if self.elapsed_ms >= self.definition.duration_ms:
            self.complete = True
        return emitted

    def restore_checkpoint(self) -> None:
        """Restore time and event cursor without replaying pre-checkpoint events."""

        self.elapsed_ms = self.checkpoint_ms
        self.complete = False
        times = [event.at_ms for event in self.definition.events]
        self._cursor = bisect_right(times, self.checkpoint_ms)

    def reset(self) -> None:
        self.elapsed_ms = 0
        self.checkpoint_ms = 0
        self.complete = False
        self._cursor = 0


def enabled_stages(campaign: Campaign, platform: str) -> Iterable[StageDefinition]:
    """Yield stages enabled for ``pi`` or ``esp32`` in campaign order."""

    if platform not in {"pi", "esp32"}:
        raise ValueError("platform must be 'pi' or 'esp32'")
    for stage in campaign.stages:
        if (platform == "pi" and stage.pi_enabled) or (
            platform == "esp32" and stage.esp32_enabled
        ):
            yield stage
