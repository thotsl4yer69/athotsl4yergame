# Copilot coding instructions

You are building a complete, shippable Raspberry Pi arcade game called **TH0TSL4YER69: Packet Loss**.

## Product constraints

- Target Raspberry Pi Zero 2 W.
- Native resolution is exactly 480×320 landscape.
- Input is a single-touch XPT2046 resistive touchscreen. Never require multitouch.
- Desktop mouse input must emulate touch for development.
- Use Python 3 and Pygame/SDL2 unless a documented benchmark proves another stack is superior.
- Maintain at least 30 FPS on a Pi Zero 2 W.
- Avoid heavyweight dependencies, browsers, Electron, web servers, and runtime asset downloads.
- The game must run offline.

## Content and tone

- This is fictional adult nightclub satire.
- Every human character is explicitly 21+.
- Characters may be exaggerated adult pin-up caricatures with neon clubwear, burlesque or pole-dance-inspired silhouettes, pronounced curves, and playful animation.
- Do not create explicit sex acts, genital detail, sexual violence, non-consensual sexual interactions, or characters who look underage.
- Combat is slapstick/non-graphic. Enemies are algorithmic clout creatures, not realistic people.
- Touch input controls gameplay actions and menus; do not make body-groping mechanics.

## Engineering rules

- Prefer a small, readable module structure over one giant file.
- Separate game state, rendering, input, entities, audio, assets, configuration, and persistence.
- Use deterministic random seeds in tests.
- All calculations should be resolution-independent internally, then rendered to 480×320.
- Add type hints to public functions.
- Add docstrings where behaviour is not obvious.
- Never swallow exceptions silently.
- Save data atomically and tolerate corrupted save files.
- Include a `--windowed` developer mode and a `--touch-debug` overlay.
- Include a headless test mode using SDL's dummy video driver.

## Definition of done

A task is not complete merely because code was generated. It is complete only when:

1. The game launches successfully.
2. Automated tests pass.
3. Touch gestures are testable with mouse input.
4. No missing assets crash the game; fallbacks are provided.
5. Performance-sensitive loops avoid unnecessary allocations.
6. README setup instructions are updated.
7. A screenshot or short capture is attached to the PR when visual behaviour changes.

## Workflow

- Work issue-by-issue.
- Start each issue by restating acceptance criteria in the PR body.
- Keep PRs focused and runnable.
- Do not redesign unrelated systems without explaining why.
- When hardware cannot be tested, add a reproducible simulator test and clearly flag the hardware verification step.
