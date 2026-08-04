from packet_loss.model import Action, EnemyState, GameModel


def test_spawning_is_deterministic() -> None:
    left = GameModel(seed=69)
    right = GameModel(seed=69)
    for _ in range(100):
        left.update(33)
        right.update(33)
    assert [(e.kind, round(e.x, 2)) for e in left.enemies] == [
        (e.kind, round(e.x, 2)) for e in right.enemies
    ]


def test_attack_disrupts_enemy() -> None:
    model = GameModel()
    model.enemies.append(EnemyState(kind="neon_siren", x=100, telegraph_ms=0))
    model.apply(Action.ATTACK)
    model.update(16)
    assert not model.enemies
    assert model.player.score >= 100
    assert model.player.combo == 1


def test_collision_costs_health() -> None:
    model = GameModel()
    model.enemies.append(EnemyState(kind="clout_leech", x=100, telegraph_ms=0))
    model.update(16)
    assert model.player.health == 85
