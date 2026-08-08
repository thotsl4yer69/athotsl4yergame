"""Command-line launcher."""

from __future__ import annotations

import argparse
import os

from .game import Game


def main() -> None:
    """Launch Packet Loss in fullscreen by default."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--windowed", action="store_true", help="run in a 480x320 desktop window")
    parser.add_argument("--touch-debug", action="store_true", help="show the last unified gesture sample")
    parser.add_argument("--headless-test", action="store_true", help="run a short SDL dummy-driver smoke test")
    arguments = parser.parse_args()
    if arguments.headless_test:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    Game(windowed=arguments.windowed or arguments.headless_test, touch_debug=arguments.touch_debug).run(
        frame_limit=2 if arguments.headless_test else None
    )


if __name__ == "__main__":
    main()
