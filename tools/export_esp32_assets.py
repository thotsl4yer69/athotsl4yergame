"""Export approved Pi sheets as deterministic RGB565 and alpha-mask frame data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

import pygame

from packet_loss.characters import load_character_manifest
from tools.validate_sprites import validate_manifest


def _rgb565(pixel: pygame.Color) -> int:
    return ((pixel.r >> 3) << 11) | ((pixel.g >> 2) << 5) | (pixel.b >> 3)


def _write_frame(frame: pygame.Surface, rgb565_path: Path, alpha_path: Path) -> None:
    rgb565 = bytearray(frame.get_width() * frame.get_height() * 2)
    alpha = bytearray(frame.get_width() * frame.get_height())
    index = 0
    for y in range(frame.get_height()):
        for x in range(frame.get_width()):
            pixel = frame.get_at((x, y))
            alpha[index] = pixel.a
            value = _rgb565(pixel) if pixel.a else 0
            rgb565[index * 2] = value & 0xFF
            rgb565[index * 2 + 1] = value >> 8
            index += 1
    rgb565_path.write_bytes(rgb565)
    alpha_path.write_bytes(alpha)


def export_esp32_assets(
    manifest_path: str | Path | None = None,
    output_dir: str | Path = ROOT / "build/esp32_assets",
    target_size: int = 64,
) -> Path:
    """Export all validated character frames as little-endian RGB565 plus alpha masks."""

    if target_size not in {64, 80}:
        raise ValueError("target_size must be 64 or 80")
    manifest = Path(manifest_path) if manifest_path is not None else ROOT / "assets/manifests/characters.json"
    validate_manifest(manifest)
    definitions = load_character_manifest(manifest)
    output_root = Path(output_dir)
    metadata: dict[str, object] = {"format": "rgb565-le+alpha8", "size": target_size, "characters": []}

    for definition in definitions.values():
        character_dir = output_root / definition.character_id
        if character_dir.exists():
            shutil.rmtree(character_dir)
        character_dir.mkdir(parents=True, exist_ok=True)
        character_data: dict[str, object] = {
            "id": definition.character_id,
            "pivot": [
                round(definition.pivot[0] * target_size / definition.canvas_size[0]),
                round(definition.pivot[1] * target_size / definition.canvas_size[1]),
            ],
            "animations": {},
        }
        for name, animation in definition.animations.items():
            sheet = pygame.image.load(animation.sheet)
            animation_data: list[dict[str, object]] = []
            for frame_number in range(animation.frames):
                source = sheet.subsurface(
                    (
                        frame_number * definition.canvas_size[0],
                        0,
                        definition.canvas_size[0],
                        definition.canvas_size[1],
                    )
                )
                frame = pygame.transform.scale(source, (target_size, target_size))
                stem = f"{definition.character_id}_{name}_{frame_number:02d}"
                rgb565_path = character_dir / f"{stem}.rgb565"
                alpha_path = character_dir / f"{stem}.alpha"
                _write_frame(frame, rgb565_path, alpha_path)
                animation_data.append(
                    {
                        "alpha": alpha_path.name,
                        "rgb565": rgb565_path.name,
                    }
                )
            character_data["animations"][name] = {"fps": animation.fps, "frames": animation_data}
        metadata["characters"].append(character_data)
    output_root.mkdir(parents=True, exist_ok=True)
    metadata_path = output_root / "characters_esp32.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return metadata_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=ROOT / "assets/manifests/characters.json")
    parser.add_argument("--output", type=Path, default=ROOT / "build/esp32_assets")
    parser.add_argument("--size", type=int, choices=(64, 80), default=64)
    args = parser.parse_args()
    metadata_path = export_esp32_assets(args.manifest, args.output, args.size)
    print(f"exported ESP32 assets: {metadata_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
