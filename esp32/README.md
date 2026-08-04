# ESP32-S3 Lite edition

This PlatformIO project targets an ESP32-S3 DevKitC-1 N16R8 (16 MB flash, 8 MB PSRAM), a
320×240 ST7789 SPI TFT at 40 MHz, and an optional XPT2046 on the same SPI bus. It retains the
campaign IDs from the Raspberry Pi edition: `the_queue`, `main_floor_meltdown`,
`bathroom_economy`, `neon_siren`, `velvet_vandal`, `bottle_service_valkyrie`, `packet_pidge`,
`krn`, and `thinking_dust`.

## Build and flash

```sh
pio run -d esp32
pio run -d esp32 --target upload
pio device monitor -d esp32 -b 115200
```

The build prints an ELF section report and the firmware/PSRAM budgets. The factory partition is
2.5 MiB; keep generated RGB565/indexed atlas data plus code within that budget. Runtime entities
are fixed arrays (8 enemies and 4 pickups) and need under 4 MiB PSRAM; the gameplay update does
not allocate.

The selected 320×240/40 MHz configuration presents at 30 FPS and advances deterministic gameplay
at 60 Hz. Hardware verification is still required when changing displays: the serial line printed
at boot states the frame/update target, and the host check below verifies the fixed-step and
gesture logic without hardware.

```sh
c++ -std=c++17 -Wall -Wextra -pedantic -Iesp32/include esp32/test/host_campaign_test.cpp \
  -o /tmp/packet-loss-host-test && /tmp/packet-loss-host-test
```

## Wiring and calibration

Default SPI pins are SCK=12, MISO=13, MOSI=11, TFT CS/DC/RST=10/9/8, and touch CS=7. Change the
pin constants in `src/main.cpp` for the board wiring. Calibrate the XPT2046 with build flags; no
source edit is needed:

```ini
build_flags =
  -D PACKET_LOSS_TOUCH_MIN_X=240
  -D PACKET_LOSS_TOUCH_MAX_X=3850
  -D PACKET_LOSS_TOUCH_MIN_Y=200
  -D PACKET_LOSS_TOUCH_MAX_Y=3800
```

Touches use the Pi semantics: left/right tap is jump/attack; vertical swipes are dodge/special;
the top-right corner pauses; the neighbouring inventory area consumes. Each release prints raw
and calibrated coordinates, action, and latency to the serial monitor for calibration/debugging.
Set `-D PACKET_LOSS_HAS_TOUCH=0` on displays without XPT2046.

## Assets

`SpriteAtlas` accepts generated little-endian RGB565 or Indexed8 source buffers. Indexed data
must supply a RGB565 palette. Invalid/missing buffers deliberately render cyan/magenta checker
tiles, so missing art remains visible rather than crashing the campaign. `src/generated_assets.h`
contains a tiny indexed example and is the integration point for generated atlas headers.
