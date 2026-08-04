from packet_loss.input import TouchSample, classify_touch
from packet_loss.model import Action


def test_left_tap_jumps() -> None:
    assert classify_touch(TouchSample(50, 200, 52, 201, 90)) is Action.JUMP


def test_right_tap_attacks() -> None:
    assert classify_touch(TouchSample(400, 200, 401, 201, 90)) is Action.ATTACK


def test_vertical_swipes() -> None:
    assert classify_touch(TouchSample(200, 220, 200, 120, 180)) is Action.SPECIAL
    assert classify_touch(TouchSample(200, 100, 200, 210, 180)) is Action.DODGE
