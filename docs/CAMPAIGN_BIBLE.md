# TH0TSL4YER69: Packet Loss — Campaign Bible

## Premise

The player is a cooked but strangely capable nightlife courier trapped in a corrupted entertainment district where every venue, alley, bathroom, feed, and afterparty is controlled by The Algorithm. The goal is not to hurt realistic people. The player breaks clout possession, steals back stolen packets, rescues NPCs from engagement loops, and survives increasingly absurd nightlife ecosystems.

The tone is adult, sexy, chaotic, satirical, and self-aware. The player is also a mess. Nobody is morally superior. Every level should feel like a late-night hallucination rendered as a premium 16-bit arcade game.

## Core campaign structure

The campaign is split into districts. Each district contains 3 normal stages, 1 event stage, and 1 boss. A full campaign target is 6 districts, 24 normal/event stages, 6 bosses, plus challenge routes and an endless mode.

Each stage lasts 2–4 minutes on Raspberry Pi. ESP32-S3 Lite uses shorter 45–90 second remixes of the same stages.

## District 1 — Velvet Entry

### 1-1: The Queue

Outdoor velvet-rope line in rain. Neon signs, smokers, rideshare cars, arguing guests, umbrellas, security scanners, puddle reflections, and distant bass pulses.

Gameplay:
- dodge puddles, barriers, and camera flashes
- collect dropped KRN cans and packets near the curb
- pigeon helper tutorial
- first Neon Siren encounters

Background comedy:
- one NPC claims to know the owner
- a guest repeatedly checks the wrong queue
- promoter stamps the same wrist five times

### 1-2: Coat Check Collapse

Fast indoor corridor packed with coats, mirrors, ticket stubs, lost handbags, and aggressive cloakroom machinery.

Gameplay:
- low obstacles encourage dodge
- coat racks swing into lanes
- Velvet Vandals appear
- hidden packet stash behind a jammed locker

### 1-3: Main Floor Meltdown

First full nightclub floor. Multiple pole-dance stages in background, packed bar, lasers, smoke, giant LED wall, dancers, bottle service, and moving light rigs.

Gameplay:
- rhythm-synchronised hazards
- bar-top pickups
- pole-stage spotlight telegraphs
- background performers remain non-combat scenery

### 1-E: Bathroom Economy

Comic event stage in an enormous nightclub bathroom. Mirrors, sinks, cubicles, gossip clusters, phone charging nests, broken hand dryers, and mysterious attendants.

Gameplay:
- packet pickups found beside sinks, cubicle floors, and handbag spill zones
- temporary paranoia effects create fake warning icons
- bathroom queue behaves like a moving obstacle puzzle
- pigeon enters through an air vent and steals one item unless fed

### Boss: The Promoter

A velvet-rope warlord with a tablet, guest-list shield, stamp-gun, and endless reserves of people who insist they are on the list.

Phases:
1. Guest List
2. Plus-One Swarm
3. Venue Capacity
4. Final Entry Denied

## District 2 — Bottle Service Kingdom

### 2-1: Bar Back Blitz

Run behind the bar through glass racks, ice bins, cocktail stations, beer taps, sliding bottles, and furious bartenders.

### 2-2: VIP Booth Siege

Couches, sparklers, velvet partitions, security ropes, giant ice buckets, and influencers filming everything.

### 2-3: Champagne Catwalk

Raised catwalk above the dance floor with dancers, aerial performers, moving lights, confetti cannons, and Bottle-Service Valkyries.

### 2-E: Closing-Time Cleanup

Lights half-on, sticky floors, exhausted staff, abandoned heels, lost phones, half-eaten chips, and powerful floor-cleaning machinery.

### Boss: Bottle-Service Empress

Massive mobile booth fortress with sparkler artillery, ice-bucket shield, and follower-funded reinforcements.

## District 3 — Street Feed

### 3-1: Rideshare Roulette

Outdoor city street full of double-parked cars, scooters, roadworks, phone zombies, club queues, and wrong rideshares.

### 3-2: Servo Revelation

Fluorescent service station at 3:30 AM. Hot-food cabinets, energy drinks, broken freezer hum, fuel price signs, and existential NPC dialogue.

### 3-3: Kebab Prophecy

Late-night takeaway strip. Rotating meat, neon menus, delivery riders, plastic chairs, sauce hazards, and miraculous health pickups.

### 3-E: Tram Stop Limbo

Outdoor transit platform where arrival times continuously change. Wind, rain, ads, strange conversations, and Algorithm Angel ambushes.

### Boss: Surge Pricing

A giant rideshare app daemon that changes lane rules, fare multipliers, and destination markers mid-fight.

## District 4 — Afterparty Protocol

### 4-1: Apartment Stairwell

Cramped stairs, neighbours opening doors, broken intercoms, cigarette smoke, falling cups, and confused guests.

### 4-2: Kitchen Oracle

Crowded kitchen with half-finished drinks, strange fruit bowls, Bluetooth speaker wars, and Afterparty Oracles.

### 4-3: Balcony Buffering

High-rise balcony with skyline, wind gusts, pigeons, drones, cigarette embers, and unstable outdoor furniture.

### 4-E: Bedroom Coat Mountain

Absurd obstacle level across a mountain of jackets, handbags, shoes, chargers, and sleeping NPCs.

### Boss: The Housemate

Fights through passive-aggressive notes, Wi-Fi password changes, power-board attacks, and a final bond-inspection phase.

## District 5 — Influencer Industrial Complex

### 5-1: Content Warehouse

Ring lights, sets, backdrops, makeup tables, rented cars, fake private jets, and content assembly lines.

### 5-2: Wellness Lab

Detox tea vats, crystal conveyors, breathwork chambers, supplement cannons, and manifestation hazards.

### 5-3: Podcast Mine

Rows of microphones and acoustic foam where opinions become physical projectiles.

### 5-E: Apology Studio

A fake bedroom set with carefully placed tissues, neutral clothing, scripted sincerity meters, and monetisation traps.

### Boss: The Main Character

Four phases: Content Launch, Follower Swarm, Apology Video, Demonetisation Rage.

## District 6 — Algorithm Cathedral

### 6-1: Moderation Basement

Endless cubicles, automated bans, captcha walls, terms-of-service traps, and faceless moderation drones.

### 6-2: Engagement Engine

Mechanical factory where likes, comments, outrage, and thirst are converted into energy.

### 6-3: Infinite Scroll

A surreal vertical feed rendered as a side-scrolling gauntlet. Backgrounds constantly swap style and theme.

### 6-E: Dead Account Graveyard

Abandoned profiles, broken avatars, forgotten trends, silent notifications, and ghost followers.

### Final Boss: The Algorithm

The rules change every phase. Scoring systems, safe lanes, enemy values, and pickup effects become unstable. The pigeon is essential for exposing the true weak point.

## Pigeon companion — Packet Pidge

A filthy but loyal city pigeon with a tiny reflective vest and one damaged cybernetic eye.

Functions:
- points toward hidden pickups
- retrieves one missed packet per checkpoint
- briefly distracts an enemy
- steals shiny objects from bosses
- delivers insulting tutorial messages
- can be upgraded with crumbs, chips, and servo pastry fragments

Upgrade branches:
- Scout: stronger hidden-item detection
- Thief: steals boss resources
- Menace: interrupts enemy telegraphs
- Oracle: warns about fake paranoia hazards

The pigeon should never feel cute in a conventional way. It is a suspicious urban survivor that occasionally saves the run.

## Pickups and energy economy

### KRN can

Fictional gold lager-style can. Restores health and grants temporary confidence mode: faster attacks, mild screen sway, louder footsteps, and increased combo gain.

Spawn locations:
- club floor
- bar counter
- outdoor curb
- bathroom sink area
- VIP booth
- afterparty kitchen

### Thinking Dust packet

Fictional glowing white arcade packet. The game treats it as absurd cyberpunk contraband rather than realistic drug instruction.

Effects:
- slows enemy movement
- reveals hazards and hidden routes
- boosts score multiplier
- adds surreal warning overlays
- repeated use triggers comic paranoia visuals but never unreliable controls

Spawn locations:
- nightclub floor
- bathroom cubicle area
- handbag spill zones
- alleyway
- afterparty surfaces
- boss reward drops

### Servo kebab

Large health restore with temporary movement penalty from digestion.

### Chips for Pidge

Companion upgrade currency.

### Mystery wristband

Random temporary modifier: VIP access, free drink, wrong venue, coat-check debt, or security attention.

## Stage composition rules

Every full stage needs:
- foreground gameplay lane
- midground reactive NPC layer
- background venue spectacle
- at least one adult club-performance vignette
- one environmental joke every 15–20 seconds
- one hidden pickup route
- one pigeon interaction
- one short difficulty escalation
- one readable checkpoint

## Retro presentation

Target premium 16-bit/32-bit crossover:
- high-resolution pixel-painted sprites
- strong black or dark-purple outlines
- large expressive animation frames
- parallax backgrounds
- palette cycling for signs and lights
- CRT and scanline options
- chunky arcade typography
- short voice-like text barks rather than full dialogue audio
- stage intro cards and boss warning screens

## Content scalability

Raspberry Pi:
- full backgrounds
- 128×128 character frames
- 6–10 frames per animation
- layered parallax
- more background performers
- richer particle effects

ESP32-S3 Lite:
- 64×64 or 80×80 frames
- 3–5 frames per animation
- 2 background layers
- reduced particles
- shorter stages
- same names, rules, humour, bosses, and companion

## Minimum shipped campaign

Version 1.0 should contain:
- 3 complete districts
- 12 stages
- 3 bosses
- 8 enemy archetypes
- 2 event stages
- pigeon upgrade system
- endless nightclub mode

The remaining districts can follow as free content updates after the engine, export pipeline, and art workflow are stable.
