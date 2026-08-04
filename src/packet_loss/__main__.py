"""Runnable 480x320 campaign prototype."""

from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

import pygame

from .characters import load_neon_siren_frames
from .input import TouchSample, classify_touch
from .model import Action
from .save import load_save, write_save
from .session import CampaignSession
from .stage import enabled_stages, load_campaign

WIDTH, HEIGHT = 480, 320
GROUND_Y = 260


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fullscreen", action="store_true")
    parser.add_argument("--windowed", action="store_true")
    parser.add_argument("--touch-debug", action="store_true")
    parser.add_argument("--headless-smoke-test", action="store_true")
    parser.add_argument("--stage", default="d1_queue")
    parser.add_argument("--save-path", type=Path)
    return parser.parse_args()


def _environment_palette(environment: str) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    palettes = {
        "outdoor_queue_rain": ((7, 10, 28), (30, 24, 60)),
        "coat_check_corridor": ((24, 8, 26), (58, 24, 48)),
        "neon_main_floor": ((10, 4, 24), (52, 12, 66)),
        "nightclub_bathroom": ((14, 20, 24), (40, 50, 58)),
        "promoter_boss_room": ((28, 4, 10), (72, 16, 28)),
    }
    return palettes.get(environment, ((9, 6, 20), (28, 14, 49)))


def _draw_background(screen: pygame.Surface, session: CampaignSession) -> None:
    sky, floor = _environment_palette(session.definition.environment)
    screen.fill(sky)
    pygame.draw.rect(screen, floor, (0, 170, WIDTH, 150))
    offset = (session.runtime.elapsed_ms // 20) % 48
    for x in range(-48, WIDTH + 48, 48):
        pygame.draw.line(screen, (70, 25, 90), (x - offset, 190), (x - 55 - offset, HEIGHT), 1)
    if session.definition.environment == "outdoor_queue_rain":
        rain_offset = (session.runtime.elapsed_ms // 12) % 20
        for x in range(0, WIDTH, 24):
            pygame.draw.line(screen, (90, 130, 190), (x, rain_offset), (x - 7, rain_offset + 16), 1)
    elif session.definition.environment == "neon_main_floor":
        pulse = 8 + (session.runtime.elapsed_ms // 80) % 28
        pygame.draw.circle(screen, (190, 40, 190), (350, 100), pulse, 2)
        pygame.draw.line(screen, (50, 220, 230), (330, 50), (300, 190), 2)
    elif session.definition.environment == "nightclub_bathroom":
        for x in (45, 155, 265, 375):
            pygame.draw.rect(screen, (100, 120, 130), (x, 88, 68, 95), 2)
    pygame.draw.line(screen, (220, 40, 185), (0, GROUND_Y), (WIDTH, GROUND_Y), 3)


def _draw_player(screen: pygame.Surface, session: CampaignSession) -> None:
    player = session.model.player
    y = GROUND_Y - 58 - (35 if player.airborne_ms > 0 else 0)
    body = pygame.Rect(78, y, 34, 58)
    pygame.draw.ellipse(screen, (245, 182, 140), (83, y - 19, 24, 24))
    pygame.draw.rect(screen, (38, 210, 210), body, border_radius=10)
    if player.attack_ms > 0:
        pygame.draw.arc(screen, (255, 215, 65), (100, y - 5, 55, 55), 4.4, 6.0, 5)
    if player.dodge_ms > 0:
        pygame.draw.ellipse(screen, (200, 70, 255), body.inflate(18, 5), 3)


def _neon_siren_frame(
    session: CampaignSession,
    telegraph_ms: int,
    frames_by_animation: dict[str, tuple[pygame.Surface, ...]],
) -> pygame.Surface | None:
    if not frames_by_animation:
        return None
    animation = "telegraph" if telegraph_ms > 0 else (
        "walk" if (session.runtime.elapsed_ms // 900) % 2 else "idle"
    )
    frames = frames_by_animation.get(animation)
    if not frames:
        return None
    return frames[(session.runtime.elapsed_ms // 120) % len(frames)]


def _draw_enemies(
    screen: pygame.Surface,
    session: CampaignSession,
    neon_siren_frames: dict[str, tuple[pygame.Surface, ...]],
) -> None:
    colours = {
        "neon_siren": (255, 65, 170),
        "clout_leech": (115, 235, 210),
        "bottle_knight": (255, 190, 55),
        "velvet_vandal": (185, 35, 95),
        "bottle_service_valkyrie": (255, 180, 45),
        "afterparty_oracle": (125, 70, 220),
        "the_promoter": (230, 55, 55),
    }
    for enemy in session.model.enemies:
        ex = int(enemy.x)
        colour = colours.get(enemy.kind, (225, 80, 170))
        sprite = (
            _neon_siren_frame(session, enemy.telegraph_ms, neon_siren_frames)
            if enemy.kind == "neon_siren"
            else None
        )
        if sprite is None:
            pygame.draw.ellipse(screen, (230, 165, 135), (ex + 8, 184, 23, 23))
            pygame.draw.rect(screen, colour, (ex, 205, 40, 55), border_radius=12)
        else:
            screen.blit(sprite, (ex - 12, GROUND_Y - 58))
        if enemy.telegraph_ms > 0:
            pygame.draw.circle(screen, (255, 255, 255), (ex + 20, 194), 28, 2)
        if enemy.health > 1:
            pygame.draw.rect(screen, (30, 20, 35), (ex, 178, 42, 4))
            pygame.draw.rect(screen, (255, 65, 100), (ex, 178, 14 * enemy.health, 4))


def _draw_world_objects(screen: pygame.Surface, session: CampaignSession) -> None:
    pickup_colours = {
        "krn_can": (245, 205, 45),
        "thinking_dust": (240, 245, 255),
        "servo_kebab": (205, 125, 65),
        "pidge_chips": (255, 220, 90),
        "mystery_wristband": (60, 240, 210),
    }
    for pickup in session.pickups:
        pygame.draw.rect(
            screen,
            pickup_colours[pickup.kind.value],
            (int(pickup.x), GROUND_Y - 22, 16, 16),
            border_radius=4,
        )
    for hazard in session.hazards:
        hx = int(hazard.x)
        pygame.draw.polygon(
            screen,
            (255, 90, 100),
            ((hx, GROUND_Y), (hx + 12, GROUND_Y - 20), (hx + 24, GROUND_Y)),
        )
    px = 38 + int(5 * ((session.runtime.elapsed_ms // 180) % 2))
    pygame.draw.ellipse(screen, (120, 125, 135), (px, 105, 22, 14))
    pygame.draw.circle(screen, (150, 155, 160), (px + 18, 108), 7)
    pygame.draw.circle(screen, (255, 45, 45), (px + 20, 106), 2)
    pygame.draw.polygon(screen, (230, 180, 40), ((px + 25, 108), (px + 32, 111), (px + 25, 113)))


def draw(
    screen: pygame.Surface,
    session: CampaignSession,
    debug: str = "",
    neon_siren_frames: dict[str, tuple[pygame.Surface, ...]] | None = None,
) -> None:
    _draw_background(screen, session)
    _draw_world_objects(screen, session)
    _draw_player(screen, session)
    _draw_enemies(screen, session, neon_siren_frames or {})

    font = pygame.font.Font(None, 22)
    small = pygame.font.Font(None, 18)
    title_font = pygame.font.Font(None, 27)
    player = session.model.player
    screen.blit(title_font.render("TH0TSL4YER69 // PACKET LOSS", True, (255, 65, 190)), (10, 8))
    hud = (
        f"HP {player.health:03d} VIBE {player.vibe:03d} "
        f"SCORE {player.score:06d} x{player.combo} CHIPS {session.pidge.chips}"
    )
    screen.blit(font.render(hud, True, (235, 235, 245)), (10, 34))
    progress = min(1.0, session.runtime.elapsed_ms / session.definition.duration_ms)
    pygame.draw.rect(screen, (48, 42, 60), (10, 57, 460, 7))
    pygame.draw.rect(screen, (240, 50, 180), (10, 57, int(460 * progress), 7))
    stage_text = f"{session.definition.name} // {session.background_scene.replace('_', ' ').upper()}"
    screen.blit(small.render(stage_text, True, (150, 230, 230)), (10, 70))
    if session.boss_phase:
        screen.blit(
            small.render(session.boss_phase.replace("_", " ").upper(), True, (255, 200, 70)),
            (340, 70),
        )
    if session.message_ms > 0 and session.message:
        panel = pygame.Rect(34, 274, 412, 34)
        pygame.draw.rect(screen, (10, 8, 20), panel, border_radius=5)
        pygame.draw.rect(screen, (255, 65, 190), panel, 2, border_radius=5)
        text = small.render(session.message[:54], True, (255, 245, 250))
        screen.blit(text, text.get_rect(center=panel.center))
    if session.effects.paranoia > 0 and session.effects.thinking_ms > 0:
        for index in range(session.effects.paranoia):
            screen.blit(small.render("FAKE WARNING", True, (255, 255, 80)), (300, 96 + index * 18))
    if debug:
        screen.blit(small.render(debug[:70], True, (255, 255, 100)), (10, 300))


def _headless_campaign_smoke(session: CampaignSession) -> int:
    for _ in range(4000):
        session.update(100)
        if session.runtime.complete:
            return 0
    return 2


def run(args: argparse.Namespace) -> int:
    if args.headless_smoke_test:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    campaign = load_campaign()
    save = load_save(args.save_path)
    pi_stage_ids = {stage.stage_id for stage in enabled_stages(campaign, "pi")}
    stage_id = args.stage if args.stage in pi_stage_ids else "d1_queue"
    save.unlock(stage_id)
    session = CampaignSession(campaign=campaign, save=save, stage_id=stage_id)
    if args.headless_smoke_test:
        result = _headless_campaign_smoke(session)
        write_save(save, args.save_path)
        return result

    pygame.init()
    flags = pygame.FULLSCREEN if args.fullscreen and not args.windowed else 0
    screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
    pygame.display.set_caption("TH0TSL4YER69: Packet Loss")
    clock = pygame.time.Clock()
    neon_siren_frames = load_neon_siren_frames()
    press: tuple[int, int, float] | None = None
    debug = ""
    running = True
    while running:
        dt = min(100, clock.tick(30))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                key_actions = {
                    pygame.K_SPACE: Action.JUMP,
                    pygame.K_x: Action.ATTACK,
                    pygame.K_DOWN: Action.DODGE,
                    pygame.K_UP: Action.SPECIAL,
                }
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RETURN and session.runtime.complete and session.next_stage:
                    if session.next_stage in pi_stage_ids:
                        session.start_stage(session.next_stage)
                elif event.key in key_actions:
                    session.model.apply(key_actions[event.key])
            elif event.type == pygame.MOUSEBUTTONDOWN:
                press = (event.pos[0], event.pos[1], time.monotonic())
            elif event.type == pygame.MOUSEBUTTONUP and press:
                sx, sy, started = press
                sample = TouchSample(
                    sx,
                    sy,
                    event.pos[0],
                    event.pos[1],
                    int((time.monotonic() - started) * 1000),
                )
                action = classify_touch(sample)
                session.model.apply(action)
                debug = (
                    f"touch=({sx},{sy})->{event.pos} "
                    f"{sample.duration_ms}ms action={action.name}"
                )
                press = None

        session.update(dt)
        draw(screen, session, debug if args.touch_debug else "", neon_siren_frames)
        pygame.display.flip()
        if session.model.player.health <= 0:
            session.runtime.restore_checkpoint()
            session.model = session.model.__class__(seed=69, auto_spawn=False)
            session.message = "PIDGE DRAGGED YOU BACK TO THE CHECKPOINT"
            session.message_ms = 2400
    write_save(save, args.save_path)
    pygame.quit()
    return 0


def main() -> int:
    return run(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
