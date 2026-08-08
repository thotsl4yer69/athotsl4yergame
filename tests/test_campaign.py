from __future__ import annotations

from packet_loss.campaign import Campaign
from packet_loss.entities import BossController, BossPhase, StageRun
from packet_loss.input import Gesture, GestureInput, GestureKind
from packet_loss.persistence import Progress, load_progress, save_progress
from packet_loss.stages import DISTRICT_1_STAGES, PickupKind


def action(kind: GestureKind) -> Gesture:
    return Gesture(kind, 300, 160, 4)


def test_mouse_and_touch_samples_share_gesture_classifier() -> None:
    gestures = GestureInput(480)
    gestures.begin(10, 100, 0)
    assert gestures.end(10, 100, 8) == Gesture(GestureKind.JUMP, 10, 100, 8)
    gestures.begin(400, 200, 10)
    assert gestures.end(400, 150, 20) == Gesture(GestureKind.SPECIAL, 400, 150, 10)


def test_every_stage_has_stable_id_pigeon_and_hidden_pickup_route() -> None:
    assert len(DISTRICT_1_STAGES) == 5
    assert len({stage.id for stage in DISTRICT_1_STAGES}) == 5
    for stage in DISTRICT_1_STAGES:
        run = StageRun(stage)
        run.advance(4)
        run.meet_pigeon()
        assert run.retrieve_hidden_pickup()
        assert run.inventory == [stage.pickup]
        assert {"id", "balance_name", "pickup"} <= stage.esp32_data().keys()


def test_stage_transition_unlocks_only_next_stage() -> None:
    campaign = Campaign()
    assert campaign.select_stage(0)
    assert not campaign.select_stage(1)
    assert campaign.run is not None
    campaign.run.distance = 2400
    assert campaign.finish_current_stage()
    assert campaign.progress == Progress(1, ("d1_queue",))
    assert campaign.select_stage(1)


def test_checkpoint_restore_recovers_safe_stage_state() -> None:
    run = StageRun(DISTRICT_1_STAGES[0], health=5)
    run.advance(12)
    assert run.checkpoint_distance == 600
    run.distance = 1234
    run.restore_checkpoint()
    assert (run.distance, run.health) == (600, 100)


def test_pickups_apply_context_sensitive_effects() -> None:
    can_run = StageRun(DISTRICT_1_STAGES[0], health=70)
    can_run.meet_pigeon()
    assert can_run.retrieve_hidden_pickup()
    assert can_run.use_pickup() is PickupKind.KRN_CAN
    assert can_run.health == 95
    dust_run = StageRun(DISTRICT_1_STAGES[1])
    dust_run.meet_pigeon()
    assert dust_run.retrieve_hidden_pickup()
    assert dust_run.use_pickup() is PickupKind.THINKING_DUST
    assert dust_run.score == 500


def test_promoter_has_four_combat_phases_before_defeat() -> None:
    boss = BossController()
    assert boss.phase is BossPhase.GUEST_LIST
    assert [boss.disrupt(25) for _ in range(4)] == [
        BossPhase.FOLLOWER_FLOOD,
        BossPhase.SPARKLER_PITCH,
        BossPhase.FINAL_RECEIPT,
        BossPhase.DEFEATED,
    ]


def test_corrupted_save_returns_default_and_atomic_save_round_trips(tmp_path) -> None:
    save_path = tmp_path / "progress.json"
    save_path.write_text("{nope", encoding="utf-8")
    assert load_progress(save_path) == Progress()
    progress = Progress(2, ("d1_queue", "d1_coat_check"))
    save_progress(save_path, progress)
    assert load_progress(save_path) == progress
