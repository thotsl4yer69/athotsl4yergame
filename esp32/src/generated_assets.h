#pragma once

#include "atlas.h"

namespace packet_loss {

static constexpr uint8_t kCourierPixels[] = {
    0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 2, 2, 2, 2, 1, 0,
    1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 1, 3, 3, 1, 2, 1,
    1, 2, 2, 2, 2, 2, 2, 1, 0, 1, 2, 1, 1, 2, 1, 0,
    0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 1,
};
static constexpr uint16_t kCourierPalette[] = {0x1021, 0xF81F, 0x07FF, 0xFFE0};
static constexpr AtlasSource kCourierAtlas = {
    8, 8, AtlasFormat::Indexed8, kCourierPixels, sizeof(kCourierPixels), kCourierPalette, 4,
};

}  // namespace packet_loss
