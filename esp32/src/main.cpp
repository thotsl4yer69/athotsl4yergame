#include <Arduino.h>
#include <TFT_eSPI.h>
#include <XPT2046_Touchscreen.h>

// Configure these pins and TFT_eSPI/User_Setup.h for the chosen ESP32-S3 board/display.
#ifndef TOUCH_CS
#define TOUCH_CS 5
#endif
#ifndef TOUCH_IRQ
#define TOUCH_IRQ 4
#endif

TFT_eSPI tft;
XPT2046_Touchscreen touch(TOUCH_CS, TOUCH_IRQ);

constexpr int SCREEN_W = 480;
constexpr int SCREEN_H = 320;
constexpr int GROUND_Y = 260;

struct Player {
  int health = 100;
  int vibe = 0;
  uint32_t score = 0;
  uint32_t airborneUntil = 0;
  uint32_t attackUntil = 0;
  uint32_t dodgeUntil = 0;
};

Player player;
uint32_t lastFrame = 0;
uint32_t touchStarted = 0;
int16_t touchStartX = 0;
int16_t touchStartY = 0;
bool touching = false;

int16_t mapTouchX(int16_t raw) { return constrain(map(raw, 250, 3850, 0, SCREEN_W), 0, SCREEN_W - 1); }
int16_t mapTouchY(int16_t raw) { return constrain(map(raw, 250, 3850, 0, SCREEN_H), 0, SCREEN_H - 1); }

void applyGesture(int16_t startX, int16_t startY, int16_t endX, int16_t endY, uint32_t duration) {
  const int dx = endX - startX;
  const int dy = endY - startY;
  const uint32_t now = millis();
  if (abs(dy) >= 42 && abs(dy) > abs(dx)) {
    if (dy > 0) player.dodgeUntil = now + 360;
    else if (player.vibe >= 100) player.vibe = 0;
    return;
  }
  if (duration <= 450 && abs(dx) < 42 && abs(dy) < 42) {
    if (endX < SCREEN_W / 2) player.airborneUntil = now + 520;
    else player.attackUntil = now + 180;
  }
}

void readTouch() {
  if (touch.touched()) {
    TS_Point p = touch.getPoint();
    const int16_t x = mapTouchX(p.x);
    const int16_t y = mapTouchY(p.y);
    if (!touching) {
      touching = true;
      touchStarted = millis();
      touchStartX = x;
      touchStartY = y;
    }
  } else if (touching) {
    TS_Point p = touch.getPoint();
    applyGesture(touchStartX, touchStartY, mapTouchX(p.x), mapTouchY(p.y), millis() - touchStarted);
    touching = false;
  }
}

void drawFrame() {
  const uint32_t now = millis();
  tft.fillScreen(TFT_BLACK);
  tft.fillRect(0, 190, SCREEN_W, 130, tft.color565(28, 14, 49));
  tft.drawFastHLine(0, GROUND_Y, SCREEN_W, TFT_MAGENTA);

  const int playerY = GROUND_Y - 58 - (now < player.airborneUntil ? 35 : 0);
  tft.fillCircle(95, playerY - 8, 12, tft.color565(245, 182, 140));
  tft.fillRoundRect(78, playerY, 34, 58, 10, TFT_CYAN);
  if (now < player.attackUntil) tft.drawCircle(128, playerY + 20, 26, TFT_YELLOW);
  if (now < player.dodgeUntil) tft.drawRoundRect(68, playerY - 3, 54, 64, 12, TFT_PURPLE);

  tft.setTextColor(TFT_MAGENTA, TFT_BLACK);
  tft.setTextSize(2);
  tft.drawString("TH0TSL4YER69 // LITE", 8, 8);
  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  tft.setTextSize(1);
  tft.drawString("HP " + String(player.health) + "  VIBE " + String(player.vibe) + "  SCORE " + String(player.score), 8, 38);
  tft.drawString("LEFT TAP JUMP | RIGHT TAP ATTACK | SWIPE DOWN DODGE", 8, 300);
}

void setup() {
  Serial.begin(115200);
  tft.init();
  tft.setRotation(1);
  tft.setSwapBytes(true);
  touch.begin();
  touch.setRotation(1);
  lastFrame = millis();
}

void loop() {
  readTouch();
  const uint32_t now = millis();
  if (now - lastFrame >= 33) {
    player.score += 1;
    drawFrame();
    lastFrame = now;
  }
}
