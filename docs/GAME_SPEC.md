# Game specification

## Core fantasy

The player is a scrappy nightlife courier trapped inside a neon social-media machine. They auto-run through corrupted club districts, dodge algorithm hazards, and break enemies out of clout possession using stylized non-graphic attacks.

## Core loop

1. Auto-run through a short stage.
2. Tap or swipe to avoid hazards and attack.
3. Build combo and Vibe.
4. Collect power-ups.
5. Survive a Whorde encounter.
6. Reach a boss or score checkpoint.
7. Save high score and unlock modifiers.

## Touch controls

The XPT2046 is single-touch, so every action must be an independent gesture:

- Tap left half: jump
- Tap right half: attack
- Swipe down: dodge/slide
- Swipe up: special attack
- Tap top-right icon: pause
- Tap inventory icon: consume selected power-up

Gestures must use configurable thresholds and expose a debug overlay showing raw coordinates, calibrated coordinates, gesture classification and latency.

## Player systems

- Health: 0–100
- Vibe: combo-driven multiplier meter
- Special charge: earned by clean dodges and attacks
- Inventory: maximum two consumables
- Score: distance, enemies disrupted, pickups and combo

## Power-ups

### Kirin-style can

A fictional gold canned drink inspired by Japanese lager packaging but not using copyrighted branding. Restores some health and temporarily increases attack cadence while adding mild screen sway.

### Thinking Dust

A fictional glowing white arcade powder packet. Temporarily slows enemies, highlights hazards and increases score multiplier. Overuse may trigger a comic paranoia filter with fake warning icons; controls must remain reliable.

## Initial enemy archetypes

All characters are adult, clearly stylized and 21+.

### Neon Siren

- Burlesque-inspired cyber-club performer silhouette
- Exaggerated adult pin-up proportions
- Uses a camera-flash stun pulse
- Telegraph: raises phone/ring light before attack

### Clout Leech

- High-fashion influencer parasite
- Tries to latch onto the player and drain Vibe
- Telegraph: follower-count particles converge around it

### Bottle-Service Knight

- Armoured nightclub host with oversized sparkler bottle
- Slow charge attack
- Telegraph: sparkler ignites, then charge lane is shown

## Art direction

- 480×320 native pixel-art or high-resolution pixel-painted style
- Large readable silhouettes
- Neon magenta/cyan/gold palette with dark backgrounds
- Exaggerated adult curves and clubwear are allowed, but no explicit anatomy
- Animation should emphasize swagger, dance movement, hair, clothing and silhouette rather than anatomical close-ups
- Use sprite sheets with consistent pivots, hitboxes and naming

## Vertical slice acceptance criteria

- Stable 480×320 window and fullscreen modes
- Title screen, game screen, pause screen and game-over screen
- One 60–90 second stage loop
- Player run, jump, attack, dodge and hit animations
- Three enemy types with distinct telegraphs
- Two power-ups
- HUD for health, Vibe, score and inventory
- High-score persistence
- Mouse-to-touch simulation
- Touch debug overlay
- Automated tests for gesture classification, collisions, save recovery and deterministic spawning
- No missing-asset crash
- 30 FPS target documented and measured
