# Browser visual target

Zero-dependency HTML5 Canvas build used to validate the 480×320 visual direction before porting animation and layouts to Pygame and ESP32-S3.

Run:

```bash
python -m http.server 8080 -d web_preview
```

Open `http://localhost:8080/?demo=1` for deterministic attract mode, or `?screenshot=1` for the fixed CI/reference frame.

Controls: arrows or A/D to move, Z/space to jump, X to attack. Pointer/touch is split into left, right, jump, and attack zones.
