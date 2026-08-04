# ESP32-S3 Lite edition

The ESP32 edition is a separate, reduced renderer that shares the Pi game's identity, touch grammar, enemy names and balance targets. It is not expected to run Python/Pygame assets unchanged.

## Recommended hardware

- ESP32-S3 with 8 MB PSRAM and at least 8 MB flash
- 480×320 ILI9488 or ST7796 SPI display
- XPT2046 resistive touch controller
- Optional I2S amplifier for audio

The original ESP32-C3 Super Mini is unsuitable for the full game because of RAM, flash, GPIO and display-throughput constraints. It may later host a tiny score companion or one-button minigame.

## Firmware stack

- PlatformIO
- Arduino framework initially
- TFT_eSPI renderer
- XPT2046_Touchscreen input
- RGB565 sprite assets generated from the same source art used by the Pi build

## Embedded scope

- 30 FPS target, falling back to 20 FPS on slower SPI buses
- One stage at a time
- Maximum three active enemies
- Small fixed-size entity arrays; no per-frame heap allocation
- Indexed/RGB565 sprite sheets stored in flash or PSRAM
- Mono or short PCM effects, no streamed soundtrack initially
- NVS high-score save

## Pin configuration

Display and touch pins vary by module. Configure `TFT_eSPI/User_Setup.h`, `TOUCH_CS`, and `TOUCH_IRQ` before compiling. Do not assume the Raspberry Pi display pinout is electrically compatible with an ESP32-S3.

## Build

```bash
cd esp32
pio run
pio run --target upload
pio device monitor
```

## Asset conversion pipeline

1. Keep master art as transparent PNG sprite sheets.
2. Validate fixed frame dimensions and pivots.
3. Export Pi assets unchanged as PNG.
4. Quantize ESP32 assets to a limited palette or RGB565.
5. Generate C arrays or LittleFS blobs during the build.
6. Test RAM use and SPI transfer time before adding more frames.
