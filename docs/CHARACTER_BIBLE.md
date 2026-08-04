# TH0TSL4YER69 Character Bible

## Rating and intent

This is fictional adult nightclub satire. Every human character is explicitly 25+ and fictional. The visual target is outrageous neon pin-up energy: glamorous, voluptuous, cocky, theatrical, trashy in a deliberate arcade way, and funny.

Characters may wear revealing clubwear, lingerie-inspired costumes, high-cut bodysuits, thigh-high boots, fishnets, metallic micro-jackets, harness accents, pole-dance or burlesque-inspired stagewear, and exaggerated fashion silhouettes.

Do not depict explicit sex acts, genital detail, sexual violence, non-consensual sexual interaction, or characters who appear underage. Touch gestures remain combat, movement, menus, and power-up actions rather than body-touch mechanics.

## Visual pillars

1. **Instant silhouette:** exaggerated hourglass shapes, long legs, huge hair, dramatic heels, and readable props.
2. **Maximum baddie confidence:** every pose should look camera-ready, self-aware, and slightly hostile.
3. **Strip-club sci-fi:** chrome, latex-like materials, LED trims, neon tattoos, ring lights, sparklers, holographic phones, mirrors, smoke, and nightclub architecture.
4. **Arcade readability:** curves and outfit detail must never obscure attack telegraphs or collision shapes.
5. **Movement sells the fantasy:** swagger, hip-led walk cycles, hair bounce, coat tails, earrings, belts, props, and pole choreography matter more than anatomical close-ups.
6. **Funny, not grim:** defeated enemies lose their algorithmic possession, regain their dignity, and storm off annoyed or embarrassed.

## Shared production rules

- Every source prompt includes: `fictional adult woman, age 25+`.
- Side-facing game pose with consistent three-quarter torso rotation.
- Exaggerated bust and hip silhouette is allowed; no exposed nipples or genital detail.
- Hands and feet remain visible in source turnarounds.
- Avoid cropped limbs, extreme foreshortening, fisheye lenses, and low-angle crotch framing.
- Each archetype gets one dominant colour, one signature prop, and one unmistakable telegraph pose.
- Master concept: 2048 px transparent render plus front, side, back, and three-quarter turnaround.
- Raspberry Pi frames: 128×128 transparent PNG, 30 FPS target.
- ESP32-S3 frames: 64×64 or 80×80, indexed palette or RGB565, reduced animation count.

## Flagship cast

### Neon Siren

First-stage ranged enemy and visual mascot. Tall hourglass silhouette, huge swept ponytail, metallic high-cut stage bodysuit, thigh-high boots, translucent cropped coat, oversized hoops, holographic ring-light phone. Hot magenta, ultraviolet, chrome white. Telegraph: plants one heel, turns toward camera, raises ring light, then fires a flash pulse.

Animations: idle 6, walk 8, pose 6, telegraph 5, flash attack 7, hit 3, disrupted 6.

### Velvet Vandal

Fast melee rush enemy. Compact curvy build, asymmetrical bob, velvet corset-style top over opaque bodysuit, garter-inspired straps, platform boots, oversized faux-fur shoulder piece, neon velvet rope used as a lasso. Wine red, black, electric pink. Telegraph: spins rope overhead before lunging.

Animations: idle 5, strut 8, rope spin 6, lunge 6, hit 3, disrupted 5.

### Bottle-Service Valkyrie

Heavy charger. Statuesque, broad-hipped nightclub host in chrome shoulder armour, deep-cut metallic bodysuit, thigh harnesses, towering boots, oversized sparkler bottle shield. Gold, cyan flame, black chrome. Telegraph: sparkler ignites and paints the charge lane.

Animations: idle 6, march 8, ignite 6, charge 8, stagger 4, disrupted 7.

### Algorithm Angel

Aerial support enemy. Glamorous cyber-angel with holographic wing panels, sculpted club dress, sharp heels, luminous hair halo, and floating engagement counters. Pearl white, cyan, acid yellow. Telegraph: wings fold inward while counters converge.

Animations: hover 8, drift 6, summon 7, recoil 3, disrupted 8.

### Afterparty Oracle

Debuff caster and comic wildcard. Voluptuous mystic in layered sheer-effect fabrics over opaque coverage, crystal accessories, enormous hair, impractical platforms, cracked astrology-phone prop. Indigo, gold, toxic green. Telegraph: glowing zodiac circle warns the incoming effect.

Animations: idle 8, cast 8, laugh 5, hit 3, disrupted 7.

### The Main Character

First major boss. Extreme fashion silhouette: enormous coat collar, sculpted metallic bodysuit, asymmetric thigh-high boots, long animated hair, floating camera-drone crown. Adaptive rainbow neon with black outlines. Boss phases: Content Launch, Follower Swarm, Apology Video, Demonetisation Rage.

## Background performers

Pole dancers, bartenders, dancers, hosts, DJs, coat-check attendants, bathroom-gossip NPCs, smokers, rideshare drivers, kebab-shop workers, and afterparty goblins should animate in the background. They are scenery and comic NPCs, not attack targets. Their loops create the feeling of a living nightlife district.

## Approval gate

A character is approved only when:

- identifiable at 64×64
- unmistakably adult
- provocative but non-explicit
- animation pivots remain fixed
- telegraphs remain visible on Pi and ESP32 displays
- no resemblance to a real identifiable person
