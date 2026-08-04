#include <Arduino.h>
#include <Preferences.h>
#include <SPI.h>

#include "atlas.h"
#include "game.h"
#include "generated_assets.h"
#include "gesture.h"

#ifndef PACKET_LOSS_TFT_WIDTH
#define PACKET_LOSS_TFT_WIDTH 320
#endif
#ifndef PACKET_LOSS_TFT_HEIGHT
#define PACKET_LOSS_TFT_HEIGHT 240
#endif
#ifndef PACKET_LOSS_TFT_SPI_HZ
#define PACKET_LOSS_TFT_SPI_HZ 40000000
#endif
#ifndef PACKET_LOSS_TOUCH_SPI_HZ
#define PACKET_LOSS_TOUCH_SPI_HZ 2000000
#endif
#ifndef PACKET_LOSS_HAS_TOUCH
#define PACKET_LOSS_HAS_TOUCH 1
#endif

namespace {

constexpr int8_t kTftCs = 10;
constexpr int8_t kTftDc = 9;
constexpr int8_t kTftReset = 8;
constexpr int8_t kTouchCs = 7;
constexpr int8_t kSpiSck = 12;
constexpr int8_t kSpiMiso = 13;
constexpr int8_t kSpiMosi = 11;

#ifndef PACKET_LOSS_TOUCH_MIN_X
#define PACKET_LOSS_TOUCH_MIN_X 240
#endif
#ifndef PACKET_LOSS_TOUCH_MAX_X
#define PACKET_LOSS_TOUCH_MAX_X 3850
#endif
#ifndef PACKET_LOSS_TOUCH_MIN_Y
#define PACKET_LOSS_TOUCH_MIN_Y 200
#endif
#ifndef PACKET_LOSS_TOUCH_MAX_Y
#define PACKET_LOSS_TOUCH_MAX_Y 3800
#endif

class TftDisplay {
 public:
  void begin() {
    pinMode(kTftCs, OUTPUT);
    pinMode(kTftDc, OUTPUT);
    pinMode(kTftReset, OUTPUT);
    digitalWrite(kTftCs, HIGH);
    digitalWrite(kTftReset, LOW);
    delay(20);
    digitalWrite(kTftReset, HIGH);
    delay(120);
    command(0x01);
    delay(150);
    command(0x11);
    delay(120);
    command_data(0x3A, 0x55);
    command_data(0x36, 0x00);
    command(0x21);
    command(0x29);
    delay(20);
  }

  void fill(uint16_t color) { fill_rect(0, 0, PACKET_LOSS_TFT_WIDTH, PACKET_LOSS_TFT_HEIGHT, color); }

  void fill_rect(int16_t x, int16_t y, int16_t width, int16_t height, uint16_t color) {
    if (x < 0) {
      width += x;
      x = 0;
    }
    if (y < 0) {
      height += y;
      y = 0;
    }
    if (x + width > PACKET_LOSS_TFT_WIDTH) {
      width = PACKET_LOSS_TFT_WIDTH - x;
    }
    if (y + height > PACKET_LOSS_TFT_HEIGHT) {
      height = PACKET_LOSS_TFT_HEIGHT - y;
    }
    if (width <= 0 || height <= 0) {
      return;
    }
    SPI.beginTransaction(SPISettings(PACKET_LOSS_TFT_SPI_HZ, MSBFIRST, SPI_MODE0));
    digitalWrite(kTftCs, LOW);
    window(x, y, width, height);
    digitalWrite(kTftDc, HIGH);
    const uint8_t high = color >> 8;
    const uint8_t low = color & 0xFF;
    for (int32_t index = static_cast<int32_t>(width) * height; index-- > 0;) {
      SPI.write(high);
      SPI.write(low);
    }
    digitalWrite(kTftCs, HIGH);
    SPI.endTransaction();
  }

 private:
  void command(uint8_t value) {
    SPI.beginTransaction(SPISettings(PACKET_LOSS_TFT_SPI_HZ, MSBFIRST, SPI_MODE0));
    digitalWrite(kTftCs, LOW);
    digitalWrite(kTftDc, LOW);
    SPI.write(value);
    digitalWrite(kTftCs, HIGH);
    SPI.endTransaction();
  }

  void command_data(uint8_t command_value, uint8_t data) {
    SPI.beginTransaction(SPISettings(PACKET_LOSS_TFT_SPI_HZ, MSBFIRST, SPI_MODE0));
    digitalWrite(kTftCs, LOW);
    digitalWrite(kTftDc, LOW);
    SPI.write(command_value);
    digitalWrite(kTftDc, HIGH);
    SPI.write(data);
    digitalWrite(kTftCs, HIGH);
    SPI.endTransaction();
  }

  void window(int16_t x, int16_t y, int16_t width, int16_t height) {
    digitalWrite(kTftDc, LOW);
    SPI.write(0x2A);
    digitalWrite(kTftDc, HIGH);
    SPI.write(x >> 8);
    SPI.write(x);
    const int16_t right = x + width - 1;
    SPI.write(right >> 8);
    SPI.write(right);
    digitalWrite(kTftDc, LOW);
    SPI.write(0x2B);
    digitalWrite(kTftDc, HIGH);
    SPI.write(y >> 8);
    SPI.write(y);
    const int16_t bottom = y + height - 1;
    SPI.write(bottom >> 8);
    SPI.write(bottom);
    digitalWrite(kTftDc, LOW);
    SPI.write(0x2C);
  }
};

struct CalibratedTouch {
  bool pressed;
  packet_loss::TouchPoint point;
  uint16_t raw_x;
  uint16_t raw_y;
};

class Xpt2046 {
 public:
  void begin() {
    pinMode(kTouchCs, OUTPUT);
    digitalWrite(kTouchCs, HIGH);
  }

  CalibratedTouch read() {
#if PACKET_LOSS_HAS_TOUCH
    const uint16_t raw_x = sample(0xD0);
    const uint16_t raw_y = sample(0x90);
    const bool pressed = raw_x > 50 && raw_y > 50 && raw_x < 4090 && raw_y < 4090;
    return {pressed,
            {scale(raw_x, PACKET_LOSS_TOUCH_MIN_X, PACKET_LOSS_TOUCH_MAX_X,
                   PACKET_LOSS_TFT_WIDTH),
             scale(raw_y, PACKET_LOSS_TOUCH_MIN_Y, PACKET_LOSS_TOUCH_MAX_Y,
                   PACKET_LOSS_TFT_HEIGHT)},
            raw_x, raw_y};
#else
    return {false, {}, 0, 0};
#endif
  }

 private:
  uint16_t sample(uint8_t command) {
    SPI.beginTransaction(SPISettings(PACKET_LOSS_TOUCH_SPI_HZ, MSBFIRST, SPI_MODE0));
    digitalWrite(kTouchCs, LOW);
    SPI.transfer(command);
    const uint16_t value = SPI.transfer16(0) >> 3;
    digitalWrite(kTouchCs, HIGH);
    SPI.endTransaction();
    return value;
  }

  static int16_t scale(uint16_t value, int16_t minimum, int16_t maximum, int16_t size) {
    if (value <= minimum) {
      return 0;
    }
    if (value >= maximum) {
      return size - 1;
    }
    return static_cast<int16_t>((static_cast<int32_t>(value - minimum) * (size - 1)) /
                                (maximum - minimum));
  }
};

struct SaveRecord {
  uint32_t score;
  uint8_t unlocked_stage;
  uint8_t checksum;
};

class SaveStore {
 public:
  SaveRecord load() {
    Preferences preferences;
    SaveRecord record{};
    if (!preferences.begin("packetloss", true) ||
        preferences.getBytesLength("campaign") != sizeof(record) ||
        preferences.getBytes("campaign", &record, sizeof(record)) != sizeof(record) ||
        record.checksum != checksum(record) || record.unlocked_stage >= packet_loss::kStageCount) {
      record = {};
    }
    preferences.end();
    return record;
  }

  void save(uint32_t score, uint8_t unlocked_stage) {
    SaveRecord record{score, unlocked_stage, 0};
    record.checksum = checksum(record);
    Preferences preferences;
    if (!preferences.begin("packetloss", false) ||
        preferences.putBytes("campaign", &record, sizeof(record)) != sizeof(record)) {
      Serial.println("Unable to save campaign");
    }
    preferences.end();
  }

 private:
  static uint8_t checksum(const SaveRecord& record) {
    uint8_t value = record.unlocked_stage;
    value ^= static_cast<uint8_t>(record.score);
    value ^= static_cast<uint8_t>(record.score >> 8);
    value ^= static_cast<uint8_t>(record.score >> 16);
    return value ^ 0xA7;
  }
};

TftDisplay display;
Xpt2046 touch;
packet_loss::GestureRecognizer gestures;
packet_loss::Game game;
packet_loss::SceneManager scenes(game);
packet_loss::SpriteAtlas courier_atlas;
SaveStore saves;
bool touch_was_pressed = false;
uint32_t next_step_us = 0;
uint32_t next_frame_us = 0;
uint32_t high_score = 0;
bool game_over_saved = false;

void draw_atlas(const packet_loss::SpriteAtlas& atlas, int16_t x, int16_t y, uint8_t scale) {
  for (uint16_t row = 0; row < atlas.height(); ++row) {
    for (uint16_t column = 0; column < atlas.width(); ++column) {
      display.fill_rect(x + column * scale, y + row * scale, scale, scale, atlas.pixel(column, row));
    }
  }
}

void render() {
  constexpr uint16_t kNight = 0x080F;
  display.fill(kNight);
  display.fill_rect(0, 204, PACKET_LOSS_TFT_WIDTH, 36, 0x2104);
  display.fill_rect(4, 4, game.player().health * 2, 6, 0xF800);
  display.fill_rect(4, 12, game.player().special_charge * 2, 4, 0x07FF);
  display.fill_rect(PACKET_LOSS_TFT_WIDTH - 36, 4, 28, 18, 0xF81F);

  if (scenes.scene() == packet_loss::Scene::Title) {
    draw_atlas(courier_atlas, 148, 92, 3);
    display.fill_rect(80, 156, 160, 12, 0xF81F);
    return;
  }
  draw_atlas(courier_atlas, 48, game.player().y - 16, 2);
  for (const packet_loss::Enemy* enemy = game.enemies();
       enemy != game.enemies() + packet_loss::kMaxEnemies; ++enemy) {
    if (enemy->active) {
      display.fill_rect(enemy->x, enemy->y - 20, 14, 20,
                        enemy->id == packet_loss::EnemyId::NeonSiren ? 0xF81F : 0xFFE0);
    }
  }
  for (const packet_loss::Pickup* pickup = game.pickups();
       pickup != game.pickups() + packet_loss::kMaxPickups; ++pickup) {
    if (pickup->active) {
      display.fill_rect(pickup->x, pickup->y, 8, 8,
                        pickup->id == packet_loss::PickupId::Krn ? 0xFFE0 : 0xFFFF);
    }
  }
  if (game.packet_pidge_ticks() > 0) {
    display.fill_rect(88, game.player().y - 30, 10, 6, 0x07FF);
  }
  if (scenes.scene() == packet_loss::Scene::Paused) {
    display.fill_rect(80, 100, 160, 40, 0x780F);
  } else if (scenes.scene() == packet_loss::Scene::GameOver) {
    display.fill_rect(60, 90, 200, 60, 0xF800);
  }
}

}  // namespace

void setup() {
  Serial.begin(115200);
  SPI.begin(kSpiSck, kSpiMiso, kSpiMosi, -1);
  display.begin();
  touch.begin();
  courier_atlas.load(packet_loss::kCourierAtlas);
  const SaveRecord saved = saves.load();
  high_score = saved.score;
  scenes.set_unlocked_stage(saved.unlocked_stage);
  next_step_us = micros();
  next_frame_us = next_step_us;
  Serial.println("Packet Loss ESP32-S3 Lite ready; fixed update 60 Hz, present 30 FPS");
}

void loop() {
  const uint32_t now_us = micros();
  const CalibratedTouch current_touch = touch.read();
  if (current_touch.pressed && !touch_was_pressed) {
    gestures.begin(current_touch.point, millis());
  } else if (!current_touch.pressed && touch_was_pressed) {
    const packet_loss::GestureResult result = gestures.end(current_touch.point, millis());
    scenes.dispatch(result.action);
    Serial.printf("touch raw=%u,%u calibrated=%d,%d action=%u latency=%ums\n", current_touch.raw_x,
                  current_touch.raw_y, current_touch.point.x, current_touch.point.y,
                  static_cast<unsigned>(result.action), result.latency_ms);
  }
  touch_was_pressed = current_touch.pressed;

  uint8_t catch_up = 0;
  while (static_cast<int32_t>(now_us - next_step_us) >= 0 && catch_up++ < 3) {
    scenes.step();
    next_step_us += 16667;
  }
  if (game.score() > high_score) {
    high_score = game.score();
  }
  if (scenes.scene() == packet_loss::Scene::GameOver && !game_over_saved) {
    saves.save(high_score, scenes.unlocked_stage());
    game_over_saved = true;
  } else if (scenes.scene() != packet_loss::Scene::GameOver) {
    game_over_saved = false;
  }
  if (static_cast<int32_t>(now_us - next_frame_us) >= 0) {
    render();
    next_frame_us += 33333;
  }
}
