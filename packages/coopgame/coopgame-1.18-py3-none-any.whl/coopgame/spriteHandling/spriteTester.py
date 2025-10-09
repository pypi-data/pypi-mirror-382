from typing import List

from coopgame.gameTemplate import GameTemplate, BuiltInSurfaceType
from coopgame.spriteHandling.spritePoseHandler import SpritePoseHandler
from coopgame.spriteHandling.spriteFolder import SpriteFolderHandler
from coopgame.spriteHandling.sprites import AnimatedPoseSprite
from coopgame.spriteHandling.spritesheet import SpriteSheet
from cooptools.toggles import IntegerRangeToggleable
import cooptools.geometry_utils.vector_utils as vec
import pygame
import coopgame.pygamehelpers as help
from coopgame.label_drawing import label_drawing_utils as ldu
from coopgame.label_drawing.pyLabel import TextAlignmentType
from cooptools.coopEnum import CardinalPosition
from cooptools.colors import Color
from coopgame.handleKeyPressedArgs import InputState, InputStateHandler, InputAction, InputEvent, InputEventType, basic_key_actions, CallbackPackage
from coopgame.pygame_k_constant_names import PyKeys, PyMouse

SPRITE_DIRS = [
    r'C:\Users\tburns\Downloads\ilyGuy',
    # r'C:\Users\tburns\Downloads\ninjaadventurenew\png',
    # r'C:\Users\tburns\Downloads\freeknight\png',
    # r'C:\Users\tburns\Downloads\zombiefiles\png\male',
    # r'C:\Users\tburns\Downloads\zombiefiles\png\female',
    # r'C:\Users\tburns\Downloads\craftpix-net-786503-free-spaceship-pixel-art-sprite-sheets\Fighter'
]




class SpriteTester(GameTemplate):

    def __init__(self):
        self.animation_cycle = IntegerRangeToggleable(min=100, max=1000, step_size=25)

        input_state_handler = InputStateHandler(
            quit_callback_package=CallbackPackage(down=lambda x: self.quit()),
            debug_callback_package=CallbackPackage(down=lambda x: self.debug_mode_toggle.toggle()),
            fullscreen_callback_package=CallbackPackage(down=lambda x: self.toggle_fullscreen()),
            key_actions=[
                InputAction([InputEvent(PyKeys.K_DOWN, event_type=InputEventType.DOWN)], callback=lambda x: self.animation_cycle.toggle(reverse=True)),
                InputAction([InputEvent(PyKeys.K_UP, event_type=InputEventType.DOWN)], callback=lambda x: self.animation_cycle.toggle()),
                InputAction([InputEvent(PyKeys.K_LEFT, event_type=InputEventType.DOWN)], callback=lambda x: self.Sprite.pose_handler.decrement_pose()),
                InputAction([InputEvent(PyKeys.K_RIGHT, event_type=InputEventType.DOWN)], callback=lambda x: self.Sprite.pose_handler.increment_pose())
        ])

        super().__init__(input_state_handler=input_state_handler)
        # self.sprite_handler = SpritePoseHandler.from_spritefolder(
        #     SpriteFolderHandler(SPRITE_DIRS[4]))
        self.sprite_handler = SpritePoseHandler.from_spritesheet(
            sprite_sheet=SpriteSheet(filename=r'C:\Users\Tj Burns\OneDrive - T-Hive\Desktop\ilyGuy.png',
                                     n_columns=2,
                                     n_rows=3,
                                     x_margin_right=32
                                     ),
            pose_def={
                'waving': (0, 0, 2),
                'idle': (1, 0, 2),
                'walkright': (2, 0, 3)
            }
        )

        self.anim_sprite = AnimatedPoseSprite(
            id='main',
            init_pos=(0, 0),
            pose_handler=self.sprite_handler,
            animation_cycle_ms=lambda: self.animation_cycle.value,
            width=int(self.screen_width / 3),
            height=int(self.screen_height)
        )

    def initialize_game(self):
        pass

    def draw(self, frames: int, debug_mode: bool = False):
        self.anim_sprite.blit(self.screen)
        current_pose_data = self.anim_sprite.pose_handler.get_current()
        ldu.draw_label(self.screen,
                       f"Current Pose: {current_pose_data['pose']}, "
                       f"anim_idx: {current_pose_data['animation_idx']}, "
                       f"anim cycle: {self.animation_cycle.value}",
                       args=ldu.DrawLabelArgs(
                           color=Color.CYAN,
                           font=ldu.DEFAULT_FONT,
                           alignment=TextAlignmentType.TOPLEFT,
                           anchor_alignment=CardinalPosition.TOP_LEFT
                       ),
                       pos=(50, 50))


    def model_updater(self, delta_time_ms: int):
        pass

    def sprite_updater(self, delta_time_ms: int):
        self.anim_sprite.animate(delta_time_ms)

    def on_resize(self):
        pass

    def _increase_animation_cycle(self):
        self.animation_cycle.toggle(loop=False)

    def _decrease_animation_cycle(self):
        self.animation_cycle.toggle(reverse=True, loop=False)

    def update_built_in_surfaces(self, surface_types: List[BuiltInSurfaceType]):
        pass

    @property
    def Sprite(self):
        return self.anim_sprite

if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)

    game = SpriteTester()
    game.main()