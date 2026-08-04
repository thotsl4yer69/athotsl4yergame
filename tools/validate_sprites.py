"""Validate character animation sheets against the production manifest."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

import pygame

from packet_loss.characters import CharacterDefinition, CharacterManifestError, load_character_manifest


class SpriteValidationError(ValueError):
    """Raised when a character sheet violates the source asset contract."""


def _validate_sheet(
    definition: CharacterDefinition, animation_name: str, require_transparency: bool
) -> list[str]:
    animation = definition.animations[animation_name]
    errors: list[str] = []
    expected_name = f"{definition.character_id}_{animation_name}.png"
    if animation.sheet.name != expected_name or not re.fullmatch(r"[a-z0-9_]+\.png", expected_name):
        errors.append(f"{animation.sheet}: filename must be {expected_name}")
    if not animation.sheet.is_file():
        return [*errors, f"{animation.sheet}: missing sheet"]
    try:
        sheet = pygame.image.load(animation.sheet)
    except pygame.error as exc:
        return [*errors, f"{animation.sheet}: cannot read PNG ({exc})"]
    width, height = definition.canvas_size
    expected_size = (width * animation.frames, height)
    if sheet.get_size() != expected_size:
        errors.append(
            f"{animation.sheet}: expected {expected_size[0]}x{expected_size[1]} for "
            f"{animation.frames} {width}x{height} frames, got {sheet.get_width()}x{sheet.get_height()}"
        )
    if require_transparency:
        if not sheet.get_masks()[3]:
            errors.append(f"{animation.sheet}: PNG must have an alpha channel")
        elif not any(
            sheet.get_at((x, y)).a == 0
            for y in range(sheet.get_height())
            for x in range(sheet.get_width())
        ):
            errors.append(f"{animation.sheet}: PNG must contain transparent background pixels")
    return errors


def validate_manifest(manifest_path: str | Path | None = None) -> None:
    """Validate source PNG dimensions, alpha, names, and declared animation frame counts."""

    try:
        definitions = load_character_manifest(manifest_path)
    except CharacterManifestError as exc:
        raise SpriteValidationError(str(exc)) from exc
    errors: list[str] = []
    for definition in definitions.values():
        for animation_name in definition.animations:
            errors.extend(_validate_sheet(definition, animation_name, require_transparency=True))
    if errors:
        raise SpriteValidationError("\n".join(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "assets/manifests/characters.json",
        help="character manifest to validate",
    )
    args = parser.parse_args()
    try:
        validate_manifest(args.manifest)
    except SpriteValidationError as exc:
        print(f"sprite validation failed:\n{exc}", file=sys.stderr)
        return 1
    print(f"sprite validation passed: {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
