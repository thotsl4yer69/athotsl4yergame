#pragma once

#include <cstdint>

namespace packet_loss {

enum class Action : uint8_t {
  None,
  Jump,
  Attack,
  Dodge,
  Special,
  Pause,
  Consume,
};

struct TouchPoint {
  int16_t x;
  int16_t y;
};

struct GestureResult {
  Action action;
  uint16_t latency_ms;
};

struct GestureConfig {
  int16_t width;
  int16_t height;
  int16_t swipe_threshold;
  uint16_t tap_max_ms;
  int16_t tap_slop;
  int16_t pause_size;
  int16_t inventory_x;
  int16_t inventory_width;
  int16_t inventory_height;
};

static constexpr GestureConfig kDefaultGestureConfig = {
    320, 240, 24, 250, 12, 40, 232, 40, 40,
};

class GestureRecognizer {
 public:
  explicit GestureRecognizer(const GestureConfig& config = kDefaultGestureConfig) : config_(config) {}

  void begin(TouchPoint point, uint32_t now_ms) {
    start_ = point;
    start_ms_ = now_ms;
    active_ = true;
  }

  GestureResult end(TouchPoint point, uint32_t now_ms) {
    if (!active_) {
      return {Action::None, 0};
    }
    active_ = false;
    const int16_t dx = point.x - start_.x;
    const int16_t dy = point.y - start_.y;
    const uint16_t latency = static_cast<uint16_t>(now_ms - start_ms_);

    if (dy <= -config_.swipe_threshold) {
      return {Action::Special, latency};
    }
    if (dy >= config_.swipe_threshold) {
      return {Action::Dodge, latency};
    }
    if (latency > config_.tap_max_ms || abs16(dx) > config_.tap_slop ||
        abs16(dy) > config_.tap_slop) {
      return {Action::None, latency};
    }
    if (start_.x >= config_.width - config_.pause_size && start_.y < config_.pause_size) {
      return {Action::Pause, latency};
    }
    if (start_.x >= config_.inventory_x &&
        start_.x < config_.inventory_x + config_.inventory_width &&
        start_.y < config_.inventory_height) {
      return {Action::Consume, latency};
    }
    return {start_.x < config_.width / 2 ? Action::Jump : Action::Attack, latency};
  }

 private:
  static int16_t abs16(int16_t value) { return value < 0 ? -value : value; }

  GestureConfig config_;
  TouchPoint start_{};
  uint32_t start_ms_ = 0;
  bool active_ = false;
};

}  // namespace packet_loss
