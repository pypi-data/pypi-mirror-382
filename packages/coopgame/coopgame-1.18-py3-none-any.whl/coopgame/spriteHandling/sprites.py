import pygame
import cooptools.geometry_utils.vector_utils as vec
from cooptools.colors import Color
from typing import Dict, Tuple, Any, Union, Callable
from enum import Enum
from coopgame.spriteHandling.spritePoseHandler import SpritePoseHandler

class SpriteOriginPosition(Enum):
    CENTER = 1
    BOTTOM_MIDDLE = 2
    BOTTOM_RIGHT = 3
    TOP_LEFT = 4


class MySprite(pygame.sprite.Sprite):
    def __init__(self,
                 id: str,
                 init_pos: vec.FloatVec,
                 width: int,
                 height: int,
                 sprite_origin_position: SpriteOriginPosition = None
                 ):
        super().__init__()

        self.id = id

        self.surf = None
        self.rect = None

        self.width = None
        self.height = None

        self.set_size(width, height)

        self.set_pos(init_pos, sprite_origin_position)

    @property
    def size(self):
        return (self.width, self.height)

    def set_size(self, width, height):
        if width != self.width or height != self.height:
            self.width = width
            self.height = height

            self.surf = pygame.Surface([width, height]).convert()
            self.surf.fill(Color.PINK.value)
            self.surf.set_colorkey(Color.PINK.value)

            self.rect = self.surf.get_rect()

    @property
    def bottom_center_pos(self) -> vec.FloatVec:
        x = self.rect.x + self.rect.width / 2
        y = self.rect.y + self.rect.height

        return (x, y)

    def _center_from_sprite_origin(self, pos: vec.FloatVec, sprite_origin_position: SpriteOriginPosition):
        if sprite_origin_position == SpriteOriginPosition.CENTER:
            ret = (pos[0], pos[1])
        elif sprite_origin_position == SpriteOriginPosition.BOTTOM_MIDDLE:
            ret = (pos[0], pos[1] - self.surf.get_height() / 2)
        elif sprite_origin_position == SpriteOriginPosition.BOTTOM_RIGHT:
            ret = (pos[0] - self.surf.get_width() / 2, pos[1] - self.surf.get_height() / 2)
        elif sprite_origin_position == SpriteOriginPosition.TOP_LEFT:
            ret = (pos[0] + self.surf.get_width() / 2, pos[1] + self.surf.get_height() / 2)
        else:
            raise NotImplementedError(f"origin pos: {sprite_origin_position} not handled for finding center")
        return ret

    def set_pos(self, pos: vec.FloatVec, sprite_origin_position: SpriteOriginPosition = None):
        if sprite_origin_position is None:
            sprite_origin_position = SpriteOriginPosition.TOP_LEFT

        center = self._center_from_sprite_origin(pos, sprite_origin_position)

        self.rect = self.surf.get_rect(center=center)

    def blit(self, surface: pygame.Surface,
             display_handle: Union[bool, Callable[[], bool]] = False,
             display_rect: Union[bool, Callable[[], bool]] = False):

        surface.blit(self.surf, (self.rect.x, self.rect.y))
        if display_handle and callable(display_handle) and display_handle():
            pygame.draw.rect(surface, Color.RED.value, [self.rect.x, self.rect.y, 1, 1])
        elif display_handle and not callable(display_handle):
            pygame.draw.rect(surface, Color.RED.value, [self.rect.x, self.rect.y, 1, 1])

        if display_rect and callable(display_rect) and display_rect():
            pygame.draw.rect(surface, Color.RED.value, [self.rect.x, self.rect.y, self.rect.width, self.rect.height], 1)
        elif display_rect and not callable(display_handle):
            pygame.draw.rect(surface, Color.RED.value, [self.rect.x, self.rect.y, self.rect.width, self.rect.height], 1)

    def __repr__(self):
        return f"{self.id} {super().__repr__()}"


class RectangleSprite(MySprite):
    def __init__(self, id: str, init_pos: vec.FloatVec, color: Color, width: int, height: int):
        # Call the parent class (Sprite) constructor
        MySprite.__init__(self, id, init_pos, width, height)

        pygame.draw.rect(self.surf, color.value, [0, 0, width, height])


class ImageSprite(MySprite):
    def __init__(self,
                 id: str,
                 init_pos: vec.FloatVec,
                 width: int,
                 height: int):
        # Call the parent class (Sprite) constructor
        MySprite.__init__(self, id, init_pos, width, height)


class AnimatedPoseSprite(MySprite):
    def __init__(self,
                 id:str,
                 init_pos: vec.FloatVec,
                 pose_handler: SpritePoseHandler,
                 animation_cycle_ms: Union[int, Callable[[], int]] = None,
                 width: int = None,
                 height: int = None,
                 sprite_origin_position: SpriteOriginPosition = None,
                 loop:bool=True
                 ):
        self.pose_handler = pose_handler

        # Call the parent class (Sprite) constructor
        pose_w, pose_h = self.pose_handler.Shape
        width = pose_w if not width else width
        height = pose_h if not height else height
        MySprite.__init__(self, id, init_pos, width, height, sprite_origin_position)

        self.loop = loop
        self.animate_timer = 0
        self.animate_cycle = animation_cycle_ms if animation_cycle_ms else 100

        self.image = None
        self._set_image()

    def _set_image(self):
        self.surf.fill(Color.PINK.value)

        self.image = self.pose_handler.get_current()['surface']
        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.surf.blit(self.image, (0, 0))

    def _resolve_animation_cycle(self):
        if type(self.animate_cycle) == int:
            return self.animate_cycle
        else:
            return self.animate_cycle()

    def animate(self,
                delta_time_ms: int):
        self.animate_timer += delta_time_ms
        if self.animate_timer > self._resolve_animation_cycle():
            self.increment_animation_phase(loop=self.loop)
            self.animate_timer = 0

    def increment_animation_phase(self, loop: bool = True):
        ''':return True if animation cycle has completed, False if still in cycle
        :param loop allows caller to specify whether or not to loop the aniimation (default True)'''
        ret = False
        if self.pose_handler.AnimationEnded and not loop:
            ret = True

        self.pose_handler.increment_animation(loop=loop)
        self._set_image()
        return ret

    def set_animation_cycle(self, animation_cycle_ms: Union[int, Callable[[], int]]):
        self.animate_cycle = animation_cycle_ms

class AnimatedSprite(MySprite):
    def __init__(self,
                 id: str,
                 init_pos: vec.FloatVec,
                 animation_dict: Dict[Any, Tuple],
                 default_animation_key=None,
                 animation_cycle_ms: Union[int, Callable[[], int]] = None,
                 width: int = None,
                 height: int = None,
                 sprite_origin_position: SpriteOriginPosition = None,
                 loop: bool = False):

        self._animation_dict = animation_dict

        self._animation_key = default_animation_key
        self._animation_index = 0

        # Call the parent class (Sprite) constructor
        first_image = next(iter(self._animation_dict.values()))[0]
        width = first_image.get_width() if not width else width
        height = first_image.get_height() if not height else height
        MySprite.__init__(self, id, init_pos, width, height, sprite_origin_position)

        self.loop = loop
        self.animate_timer = 0
        self.animate_cycle = animation_cycle_ms if animation_cycle_ms else 100

        self.image = None
        self._set_image()

    def set_animation(self, animation: str):
        if animation in self._animation_dict.keys() and animation != self.current_animation:
            self._animation_key = animation
            self._animation_index = 0

    def increment_animation_phase(self, loop: bool = True):
        ''':return True if animation cycle has completed, False if still in cycle
        :param loop allows caller to specify whether or not to loop the aniimation (default True)'''
        ret = False
        self._animation_index += 1
        if self._animation_index >= len(self._animation_dict[self._animation_key]):
            self._animation_index = 0 if loop else len(self._animation_dict[self._animation_key]) - 1
            ret = True

        self._set_image()
        return ret

    def _set_image(self):
        self.surf.fill(Color.PINK.value)
        self.image = self._animation_dict[self._animation_key][self._animation_index]
        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.surf.blit(self.image, (0, 0))

    @property
    def current_animation(self):
        return self._animation_key

    def _resolve_animation_cycle(self):
        if type(self.animate_cycle) == int:
            return self.animate_cycle
        else:
            return self.animate_cycle()

    def animate(self,
                delta_time_ms: int):
        self.animate_timer += delta_time_ms
        if self.animate_timer > self._resolve_animation_cycle():
            self.increment_animation_phase(self.loop)
            self.animate_timer = 0

