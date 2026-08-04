#include <cassert>
#include <cstring>

#include "atlas.h"
#include "campaign_manifest.h"
#include "game.h"
#include "gesture.h"

int main() {
  using namespace packet_loss;

  static_assert(kStageCount == 3);
  assert(std::strcmp(kEnemyManifest[0].id, "neon_siren") == 0);
  assert(std::strcmp(kEnemyManifest[2].name, "Bottle-Service Valkyrie") == 0);

  GestureRecognizer gestures;
  gestures.begin({20, 100}, 100);
  assert(gestures.end({20, 100}, 150).action == Action::Jump);
  gestures.begin({300, 100}, 200);
  assert(gestures.end({300, 100}, 250).action == Action::Attack);
  gestures.begin({100, 100}, 300);
  assert(gestures.end({100, 130}, 340).action == Action::Dodge);
  gestures.begin({100, 100}, 400);
  assert(gestures.end({100, 70}, 440).action == Action::Special);

  SpriteAtlas missing;
  assert(missing.pixel(0, 0) != missing.pixel(4, 0));
  const uint8_t pixels[] = {0};
  const uint16_t palette[] = {0x1234};
  SpriteAtlas indexed;
  assert(indexed.load({1, 1, AtlasFormat::Indexed8, pixels, sizeof(pixels), palette, 1}));
  assert(indexed.pixel(0, 0) == 0x1234);

  Game game;
  game.reset(StageId::TheQueue);
  game.dispatch(Action::Jump);
  game.step();
  assert(game.player().y < kGroundY);
  for (int i = 0; i < 36 * 60; ++i) {
    game.step();
  }
  assert(game.finished());

  Game completed_game;
  SceneManager scenes(completed_game);
  scenes.dispatch(Action::Jump);
  for (int i = 0; i < 36 * 60; ++i) {
    scenes.step();
  }
  assert(scenes.scene() == Scene::GameOver);
  assert(scenes.unlocked_stage() == 1);
}
