from coopstructs.geometry.vectors.vectorN import Vector2
from typing import Callable, Any, Optional
from cooptools.colors import Color
from coopgame.particleSystem.protocol import UpdateRenderableProtocol

vec2_callable = Callable[[], Vector2]
float_from_ms_callable = Callable[[int], float]
color_from_ms_callable = Callable[[int], Color]
color_callable = Callable[[], Color]
int_callable = Callable[[], int]
float_callable = Callable[[], float]
UpdateRenderableProtocol_provider = Callable[[Optional[UpdateRenderableProtocol]], UpdateRenderableProtocol]
phase_end_trigger = Callable[[], bool]
phase_callback = Callable[[UpdateRenderableProtocol], Any]