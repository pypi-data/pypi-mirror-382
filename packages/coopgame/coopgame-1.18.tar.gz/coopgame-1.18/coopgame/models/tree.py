from cooptools.toggles import EnumToggleable
from enum import Enum
from coopgame.models.primitives.gameObject import GameObject
from typing import List
from cooptools.geometry_utils import vector_utils as vec

class TreePhase(Enum):
    SEED = 0
    SAPLING = 1
    YOUTH = 2
    ADULT = 3
    ANCIENT = 4

class TreeType:
    OAK = 0
    WILLOW = 1
    MAPLE = 2
    BIRCH = 3


class Tree(GameObject):
    def __init__(self,
                 id,
                 pos: vec.FloatVec,
                 type: TreeType,
                 age: int = None,
                 tags: List[str] = None):
        super().__init__(name=id, pos=pos, tags=tags)
        self.id = id
        self.type = type
        self._age_phase = EnumToggleable(TreePhase, TreePhase.SEED)
        self._age = age if age else 0


