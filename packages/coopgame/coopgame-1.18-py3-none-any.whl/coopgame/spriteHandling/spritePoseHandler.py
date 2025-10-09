import pygame

from coopgame.spriteHandling.spritesheet import SpriteSheet
from coopgame.spriteHandling.spriteFolder import SpriteFolderHandler
from typing import Dict, List, Tuple
from cooptools.toggles import IntegerRangeToggleable

class SpritePoseHandler:

    @classmethod
    def from_spritesheet(cls,
                         sprite_sheet: SpriteSheet,
                         pose_def: Dict[str, Tuple[int, int, int]], #{poseName: [row, start_idx, end_idx]}
                         colorkey: int = -1, allow_wrap: bool=True):

        surf_getter = lambda row, colorkey, start, end: tuple(sprite_sheet.load_row_strip(row, colorkey=colorkey)[start:end])

        poses = {
            pose: surf_getter(attrs[0], colorkey, attrs[1], attrs[2]) for pose, attrs in pose_def.items()
        }

        return SpritePoseHandler(poses=poses)

    @classmethod
    def from_spritefolder(cls,
                          sprite_folder: SpriteFolderHandler):
        return SpritePoseHandler(sprite_folder.poses)

    def __init__(self,
                 poses: Dict[str, List[pygame.Surface]],
                 default_pose: str=None):
        self.poses = poses
        self._pose_idx = IntegerRangeToggleable(0, len(self.poses) - 1)
        self._pose_idx_map = {
            ii: name for ii, name in enumerate(self.poses.keys())
        }
        self._name_pose_idx_map = {
            name: ii for ii, name in enumerate(self.poses.keys())
        }

        self._animation_idx: IntegerRangeToggleable = self._a_valid_integer_range_for_current_pose()

        if default_pose is not None:
            self.set_pose(default_pose)

    def get_pose(self):
        return self.poses[self._pose_idx_map[self._pose_idx.value]]

    def get_current(self):
        try:
            return {
                'pose': self._pose_idx_map[self._pose_idx.value],
                'animation_idx':self._animation_idx.value,
                'surface': self.get_pose()[self._animation_idx.value]
            }

        except Exception as e:
            raise e

    def increment_pose(self, loop: bool=True):
        self._pose_idx.toggle(on_toggle_callbacks=[lambda val: self._init_animation_indexer()],
                              loop=loop)

    def decrement_pose(self, loop: bool=True):
        self._pose_idx.toggle(reverse=True,
                              on_toggle_callbacks=[lambda val: self._init_animation_indexer()],
                              loop=loop
                              )

    def set_pose(self, pose: str):
        self._pose_idx.set_value(self._name_pose_idx_map[pose],
                                 on_toggle_callbacks=[lambda val: self._init_animation_indexer()])

    def _a_valid_integer_range_for_current_pose(self):
        return IntegerRangeToggleable(0, len(self.poses[self._pose_idx_map[self._pose_idx.value]]) - 1)

    def _init_animation_indexer(self):
        self._animation_idx = self._a_valid_integer_range_for_current_pose()

    def increment_animation(self, loop: bool=True):
        self._animation_idx.toggle(loop=loop)

    def decrement_animation(self, loop: bool=True):
        self._animation_idx.toggle(reverse=True, loop=loop)

    @property
    def Shape(self) -> Tuple[int, int]:
        first_image = next(iter(self.poses.values()))[0]
        width = first_image.get_width()
        height = first_image.get_height()
        return width, height

    @property
    def AnimationEnded(self) -> bool:
        return self._animation_idx.value == self._animation_idx.max