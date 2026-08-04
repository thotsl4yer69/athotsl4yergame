# TH0TSL4YER69: Packet Loss

A touch-first cyberpunk arcade game for a Raspberry Pi Zero 2 W and a 3.5-inch 480×320 XPT2046 resistive touchscreen.

The game is adult nightclub satire. All human characters are explicitly 21+. Visual direction may use exaggerated pin-up proportions, neon clubwear, burlesque styling, and suggestive humour, but no explicit sex acts, genital detail, or sexual violence.

## Hardware target

- Raspberry Pi Zero 2 W
- Raspberry Pi OS Bookworm, 32-bit
- 3.5-inch 480×320 SPI display
- XPT2046 single-touch resistive controller
- No physical buttons required

## Software target

- Python 3.11+
- Pygame/SDL2
- Native 480×320 fullscreen
- 30 FPS minimum on Pi Zero 2 W
- Mouse input must emulate touch during desktop development

## First milestone

Build a polished vertical slice containing:

1. Title screen
2. One playable auto-running level
3. One player character
4. Three adult nightclub enemy archetypes
5. Tap-left jump, tap-right attack, swipe-down dodge, swipe-up special
6. Kirin-style canned drink power-up and fictional Thinking Dust power-up
7. Score, combo, health, pause, restart and local save
8. Touch calibration/debug overlay

See `docs/GAME_SPEC.md` and `.github/copilot-instructions.md` before making changes.
