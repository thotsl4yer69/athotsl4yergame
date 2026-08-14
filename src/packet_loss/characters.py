"""Character sprite manifest parsing and cached Pi sprite loading."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import pygame


class CharacterManifestError(ValueError):
    """Raised when a character asset manifest cannot be used safely."""


@dataclass(frozen=True, slots=True)
class SpriteAnimation:
    """One fixed-canvas animation sheet declared by the character manifest."""

    name: str
    sheet: Path
    frames: int
    fps: int


@dataclass(frozen=True, slots=True)
class CharacterDefinition:
    """A manifest character with immutable source canvas information."""

    character_id: str
    canvas_size: tuple[int, int]
    pivot: tuple[int, int]
    animations: dict[str, SpriteAnimation]


def project_root() -> Path:
    """Return the repository root used by source asset manifests."""

    return Path(__file__).resolve().parents[2]


def _as_positive_int(raw: Any, field_name: str) -> int:
    if not isinstance(raw, int) or raw <= 0:
        raise CharacterManifestError(f"{field_name} must be a positive integer")
    return raw


def load_character_manifest(path: str | Path | None = None) -> dict[str, CharacterDefinition]:
    """Parse the repository character manifest without loading image files."""

    manifest_path = Path(path) if path is not None else project_root() / "assets/manifests/characters.json"
    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise CharacterManifestError(f"cannot read manifest: {manifest_path}") from exc
    except json.JSONDecodeError as exc:
        raise CharacterManifestError(f"invalid JSON in manifest: {exc}") from exc
    if not isinstance(raw, dict) or raw.get("schema_version") != 1:
        raise CharacterManifestError("manifest schema_version must be 1")
    characters = raw.get("characters")
    if not isinstance(characters, list) or not characters:
        raise CharacterManifestError("manifest characters must be a non-empty list")

    definitions: dict[str, CharacterDefinition] = {}
    root = project_root().resolve()
    for index, character in enumerate(characters):
        if not isinstance(character, dict):
            raise CharacterManifestError(f"characters[{index}] must be an object")
        character_id = character.get("id")
        if not isinstance(character_id, str) or not character_id or character_id in definitions:
            raise CharacterManifestError(f"characters[{index}] has a duplicate or empty id")
        if not isinstance(character.get("adult_age_minimum"), int) or character["adult_age_minimum"] < 25:
            raise CharacterManifestError(f"{character_id}: adult_age_minimum must be at least 25")
        canvas = character.get("canvas")
        if not isinstance(canvas, dict) or canvas.get("transparent") is not True:
            raise CharacterManifestError(f"{character_id}: canvas must require transparency")
        width = _as_positive_int(canvas.get("width"), f"{character_id}.canvas.width")
        height = _as_positive_int(canvas.get("height"), f"{character_id}.canvas.height")
        pivot = canvas.get("pivot")
        if (
            not isinstance(pivot, list)
            or len(pivot) != 2
            or not all(isinstance(value, int) for value in pivot)
            or not 0 <= pivot[0] < width
            or not 0 <= pivot[1] < height
        ):
            raise CharacterManifestError(f"{character_id}: canvas pivot must be within the canvas")
        raw_animations = character.get("animations")
        if not isinstance(raw_animations, dict) or not raw_animations:
            raise CharacterManifestError(f"{character_id}: animations must be a non-empty object")
        animations: dict[str, SpriteAnimation] = {}
        for name, animation in raw_animations.items():
            if not isinstance(name, str) or not isinstance(animation, dict):
                raise CharacterManifestError(f"{character_id}: invalid animation entry")
            sheet = animation.get("sheet")
            if not isinstance(sheet, str) or not sheet:
                raise CharacterManifestError(f"{character_id}.{name}: sheet must be a path")
            resolved_sheet = (project_root() / sheet).resolve()
            if not resolved_sheet.is_relative_to(root):
                raise CharacterManifestError(f"{character_id}.{name}: sheet must stay within project root")
            animations[name] = SpriteAnimation(
                name=name,
                sheet=resolved_sheet,
                frames=_as_positive_int(animation.get("frames"), f"{character_id}.{name}.frames"),
                fps=_as_positive_int(animation.get("fps"), f"{character_id}.{name}.fps"),
            )
        definitions[character_id] = CharacterDefinition(
            character_id=character_id,
            canvas_size=(width, height),
            pivot=(pivot[0], pivot[1]),
            animations=animations,
        )
    return definitions


@lru_cache(maxsize=1)
def load_neon_siren_frames() -> dict[str, tuple[pygame.Surface, ...]]:
    """Load scaled Neon Siren frames, returning an empty map when assets are unavailable."""

    try:
        definition = load_character_manifest()["neon_siren"]
        frames_by_animation: dict[str, tuple[pygame.Surface, ...]] = {}
        for name, animation in definition.animations.items():
            sheet = pygame.image.load(animation.sheet)
            expected_size = (definition.canvas_size[0] * animation.frames, definition.canvas_size[1])
            if sheet.get_size() != expected_size:
                raise CharacterManifestError(
                    f"{animation.sheet}: expected {expected_size[0]}x{expected_size[1]} sheet"
                )
            frames_by_animation[name] = tuple(
                pygame.transform.scale(
                    sheet.subsurface(
                        (frame * definition.canvas_size[0], 0, *definition.canvas_size)
                    ),
                    (64, 64),
                )
                for frame in range(animation.frames)
            )
        return frames_by_animation
    except (CharacterManifestError, OSError, pygame.error):
        return {}
