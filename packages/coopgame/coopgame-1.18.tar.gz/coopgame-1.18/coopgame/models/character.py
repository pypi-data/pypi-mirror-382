from coopmovers.segmentfollower import SegmentFollower
from coopstructs.vectors import Vector2
from typing import List
import time
from coopgame.models.status import Status
from coopgame.models.primitives.gameObject import GameObject
from coopgame.models.primitives.health import Health

class Character(GameObject):
    def __init__(self,
                 name,
                 pos,
                 health: Health = None,
                 tags: List[str] = None,
                 max_speed_meters_per_sec: int = 10,
                 max_accel_meters_per_sec: int = 10, initial_velocity: Vector2 = None,
                 statuss: List[Status] = None):
        super().__init__(name=name, pos=pos, tags=tags)
        self.segment_follower = SegmentFollower(name=name
                                                 , start_pos=pos
                                                 , max_speed_meters_per_sec=max_speed_meters_per_sec
                                                 , max_accel_meters_per_sec=max_accel_meters_per_sec
                                                 , initial_velocity=initial_velocity)
        self._health = health
        self._statuss: List[Status] = statuss if statuss else []
        self.name = name

    @property
    def status(self):
        return self._statuss

