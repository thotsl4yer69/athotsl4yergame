# Campaign bible

## District 1: Velvet Entry

The opening district is a fictional adult (21+) nightclub satire. Its five
stable stage IDs are `d1_queue`, `d1_coat_check`, `d1_main_floor`,
`d1_bathroom_economy`, and `d1_promoter`. The Python stage loader exports the
same IDs and balance names to reduced ESP32 data, so companion builds do not
need a translation table.

Each stage puts Packet Pidge at the mid-stage interaction point. After speaking
to Pidge, a swipe-up retrieves that stage's hidden KRN can or Thinking Dust
route. Pidge's same swipe-up is a non-combat-contact distraction during The
Promoter encounter, which advances its four phases: Guest List, Follower
Flood, Sparkler Pitch, and Final Receipt.

Background adult performers are decorative parallax rendering only. They do
not instantiate gameplay entities or participate in combat collision layers.
