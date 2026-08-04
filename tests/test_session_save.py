from pathlib import Path

from packet_loss.save import SaveData, load_save, write_save
from packet_loss.session import CampaignSession
from packet_loss.stage import load_campaign


def test_save_round_trip_and_corrupt_recovery(tmp_path: Path) -> None:
    path = tmp_path / "save.json"
    save = SaveData(high_score=42069, unlocked_stages=["d1_queue", "d1_coat_check"])
    write_save(save, path)
    loaded = load_save(path)
    assert loaded.high_score == 42069
    assert "d1_coat_check" in loaded.unlocked_stages

    path.write_text("{broken", encoding="utf-8")
    recovered = load_save(path)
    assert recovered.high_score == 0
    assert recovered.unlocked_stages == ["d1_queue"]


def test_stage_events_drive_session() -> None:
    campaign = load_campaign()
    save = SaveData()
    session = CampaignSession(campaign=campaign, save=save)

    for _ in range(110):
        session.update(100)
    assert session.message
    assert session.pickups
    assert session.pidge.retrieve_cooldown_ms >= 0

    for _ in range(50):
        session.update(100)
    assert session.model.enemies


def test_stage_completion_unlocks_next_stage() -> None:
    campaign = load_campaign()
    save = SaveData()
    session = CampaignSession(campaign=campaign, save=save)

    session.update(session.definition.duration_ms)
    assert session.runtime.complete
    assert session.next_stage == "d1_coat_check"
    assert "d1_coat_check" in save.unlocked_stages
    assert "d1_queue" in save.completed_stages


def test_headless_campaign_timeline_reaches_finish() -> None:
    campaign = load_campaign()
    save = SaveData()
    session = CampaignSession(campaign=campaign, save=save)
    for _ in range(1000):
        session.update(100)
        if session.runtime.complete:
            break
    assert session.runtime.complete
