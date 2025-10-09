from cooptools.colors import Color
from typing import Protocol, Tuple, Union, List
from coopgame.particleSystem.callables import color_callable
import coopgame.particleSystem.utils as utils


def _interpolate_int(start, end, progress):
    return int(start + (end - start) * progress)

def _resolve_color(color: Union[Color, color_callable]):
    if callable(color):
        return color()
    else:
        return color

def interpolate_at_t(t: int,
                     start_color: Union[Color, color_callable],
                     end_color: Union[Color, color_callable],
                     lifespan_ms: int) -> Tuple[int, int, int]:
    progress = min(t / lifespan_ms, 1)

    start = _resolve_color(start_color)
    end = _resolve_color(end_color)

    r = _interpolate_int(start.value[0], end.value[0], progress)
    g = _interpolate_int(start.value[1], end.value[1], progress)
    b = _interpolate_int(start.value[2], end.value[2], progress)

    return r, g, b

class ColorBehaviorProtocol(Protocol):
    def resolve_at_t(self, t: int) -> Tuple[int, int, int]:
        pass


class PulseColorBehavior:
    def __init__(self,
                 colors: List[Color],
                 pulse_duration_ms: int,
                 ):
        self.colors = colors
        self.pulse_duration_ms = pulse_duration_ms

    def resolve_at_t(self, t: int) -> Tuple[int, int, int]:
        color_changes = t / self.pulse_duration_ms

        current_start_color_idx = int(color_changes) % len(self.colors)
        current_end_color_idx = current_start_color_idx + 1

        if current_end_color_idx >= len(self.colors):
            current_end_color_idx = 0

        return interpolate_at_t(int((color_changes - int(color_changes)) * 1000),
                                self.colors[current_start_color_idx],
                                self.colors[current_end_color_idx],
                                1000
        )

class InterpolateColorBehavior:
    def __init__(self, start_color: Union[Color, color_callable], end_color: Union[Color, color_callable], lifespan_ms: int):
        self.start = start_color
        self.end = end_color
        self.lifespan_ms = lifespan_ms

    def resolve_at_t(self, t: int) -> Tuple[int, int, int]:
        return interpolate_at_t(
            t=t,
            start_color=self.start,
            end_color=self.end,
            lifespan_ms=self.lifespan_ms
        )

