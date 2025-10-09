# coopgame
Library of tooling and templates used for building games

Example:
```
from coopgame.gameTemplate import GameTemplate
from coopstructs.vectors import Vector2
import pygame
from coopgame.colors import Color
from coopgame.sprites import RectangleSprite

class MyGame(GameTemplate):
    def __init__(self):
        super().__init__()

        self.sprites = pygame.sprite.Group()

    def draw(self, frames):
        for entity in self.sprites:
            self.screen.blit(entity.surf, entity.rect)

    def handle_hover_over(self, mouse_pos_as_vector: Vector2):
        pass

    def handle_left_click(self):
        self.sprites.add(RectangleSprite(self.mouse_pos_as_vector(), Color.BLUE, 10, 10))

    def handle_right_click(self):
        self.sprites.add(RectangleSprite(self.mouse_pos_as_vector(), Color.RED, 20, 30))

    def handle_key_pressed(self, pressed_key):
        if pressed_key == pygame.K_r:
            self.sprites.empty()

if __name__ == "__main__":
    import logging
    import loggingConfig

    loggingConfig.initLogging(loggingLvl=logging.DEBUG)
    game = MyGame()
    game.main()
```