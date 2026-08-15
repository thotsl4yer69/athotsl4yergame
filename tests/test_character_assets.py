from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import pygame
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from packet_loss.characters import CharacterManifestError, load_character_manifest, load_neon_siren_frames
from tools.export_esp32_assets import export_esp32_assets
from tools.validate_sprites import SpriteValidationError, validate_manifest


def _manifest(sheet: Path, frames: int = 2) -> dict[str, object]:
    return {
        "schema_version": 1,
        "characters": [
            {
                "id": "neon_siren",
                "adult_age_minimum": 25,
                "canvas": {"width": 128, "height": 128, "pivot": [64, 116], "transparent": True},
                "animations": {"idle": {"sheet": str(sheet), "frames": frames, "fps": 6}},
            }
        ],
    }


def _write_manifest(tmp_path: Path, sheet: Path, frames: int = 2) -> Path:
    manifest = tmp_path / "characters.json"
    manifest.write_text(json.dumps(_manifest(sheet, frames)), encoding="utf-8")
    return manifest


def _write_sheet(path: Path, size: tuple[int, int], alpha: bool = True) -> None:
    flags = pygame.SRCALPHA if alpha else 0
    sheet = pygame.Surface(size, flags)
    sheet.fill((240, 50, 170, 255))
    if alpha:
        sheet.set_at((0, 0), (0, 0, 0, 0))
    pygame.image.save(sheet, path)


def _repo_tmp_dir(tmp_path: Path) -> Path:
    path = ROOT / "build" / "pytest_character_assets" / tmp_path.name
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_committed_manifest_parses_and_loads_neon_siren_frames() -> None:
    definition = load_character_manifest()["neon_siren"]
    assert definition.pivot == (64, 116)
    assert {name: animation.frames for name, animation in definition.animations.items()} == {
        "idle": 6,
        "walk": 8,
        "telegraph": 5,
        "attack": 7,
        "hit": 3,
        "disrupted": 6,
    }
    frames = load_neon_siren_frames()
    assert len(frames["idle"]) == 6
    assert frames["idle"][0].get_size() == (64, 64)


def test_manifest_rejects_non_adult_character(tmp_path: Path) -> None:
    sheet = _repo_tmp_dir(tmp_path) / "neon_siren_idle.png"
    _write_sheet(sheet, (256, 128))
    manifest = _write_manifest(tmp_path, sheet)
    raw = json.loads(manifest.read_text(encoding="utf-8"))
    raw["characters"][0]["adult_age_minimum"] = 24
    manifest.write_text(json.dumps(raw), encoding="utf-8")

    with pytest.raises(CharacterManifestError, match="at least 25"):
        load_character_manifest(manifest)


def test_manifest_rejects_sheet_outside_project_root(tmp_path: Path) -> None:
    manifest = _write_manifest(tmp_path, Path("../../etc/passwd"))
    with pytest.raises(CharacterManifestError, match="stay within project root"):
        load_character_manifest(manifest)


def test_validator_reports_missing_and_wrong_sized_sheets(tmp_path: Path) -> None:
    missing = _write_manifest(tmp_path, _repo_tmp_dir(tmp_path) / "neon_siren_idle.png")
    with pytest.raises(SpriteValidationError, match="missing sheet"):
        validate_manifest(missing)

    sheet = _repo_tmp_dir(tmp_path) / "neon_siren_idle.png"
    _write_sheet(sheet, (128, 128))
    wrong_sized = _write_manifest(tmp_path, sheet)
    with pytest.raises(SpriteValidationError, match="expected 256x128"):
        validate_manifest(wrong_sized)


def test_validator_reports_missing_alpha_channel(tmp_path: Path) -> None:
    sheet = _repo_tmp_dir(tmp_path) / "neon_siren_idle.png"
    _write_sheet(sheet, (256, 128), alpha=False)
    manifest = _write_manifest(tmp_path, sheet)

    with pytest.raises(SpriteValidationError, match="alpha channel"):
        validate_manifest(manifest)


def test_esp32_export_is_deterministic(tmp_path: Path) -> None:
    first = export_esp32_assets(output_dir=tmp_path / "first", target_size=64)
    second = export_esp32_assets(output_dir=tmp_path / "second", target_size=64)
    assert first.read_bytes() == second.read_bytes()
    first_frame = next((tmp_path / "first" / "neon_siren").glob("*.rgb565"))
    second_frame = tmp_path / "second" / "neon_siren" / first_frame.name
    assert len(first_frame.read_bytes()) == 64 * 64 * 2
    assert hashlib.sha256(first_frame.read_bytes()).digest() == hashlib.sha256(second_frame.read_bytes()).digest()


def test_esp32_export_sorts_output_and_preserves_aspect_ratio(tmp_path: Path) -> None:
    sprites = _repo_tmp_dir(tmp_path) / "sprites"
    sprites.mkdir()
    _write_sheet(sprites / "beta_walk.png", (128, 32))
    _write_sheet(sprites / "beta_idle.png", (128, 32))
    _write_sheet(sprites / "alpha_idle.png", (128, 32))
    manifest = tmp_path / "characters.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "characters": [
                    {
                        "id": "beta",
                        "adult_age_minimum": 25,
                        "canvas": {"width": 64, "height": 32, "pivot": [32, 24], "transparent": True},
                        "animations": {
                            "walk": {"sheet": str(sprites / "beta_walk.png"), "frames": 2, "fps": 6},
                            "idle": {"sheet": str(sprites / "beta_idle.png"), "frames": 2, "fps": 6},
                        },
                    },
                    {
                        "id": "alpha",
                        "adult_age_minimum": 25,
                        "canvas": {"width": 64, "height": 32, "pivot": [32, 24], "transparent": True},
                        "animations": {"idle": {"sheet": str(sprites / "alpha_idle.png"), "frames": 2, "fps": 6}},
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    metadata_path = export_esp32_assets(manifest_path=manifest, output_dir=tmp_path / "out", target_size=64)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert [character["id"] for character in metadata["characters"]] == ["alpha", "beta"]
    assert list(metadata["characters"][1]["animations"]) == ["idle", "walk"]
    frame = tmp_path / "out" / "beta" / "beta_idle_00.rgb565"
    assert len(frame.read_bytes()) == 64 * 32 * 2
