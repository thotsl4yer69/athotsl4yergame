from __future__ import annotations

import copy

import pytest

from packet_loss.stage import CampaignDataError, StageRuntime, campaign_from_dict, load_campaign
from packet_loss.systems import EffectState, PickupKind, PidgeBranch, PidgeState, apply_pickup


def test_bundled_campaign_has_unique_ordered_events() -> None:
    campaign = load_campaign()
    assert campaign.campaign_id == "packet_loss_campaign"
    assert campaign.stage("d1_queue").esp32_enabled is True
    assert campaign.stage("d1_promoter").esp32_enabled is False
    all_ids = [event.event_id for stage in campaign.stages for event in stage.events]
    assert len(all_ids) == len(set(all_ids))


def test_runtime_emits_events_once_and_restores_checkpoint() -> None:
    stage = load_campaign().stage("d1_queue")
    runtime = StageRuntime(stage)
    first = runtime.advance(41000)
    assert first[-1].kind == "checkpoint"
    assert runtime.checkpoint_ms == 40000
    second = runtime.advance(10000)
    assert second
    emitted_ids = {event.event_id for event in first + second}
    assert len(emitted_ids) == len(first + second)

    runtime.restore_checkpoint()
    replay = runtime.advance(8000)
    assert all(event.at_ms > runtime.checkpoint_ms for event in replay)
    assert "queue_checkpoint_1" not in {event.event_id for event in replay}


def test_campaign_rejects_duplicate_event_ids() -> None:
    campaign = load_campaign()
    raw = {
        "campaign_id": campaign.campaign_id,
        "version": campaign.version,
        "stages": [
            {
                "id": stage.stage_id,
                "district_id": stage.district_id,
                "name": stage.name,
                "duration_ms": stage.duration_ms,
                "environment": stage.environment,
                "pi_enabled": stage.pi_enabled,
                "esp32_enabled": stage.esp32_enabled,
                "events": [
                    {
                        "at_ms": event.at_ms,
                        "kind": event.kind,
                        "id": event.event_id,
                        "payload": copy.deepcopy(event.payload),
                    }
                    for event in stage.events
                ],
            }
            for stage in campaign.stages
        ],
    }
    raw["stages"][1]["events"][0]["id"] = raw["stages"][0]["events"][0]["id"]
    with pytest.raises(CampaignDataError, match="duplicate event id"):
        campaign_from_dict(raw)


def test_pickup_effects_and_expiry() -> None:
    effects = EffectState()
    krn = apply_pickup(PickupKind.KRN_CAN, effects)
    assert krn.health_delta == 18
    assert effects.confidence_ms == 9000

    dust = apply_pickup(PickupKind.THINKING_DUST, effects, dust_uses=5)
    assert dust.vibe_delta == 12
    assert effects.score_multiplier == 2.0
    assert effects.paranoia == 2

    effects.update(7000)
    assert effects.thinking_ms == 0
    assert effects.score_multiplier == 1.0


def test_pidge_upgrade_and_cooldowns() -> None:
    pidge = PidgeState(chips=20)
    assert pidge.upgrade(PidgeBranch.SCOUT)
    assert pidge.scout == 1
    assert pidge.hidden_route_radius() == 76

    assert pidge.retrieve_missed_pickup()
    assert not pidge.retrieve_missed_pickup()
    pidge.update(pidge.retrieve_cooldown_ms)
    assert pidge.retrieve_missed_pickup()

    assert pidge.upgrade(PidgeBranch.MENACE)
    assert pidge.interrupt_enemy()
    assert not pidge.interrupt_enemy()
