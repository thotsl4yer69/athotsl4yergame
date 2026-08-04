"""Runnable 480x320 vertical-slice prototype."""

from __future__ import annotations

import argparse
import os
import time

import pygame

from .input import TouchSample, classify_touch
from .model import Action, GameModel

WIDTH, HEIGHT = 480, 320
GROUND_Y = 260


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fullscreen", action="store_true")
    parser.add_argument("--windowed", action="store_true")
    parser.add_argument("--touch-debug", action="store_true")
    parser.add_argument("--headless-smoke-test", action="store_true")
    return parser.parse_args()


def draw(screen: pygame.Surface, model: GameModel, debug: str = "") -> None:
    screen.fill((9, 6, 20))
    pygame.draw.rect(screen, (28, 14, 49), (0, 190, WIDTH, 130))
    for x in range(0, WIDTH, 48):
        pygame.draw.line(screen, (70, 25, 90), (x, 190), (x - 55, HEIGHT), 1)
    pygame.draw.line(screen, (220, 40, 185), (0, GROUND_Y), (WIDTH, GROUND_Y), 3)

    p = model.player
    y = GROUND_Y - 58 - (35 if p.airborne_ms > 0 else 0)
    body = pygame.Rect(78, y, 34, 58)
    pygame.draw.ellipse(screen, (245, 182, 140), (83, y - 19, 24, 24))
    pygame.draw.rect(screen, (38, 210, 210), body, border_radius=10)
    if p.attack_ms > 0:
        pygame.draw.arc(screen, (255, 215, 65), (100, y - 5, 55, 55), 4.4, 6.0, 5)
    if p.dodge_ms > 0:
        pygame.draw.ellipse(screen, (200, 70, 255), body.inflate(18, 5), 3)

    enemy_colours = {
        "neon_siren": (255, 65, 170),
        "clout_leech": (115, 235, 210),
        "bottle_knight": (255, 190, 55),
    }
    for enemy in model.enemies:
        ex = int(enemy.x)
        pygame.draw.ellipse(screen, (230, 165, 135), (ex + 8, 184, 23, 23))
        pygame.draw.rect(screen, enemy_colours[enemy.kind], (ex, 205, 40, 55), border_radius=12)
        if enemy.telegraph_ms > 0:
            pygame.draw.circle(screen, (255, 255, 255), (ex + 20, 194), 28, 2)

    font = pygame.font.Font(None, 22)
    title_font = pygame.font.Font(None, 28)
    screen.blit(title_font.render("TH0TSL4YER69 // PACKET LOSS", True, (255, 65, 190)), (10, 8))
    hud = f"HP {p.health:03d}   VIBE {p.vibe:03d}   SCORE {p.score:06d}   x{p.combo}"
    screen.blit(font.render(hud, True, (235, 235, 245)), (10, 36))
    pygame.draw.rect(screen, (50, 45, 65), (10, 58, 130, 8))
    pygame.draw.rect(screen, (255, 70, 110), (10, 58, int(1.3 * p.health), 8))
    pygame.draw.rect(screen, (50, 45, 65), (150, 58, 130, 8))
    pygame.draw.rect(screen, (110, 240, 220), (150, 58, int(1.3 * p.vibe), 8))
    if debug:
        screen.blit(font.render(debug, True, (255, 255, 100)), (10, 290))


def run(args: argparse.Namespace) -> int:
    if args.headless_smoke_test:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    flags = pygame.FULLSCREEN if args.fullscreen and not args.windowed else 0
    screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
    pygame.display.set_caption("TH0TSL4YER69: Packet Loss")
    clock = pygame.time.Clock()
    model = GameModel()
    press: tuple[int, int, float] | None = None
    debug = ""
    frames = 0
    running = True
    while running:
        dt = clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    model.apply(Action.JUMP)
                elif event.key == pygame.K_x:
                    model.apply(Action.ATTACK)
                elif event.key == pygame.K_DOWN:
                    model.apply(Action.DODGE)
                elif event.key == pygame.K_UP:
                    model.apply(Action.SPECIAL)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                press = (event.pos[0], event.pos[1], time.monotonic())
            elif event.type == pygame.MOUSEBUTTONUP and press:
                sx, sy, started = press
                sample = TouchSample(sx, sy, event.pos[0], event.pos[1], int((time.monotonic() - started) * 1000))
                action = classify_touch(sample)
                model.apply(action)
                debug = f"touch=({sx},{sy})->{event.pos} {sample.duration_ms}ms action={action.name}"
                press = None

        model.update(dt)
        draw(screen, model, debug if args.touch_debug else "")
        pygame.display.flip()
        frames += 1
        if args.headless_smoke_test and frames >= 3:
            running = False
        if model.player.health <= 0:
            model = GameModel(seed=model.seed)
    pygame.quit()
    return 0


def main() -> int:
    return run(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
