#pragma once

#include <cstddef>
#include <cstdint>

namespace packet_loss {

struct NamedId {
  const char* id;
  const char* name;
};

enum class EnemyId : uint8_t {
  NeonSiren,
  VelvetVandal,
  BottleServiceValkyrie,
};

enum class PickupId : uint8_t {
  Krn,
  ThinkingDust,
};

enum class StageId : uint8_t {
  TheQueue,
  MainFloorMeltdown,
  BathroomEconomy,
};

static constexpr NamedId kEnemyManifest[] = {
    {"neon_siren", "Neon Siren"},
    {"velvet_vandal", "Velvet Vandal"},
    {"bottle_service_valkyrie", "Bottle-Service Valkyrie"},
};

static constexpr NamedId kPickupManifest[] = {
    {"krn", "KRN"},
    {"thinking_dust", "Thinking Dust"},
};

static constexpr NamedId kHelperManifest[] = {
    {"packet_pidge", "Packet Pidge"},
};

struct StageDefinition {
  StageId id;
  const char* id_text;
  const char* name;
  uint16_t duration_seconds;
  uint8_t enemy_interval_ticks;
  uint8_t base_enemy_speed;
};

// Lite stages preserve the Raspberry Pi campaign IDs while shortening each run.
static constexpr StageDefinition kStageManifest[] = {
    {StageId::TheQueue, "the_queue", "The Queue", 36, 105, 1},
    {StageId::MainFloorMeltdown, "main_floor_meltdown", "Main Floor Meltdown", 42, 82, 2},
    {StageId::BathroomEconomy, "bathroom_economy", "Bathroom Economy", 48, 68, 2},
};

constexpr size_t kEnemyCount = sizeof(kEnemyManifest) / sizeof(kEnemyManifest[0]);
constexpr size_t kPickupCount = sizeof(kPickupManifest) / sizeof(kPickupManifest[0]);
constexpr size_t kStageCount = sizeof(kStageManifest) / sizeof(kStageManifest[0]);

}  // namespace packet_loss
