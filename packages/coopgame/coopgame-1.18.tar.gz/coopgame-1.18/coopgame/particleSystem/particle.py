from coopstructs.geometry.vectors.vectorN import Vector2
from coopgame.particleSystem.callables import float_from_ms_callable
from typing import Union, Tuple
from cooptools.colors import Color
import uuid
from coopgame.particleSystem.callables import vec2_callable

class Particle:

    def __init__(self,
                 pos: Vector2,
                 velo_u_s: Union[Vector2, vec2_callable],
                 accel_u_s2: Union[Vector2, vec2_callable],
                 size: Union[float, float_from_ms_callable],
                 context = None,
                 id = None):

        if pos is None:
            raise ValueError(f"Particle pos cannot be initiated as None")

        self.pos = pos
        self.velo_u_s = velo_u_s
        self.accel_u_s2 = accel_u_s2 or Vector2(0, 0)
        self._lifetime_ms = 0
        self._size: Union[float, float_from_ms_callable] = size

        self._size_resolved: float = None
        self._color_resolved: Tuple[int, int, int] = None

        self.update(0)
        self.context = context
        self.id = id or uuid.uuid4()

    def __hash__(self):
        return hash(self.id)

    def _resolve_size(self, size, lifetime_ms):
        if callable(size):
            return size(lifetime_ms)

        return size

    def _resolve_velo(self):
        if callable(self.velo_u_s):
            return self.velo_u_s()
        return self.velo_u_s

    def _resolve_accel(self):
        if callable(self.accel_u_s2):
            return self.accel_u_s2()
        return self.accel_u_s2

    def update(self, delta_time_ms: int):
        self._lifetime_ms += delta_time_ms
        self._size_resolved = self._resolve_size(self._size, self._lifetime_ms)

        self.pos += self._resolve_velo() * delta_time_ms / 1000
        self.velo_u_s += self._resolve_accel() * delta_time_ms / 1000

    @property
    def Lifetime_ms(self):
        return self._lifetime_ms

    @property
    def Size(self):
        return self._size_resolved

    @property
    def Color(self):
        return Color.closest_color(self._color_resolved)

    @property
    def Color_RGB(self):
        return self._color_resolved
