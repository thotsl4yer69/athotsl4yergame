#pragma once

#include <cstdint>

#include "campaign_manifest.h"
#include "gesture.h"

namespace packet_loss {

constexpr int16_t kScreenWidth = 320;
constexpr int16_t kGroundY = 198;
constexpr uint8_t kMaxEnemies = 8;
constexpr uint8_t kMaxPickups = 4;

struct Player {
  int16_t y = kGroundY;
  int8_t velocity_y = 0;
  uint8_t health = 100;
  uint8_t vibe = 0;
  uint8_t special_charge = 0;
  uint8_t inventory = 0;
  uint8_t attack_ticks = 0;
  uint8_t dodge_ticks = 0;
};

struct Enemy {
  EnemyId id = EnemyId::NeonSiren;
  int16_t x = 0;
  int16_t y = kGroundY;
  uint8_t speed = 1;
  bool active = false;
};

struct Pickup {
  PickupId id = PickupId::Krn;
  int16_t x = 0;
  int16_t y = kGroundY;
  bool active = false;
};

class Game {
 public:
  void reset(StageId stage) {
    stage_ = stage;
    player_ = Player{};
    score_ = 0;
    tick_ = 0;
    packet_pidge_ticks_ = 0;
    finished_ = false;
    for (Enemy& enemy : enemies_) {
      enemy.active = false;
    }
    for (Pickup& pickup : pickups_) {
      pickup.active = false;
    }
  }

  void dispatch(Action action) {
    if (finished_) {
      return;
    }
    switch (action) {
      case Action::Jump:
        if (player_.y == kGroundY && player_.dodge_ticks == 0) {
          player_.velocity_y = -12;
        }
        break;
      case Action::Attack:
        player_.attack_ticks = 9;
        break;
      case Action::Dodge:
        player_.dodge_ticks = 12;
        break;
      case Action::Special:
        if (player_.special_charge >= 100) {
          player_.special_charge = 0;
          player_.attack_ticks = 16;
        }
        break;
      case Action::Consume:
        consume();
        break;
      default:
        break;
    }
  }

  void step() {
    if (finished_) {
      return;
    }
    ++tick_;
    ++score_;
    update_player();
    spawn();
    update_enemies();
    update_pickups();
    const StageDefinition& definition = kStageManifest[static_cast<uint8_t>(stage_)];
    if (tick_ >= static_cast<uint32_t>(definition.duration_seconds) * 60U ||
        player_.health == 0) {
      finished_ = true;
    }
  }

  const Player& player() const { return player_; }
  const Enemy* enemies() const { return enemies_; }
  const Pickup* pickups() const { return pickups_; }
  uint32_t score() const { return score_; }
  uint32_t tick() const { return tick_; }
  uint16_t packet_pidge_ticks() const { return packet_pidge_ticks_; }
  bool finished() const { return finished_; }

 private:
  void update_player() {
    if (player_.y != kGroundY || player_.velocity_y != 0) {
      player_.y += player_.velocity_y;
      ++player_.velocity_y;
      if (player_.y >= kGroundY) {
        player_.y = kGroundY;
        player_.velocity_y = 0;
      }
    }
    if (player_.attack_ticks > 0) {
      --player_.attack_ticks;
    }
    if (player_.dodge_ticks > 0) {
      --player_.dodge_ticks;
    }
    if (packet_pidge_ticks_ > 0) {
      --packet_pidge_ticks_;
    }
  }

  void spawn() {
    const StageDefinition& definition = kStageManifest[static_cast<uint8_t>(stage_)];
    if (tick_ % definition.enemy_interval_ticks == 0) {
      for (uint8_t index = 0; index < kMaxEnemies; ++index) {
        if (!enemies_[index].active) {
          enemies_[index] = {static_cast<EnemyId>((tick_ / definition.enemy_interval_ticks) %
                                                   kEnemyCount),
                             static_cast<int16_t>(kScreenWidth + 12), kGroundY,
                             definition.base_enemy_speed, true};
          break;
        }
      }
    }
    if (tick_ % 360U == 0) {
      for (Pickup& pickup : pickups_) {
        if (!pickup.active) {
          pickup = {tick_ % 720U == 0 ? PickupId::ThinkingDust : PickupId::Krn,
                    static_cast<int16_t>(kScreenWidth + 8), kGroundY - 24, true};
          break;
        }
      }
    }
  }

  void update_enemies() {
    for (Enemy& enemy : enemies_) {
      if (!enemy.active) {
        continue;
      }
      enemy.x -= enemy.speed;
      if (enemy.x > 98 || enemy.x < 34) {
        continue;
      }
      if (player_.attack_ticks > 0) {
        enemy.active = false;
        score_ += 100;
        player_.vibe = player_.vibe < 95 ? player_.vibe + 5 : 100;
        player_.special_charge = player_.special_charge < 90 ? player_.special_charge + 10 : 100;
      } else if (player_.dodge_ticks == 0 && player_.y >= kGroundY - 8) {
        enemy.active = false;
        player_.health = player_.health > 10 ? player_.health - 10 : 0;
      } else {
        enemy.active = false;
        player_.special_charge = player_.special_charge < 95 ? player_.special_charge + 5 : 100;
      }
    }
  }

  void update_pickups() {
    for (Pickup& pickup : pickups_) {
      if (!pickup.active) {
        continue;
      }
      --pickup.x;
      if (pickup.x <= 76 && pickup.x >= 44 && player_.y >= kGroundY - 12) {
        if (player_.inventory < 2) {
          ++player_.inventory;
        }
        pickup.active = false;
      } else if (pickup.x < 0) {
        pickup.active = false;
      }
    }
  }

  void consume() {
    if (player_.inventory == 0) {
      return;
    }
    --player_.inventory;
    player_.health = player_.health > 75 ? 100 : player_.health + 25;
    packet_pidge_ticks_ = 300;
  }

  StageId stage_ = StageId::TheQueue;
  Player player_{};
  Enemy enemies_[kMaxEnemies]{};
  Pickup pickups_[kMaxPickups]{};
  uint32_t score_ = 0;
  uint32_t tick_ = 0;
  uint16_t packet_pidge_ticks_ = 0;
  bool finished_ = false;
};

enum class Scene : uint8_t {
  Title,
  Playing,
  Paused,
  GameOver,
};

class SceneManager {
 public:
  explicit SceneManager(Game& game) : game_(game) {}

  void dispatch(Action action) {
    if (scene_ == Scene::Title) {
      if (action != Action::None) {
        game_.reset(stage_);
        scene_ = Scene::Playing;
      }
      return;
    }
    if (action == Action::Pause) {
      scene_ = scene_ == Scene::Playing ? Scene::Paused : Scene::Playing;
      return;
    }
    if (scene_ == Scene::Paused) {
      return;
    }
    if (scene_ == Scene::GameOver && action != Action::None) {
      stage_ = static_cast<StageId>((static_cast<uint8_t>(stage_) + 1) % kStageCount);
      game_.reset(stage_);
      scene_ = Scene::Playing;
      return;
    }
    if (scene_ == Scene::Playing) {
      game_.dispatch(action);
    }
  }

  void step() {
    if (scene_ != Scene::Playing) {
      return;
    }
    game_.step();
    if (game_.finished()) {
      scene_ = Scene::GameOver;
      if (static_cast<uint8_t>(stage_) < kStageCount - 1) {
        unlocked_stage_ = static_cast<uint8_t>(stage_) + 1;
      }
    }
  }

  Scene scene() const { return scene_; }
  StageId stage() const { return stage_; }
  uint8_t unlocked_stage() const { return unlocked_stage_; }
  void set_unlocked_stage(uint8_t unlocked_stage) {
    unlocked_stage_ = unlocked_stage < kStageCount ? unlocked_stage : 0;
  }

 private:
  Game& game_;
  Scene scene_ = Scene::Title;
  StageId stage_ = StageId::TheQueue;
  uint8_t unlocked_stage_ = 0;
};

}  // namespace packet_loss
