"""Small Pygame renderer for the complete District 1 vertical slice."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

import pygame

from .campaign import Campaign
from .config import FPS, HEIGHT, WIDTH
from .input import Gesture, GestureInput
from .persistence import load_progress, save_progress
from .stages import DISTRICT_1_STAGES


class Screen(StrEnum):
    TITLE = "title"
    SELECT = "select"
    PLAY = "play"
    RESULTS = "results"
    PAUSE = "pause"


class Game:
    """A deliberately small 30 FPS loop using only bundled Pygame primitives."""

    def __init__(self, windowed: bool = False, touch_debug: bool = False, save_path: Path | None = None) -> None:
        pygame.init()
        flags = 0 if windowed else pygame.FULLSCREEN
        self.surface = pygame.display.set_mode((WIDTH, HEIGHT), flags)
        pygame.display.set_caption("TH0TSL4YER69: Packet Loss")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 15)
        self.input = GestureInput(WIDTH)
        self.touch_debug = touch_debug
        self.save_path = save_path or Path.home() / ".local" / "share" / "packet-loss" / "progress.json"
        self.campaign = Campaign(load_progress(self.save_path))
        self.screen = Screen.TITLE
        self.running = True
        self.last_result = ""

    def run(self, frame_limit: int | None = None) -> None:
        """Run until quit; frame_limit makes the same loop usable in headless checks."""
        frames = 0
        while self.running and (frame_limit is None or frames < frame_limit):
            delta = self.clock.tick(FPS) / 1000.0
            self._events()
            self._update(delta)
            self._draw()
            pygame.display.flip()
            frames += 1
        pygame.quit()

    def _events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                x, y = self._event_position(event)
                self.input.begin(x, y, pygame.time.get_ticks())
            elif event.type in (pygame.MOUSEBUTTONUP, pygame.FINGERUP):
                x, y = self._event_position(event)
                gesture = self.input.end(x, y, pygame.time.get_ticks())
                if gesture is not None:
                    self._handle_gesture(gesture)

    @staticmethod
    def _event_position(event: pygame.event.Event) -> tuple[float, float]:
        if event.type in (pygame.FINGERDOWN, pygame.FINGERUP):
            return event.x * WIDTH, event.y * HEIGHT
        return float(event.pos[0]), float(event.pos[1])

    def _handle_gesture(self, gesture: Gesture) -> None:
        if self.screen is Screen.TITLE:
            self.screen = Screen.SELECT
        elif self.screen is Screen.SELECT:
            index = int((gesture.y - 68) // 42)
            if self.campaign.select_stage(index):
                self.screen = Screen.PLAY
        elif self.screen is Screen.PLAY:
            if gesture.x > WIDTH - 45 and gesture.y < 40:
                self.screen = Screen.PAUSE
            else:
                self.campaign.handle_gesture(gesture)
        elif self.screen is Screen.PAUSE:
            self.screen = Screen.PLAY
        elif self.screen is Screen.RESULTS:
            self.screen = Screen.SELECT

    def _update(self, delta: float) -> None:
        if self.screen is not Screen.PLAY or self.campaign.run is None:
            return
        run = self.campaign.run
        run.advance(delta)
        if run.complete() and self.campaign.finish_current_stage():
            save_progress(self.save_path, self.campaign.progress)
            self.last_result = f"{run.stage.title} cleared! Score {run.score}"
            self.screen = Screen.RESULTS

    def _label(self, text: str, x: float, y: float, color: tuple[int, int, int] = (240, 240, 255)) -> None:
        self.surface.blit(self.font.render(text, True, color), (x, y))

    def _draw(self) -> None:
        self.surface.fill((12, 7, 28))
        if self.screen is Screen.TITLE:
            self._draw_title()
        elif self.screen is Screen.SELECT:
            self._draw_select()
        elif self.screen is Screen.PLAY:
            self._draw_stage()
        elif self.screen is Screen.RESULTS:
            self._draw_results()
        else:
            self._draw_stage()
            pygame.draw.rect(self.surface, (18, 10, 36), (75, 105, 330, 100))
            self._label("PAUSED", 195, 130, (255, 215, 80))
            self._label("Tap to resume", 170, 155)
        if self.touch_debug and self.input.last_gesture is not None:
            gesture = self.input.last_gesture
            self._label(
                f"{gesture.kind} {gesture.x:.0f},{gesture.y:.0f} {gesture.latency_ms}ms",
                4,
                HEIGHT - 18,
                (80, 255, 210),
            )

    def _draw_title(self) -> None:
        self._label("TH0TSL4YER69", 116, 94, (255, 60, 181))
        self._label("PACKET LOSS", 153, 120, (65, 230, 255))
        self._label("District 1: Velvet Entry", 145, 165, (255, 215, 80))
        self._label("All performers are adults (21+). Tap to enter.", 74, 220)

    def _draw_select(self) -> None:
        self._label("DISTRICT 1 // SELECT STAGE", 108, 28, (65, 230, 255))
        for index, stage in enumerate(DISTRICT_1_STAGES):
            y = 68 + index * 42
            unlocked = index <= self.campaign.progress.unlocked_stage
            color = (255, 60, 181) if unlocked else (65, 55, 85)
            pygame.draw.rect(self.surface, color, (36, y, 408, 32), 2)
            self._label(stage.title if unlocked else "LOCKED", 50, y + 8, color)

    def _draw_stage(self) -> None:
        if self.campaign.run is None:
            return
        run = self.campaign.run
        stage = run.stage
        scroll = int(run.distance) % WIDTH
        # Background, midground, and foreground are visuals only; performers have no collision state.
        pygame.draw.rect(self.surface, (20, 13, 55), (0, 0, WIDTH, 150))
        for x in range(-scroll // 4, WIDTH + 48, 48):
            pygame.draw.rect(self.surface, (35, 25, 78), (x, 92, 28, 58))
        pygame.draw.rect(self.surface, (30, 12, 54), (0, 150, WIDTH, 95))
        for x in range(-scroll // 2, WIDTH + 80, 80):
            pygame.draw.line(self.surface, (65, 230, 255), (x, 245), (x + 34, 175), 2)
        pygame.draw.rect(self.surface, (53, 20, 77), (0, 245, WIDTH, 75))
        for x in range(-scroll, WIDTH + 72, 72):
            pygame.draw.rect(self.surface, (255, 60, 181), (x, 278, 36, 4))
        pygame.draw.circle(self.surface, (255, 215, 80), (350, 115), 16)  # adult background performer
        pygame.draw.polygon(self.surface, (65, 230, 255), ((336, 150), (350, 124), (364, 150)))
        pygame.draw.rect(self.surface, (255, 60, 181), (100, 235, 20, 34))  # player
        self._label(stage.title, 8, 8, (255, 215, 80))
        self._label(f"HP {run.health}  SCORE {run.score}  DIST {int(run.distance)}", 8, 29)
        self._label("II", 448, 8)
        self._label(stage.bark, 16, 185, (255, 170, 220))
        if not run.pigeon_met and run.distance >= 400:
            self._label("PACKET PIDGE: tap right to talk!", 128, 78, (65, 230, 255))
        elif run.pigeon_met and not run.hidden_pickup_found:
            self._label(f"PIDGE: swipe up for hidden {stage.pickup.value}!", 96, 78, (65, 230, 255))
        if run.boss is not None:
            self._label(f"PROMOTER PHASE {run.boss.phase.name.replace('_', ' ')}", 126, 52, (255, 60, 181))
            self._label("Use Pidge's swipe-up distraction four times.", 112, 95)

    def _draw_results(self) -> None:
        self._label("DISTRICT RESULT", 158, 95, (65, 230, 255))
        self._label(self.last_result, 100, 132, (255, 215, 80))
        self._label("Tap for stage select", 145, 192)
