from coopgame.spriteHandling.sprites import MySprite
from coopgame.models.primitives.orientation import Transform
from typing import Dict, List, Tuple
import pygame
import coopgame.pygamehelpers as help
from coopstructs.geometry.vectors.vectorN import Vector2
from cooptools.colors import Color
import coopgame.spriteHandling.utils as s_util
from dataclasses import dataclass
import coopgame.pointdrawing.point_draw_utils as pdu

@dataclass
class SpriteTransformMapKey:
    id: str
    type: str

    def __hash__(self):
        return hash(self.id)

class SpriteTransformMapper:
    def __init__(self, sprite_transform_map: Dict[SpriteTransformMapKey, Tuple[pygame.Surface, Transform]] = None):
        self._sprite_transform_map: Dict[SpriteTransformMapKey, Tuple[pygame.Surface, Transform]] = {}

        if sprite_transform_map is not None:
            self.register(sprite_transform_map)

    def register(self, sprite_map: Dict[SpriteTransformMapKey, Tuple[pygame.Surface, Transform]]):
        self._sprite_transform_map = {**self._sprite_transform_map, **sprite_map}

    def get_surfaces(self) -> List[Tuple[pygame.Surface, pygame.Rect]]:
        return [
            s_util.transform_sprite(map[0], map[1]) for k, map in self._sprite_transform_map.items()
        ]

    def unregister(self, ids: List[SpriteTransformMapKey]):
        self._sprite_transform_map = {k: v for k, v in self._sprite_transform_map.items() if k not in ids}

    def draw(self, surface: pygame.Surface, debug: bool = False):
        sprites = self.get_surfaces()

        for sprite, pos in sprites:
            surface.blit(sprite, pos)
            if debug:
                help.draw_circle(surface, Vector2.from_tuple(pos.center), radius=3, color=Color.ORANGE, outline_color=Color.BLACK)

    @property
    def SpriteMap(self) -> Dict[SpriteTransformMapKey, Tuple[pygame.Surface, Transform]]:
        return self._sprite_transform_map

if __name__ == "__main__":
    from coopgame.spriteHandling.spritesheet import SpriteSheet
    from coopgame.handleKeyPressedArgs import InputStateHandler, InputAction, PyKeys, PyMouse, InputEvent, basic_key_actions, InputState, pygame_event_handler
    import logging
    from coopgame.gameTimeTracker import GameTimeTracker

    logging.basicConfig(level=logging.INFO)

    pygame.init()
    screen = pygame.display.set_mode((500, 500))


    mapper = SpriteTransformMapper()

    player_sprite = SpriteSheet(
        r'C:\Users\tburns\Downloads\craftpix-net-786503-free-spaceship-pixel-art-sprite-sheets\Fighter\Idle.png', 1,
        1).load_row_strip(0, colorkey=Color.WHITE.value)[0]

    transform = Transform()

    mapper.register({player_sprite: transform})

    print(mapper.get_surfaces())
    transform.Translation.update(vector=(250, 250))
    transform.Scale.update(scale_vector=(2, 2))
    transform.Rotation.update(rotation_point=(26, 32))

    input_state_handler = InputStateHandler(
        key_actions=basic_key_actions(
            up_package=lambda x: transform.Translation.update(delta_vector=(0, -1)),
            down_package=lambda x: transform.Translation.update(delta_vector=(0, 1)),
            left_package=lambda x: transform.Translation.update(delta_vector=(-1, 0)),
            right_package=lambda x: transform.Translation.update(delta_vector=(1, 0)),
            scale_up_package=lambda x: transform.Scale.update(scale_vector=(1.1, 1.1)),
            scale_down_package=lambda x: transform.Scale.update(scale_vector=(0.9, 0.9)),
            rot_left_package=lambda x: transform.Rotation.update(delta_rads=(0.005, 0)),
            rot_right_package=lambda x: transform.Rotation.update(delta_rads=(-0.005, 0)),
        ))
    game_time_tracker = GameTimeTracker(max_fps=60)
    game_time_tracker.set_start()

    while True:
        input_state = InputState(game_time_tracker.update())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

            input_state = pygame_event_handler(input_state, event=event)

        input_state_handler.handle_input(input_state)

        # transform.Translation.update(vector=pygame.mouse.get_pos())
        # transform.Rotation.update(delta_rads=(0.0005, 0, 0))
        sprites = mapper.get_surfaces()

        screen.fill((0, 0, 0))  # fill the screen with black
        #
        # render_sprite, render_rect = rotate(player_sprite, angle=45, pivot=(player_sprite.get_size()[0] / 2, player_sprite.get_size()[1] / 2))
        # screen.blit(render_sprite, render_rect)

        for sprite, pos in sprites:
            screen.blit(sprite, pos)  # draw the ball
            help.draw_circle(screen, Vector2.from_tuple(pos.center), radius=3, color=Color.ORANGE, outline_color=Color.BLACK)
            help.draw_circle(screen, Vector2.from_tuple(transform.Translation.Vector), radius=3, color=Color.BLUE,
                             outline_color=Color.BLACK)

        pygame.display.update()  # update the screen

        # print(transform)