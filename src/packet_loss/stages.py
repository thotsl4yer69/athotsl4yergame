"""Data-driven District 1 definitions shared by desktop and reduced-device builds."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PickupKind(StrEnum):
    KRN_CAN = "krn_can"
    THINKING_DUST = "thinking_dust"


@dataclass(frozen=True, slots=True)
class StageDefinition:
    """A stable stage record. IDs and balance names are protocol-facing."""

    id: str
    balance_name: str
    title: str
    subtitle: str
    pickup: PickupKind
    pickup_hint: str
    bark: str
    parallax: tuple[str, str, str]
    boss: bool = False

    def esp32_data(self) -> dict[str, str | bool]:
        """Return the reduced representation for an ESP32 companion display."""
        return {
            "id": self.id,
            "balance_name": self.balance_name,
            "title": self.title,
            "pickup": self.pickup.value,
            "boss": self.boss,
        }


DISTRICT_1_STAGES: tuple[StageDefinition, ...] = (
    StageDefinition(
        "d1_queue",
        "district_1_queue",
        "1. The Queue",
        "Velvet Entry",
        PickupKind.KRN_CAN,
        "Hop the rope when the pigeon circles the bouncer.",
        "LINE UPDATE: personality verification pending",
        ("rainy alley", "velvet ropes", "neon queue"),
    ),
    StageDefinition(
        "d1_coat_check",
        "district_1_coat_check_collapse",
        "2. Coat Check Collapse",
        "Velvet Entry",
        PickupKind.THINKING_DUST,
        "Jump through the lost-and-found rack after Pidge chirps.",
        "COAT CLAIM: emotionally unavailable",
        ("service corridor", "coat racks", "claim tickets"),
    ),
    StageDefinition(
        "d1_main_floor",
        "district_1_main_floor_meltdown",
        "3. Main Floor Meltdown",
        "Velvet Entry",
        PickupKind.KRN_CAN,
        "Catch the balcony route while Pidge distracts the DJ.",
        "BASS DROP: terms and conditions apply",
        ("club skyline", "dance floor", "laser confetti"),
    ),
    StageDefinition(
        "d1_bathroom_economy",
        "district_1_bathroom_economy",
        "4. Bathroom Economy",
        "Velvet Entry",
        PickupKind.THINKING_DUST,
        "Use the mirror route when Pidge marks the stall.",
        "MIRROR SAYS: hydrate your ambitions",
        ("tile tunnel", "mirror lights", "paper streamers"),
    ),
    StageDefinition(
        "d1_promoter",
        "district_1_promoter_boss",
        "5. The Promoter",
        "Velvet Entry Finale",
        PickupKind.KRN_CAN,
        "Pidge can interrupt the pitch—then claim the hidden can.",
        "GUEST LIST: every adult is 21+",
        ("rooftop haze", "VIP platform", "ticker tape"),
        boss=True,
    ),
)

STAGES_BY_ID = {stage.id: stage for stage in DISTRICT_1_STAGES}


def stage_by_id(stage_id: str) -> StageDefinition:
    """Retrieve a stage by its stable ID."""
    return STAGES_BY_ID[stage_id]
