# Neon Siren source contract

Neon Siren is a fictional adult woman, age 25+. She is the hot-magenta, ultraviolet,
and chrome-white mascot enemy described in `docs/CHARACTER_BIBLE.md`. Her oversized
ring-light phone is her readable camera-flash telegraph. Keep the result glamorous,
funny, and non-explicit: opaque bodysuit coverage, visible hands and feet, no genital
detail, nipples, real-person likeness, low-angle crotch framing, or sexual interaction.

## Artist handoff

For Scenario, Midjourney, Leonardo, or a comparable generator, begin every prompt with
`fictional adult woman, age 25+`. Request: `side-facing arcade-game character,
three-quarter torso, tall hourglass silhouette, huge swept ponytail, metallic high-cut
stage bodysuit, thigh-high boots, translucent cropped coat, oversized hoops,
holographic ring-light phone, hot magenta ultraviolet chrome-white, transparent
background, full body, hands and feet visible, 16-bit pixel-painted game art`.

Negatives: `minor, young-looking, nude, nipples, genitalia, explicit sex, real person,
cropped limbs, fisheye, extreme foreshortening, low-angle crotch`. Generate reference
art only; clean and redraw the approved result before export.

## Turnaround and poses

- Supply a 2048 px transparent master render plus front, back, side, and three-quarter
  turnarounds. The game-facing direction is right, with a three-quarter torso.
- Keep both feet on the ground line and the pelvis, shoulders, face, hands, phone, and
  ring light consistent between frames. Do not crop limbs or props.
- Supply these animations exactly: `idle` (6), `walk` (8), `telegraph` (5), `attack`
  (7), `hit` (3), and `disrupted` (6). The telegraph plants one heel and raises the
  ring-light phone; attack fires a non-graphic flash pulse; disrupted regains dignity
  and exits annoyed.

## Pi sheet export

- Export one RGBA PNG sheet per animation to `sheets/neon_siren_<animation>.png`.
- Each frame is exactly 128×128 px, arranged left-to-right in the documented order.
  Every sheet is one frame high; sheet width is `128 × frame count`.
- Use a full 8-bit alpha channel and transparent pixels outside the character. Do not
  bake backgrounds, shadows, or matte colours into transparent areas.
- The immutable gameplay pivot is bottom-centre `(64, 116)` in every 128×128 frame.
  Feet touch the 116 px ground line. Keep the silhouette inside the canvas.
- Use lowercase ASCII filenames matching `neon_siren_<animation>.png`. Update
  `assets/manifests/characters.json`, then run:

  ```sh
  python tools/validate_sprites.py
  python tools/export_esp32_assets.py --size 64
  ```

Only replace an approved sheet with the same name, dimensions, frame count, pivot, and
transparent RGBA contract. The committed sheets are non-explicit production placeholders.
