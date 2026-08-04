#pragma once

#include <cstddef>
#include <cstdint>

namespace packet_loss {

enum class AtlasFormat : uint8_t {
  Rgb565,
  Indexed8,
};

struct AtlasSource {
  uint16_t width;
  uint16_t height;
  AtlasFormat format;
  const uint8_t* pixels;
  size_t pixel_bytes;
  const uint16_t* palette;
  uint16_t palette_size;
};

class SpriteAtlas {
 public:
  bool load(const AtlasSource& source) {
    const size_t expected = static_cast<size_t>(source.width) * source.height *
                            (source.format == AtlasFormat::Rgb565 ? 2U : 1U);
    valid_ = source.width > 0 && source.height > 0 && source.pixels != nullptr &&
             source.pixel_bytes >= expected &&
             (source.format != AtlasFormat::Indexed8 ||
              (source.palette != nullptr && source.palette_size > 0));
    source_ = valid_ ? source : AtlasSource{};
    return valid_;
  }

  uint16_t width() const { return valid_ ? source_.width : 8; }
  uint16_t height() const { return valid_ ? source_.height : 8; }

  uint16_t pixel(uint16_t x, uint16_t y) const {
    if (!valid_ || x >= source_.width || y >= source_.height) {
      return fallback(x, y);
    }
    const size_t index = static_cast<size_t>(y) * source_.width + x;
    if (source_.format == AtlasFormat::Rgb565) {
      return static_cast<uint16_t>(source_.pixels[index * 2]) |
             static_cast<uint16_t>(source_.pixels[index * 2 + 1]) << 8;
    }
    const uint8_t palette_index = source_.pixels[index];
    return palette_index < source_.palette_size ? source_.palette[palette_index] : fallback(x, y);
  }

 private:
  static uint16_t fallback(uint16_t x, uint16_t y) {
    return ((x >> 2) ^ (y >> 2)) & 1U ? 0xF81F : 0x07FF;
  }

  AtlasSource source_{};
  bool valid_ = false;
};

}  // namespace packet_loss
