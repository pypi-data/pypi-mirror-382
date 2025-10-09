from coopstructs.geometry.vectors.vectorN import Vector2
import math
import random as rnd
from dataclasses import dataclass


def rotation(time_ms, r_high, r_wide, phase: int = 0) -> Vector2:
    return Vector2(((math.sin(time_ms + phase) + 1) * r_wide) / 2, ((math.cos(time_ms + phase) + 1) * r_high) / 2)

def rand_between_points(a: Vector2, b: Vector2) -> Vector2:
    return a.interpolate(b, rnd.random())

@dataclass(frozen=True)
class SinWaveArgs:
    amp: float = 1
    wavelength: float = 1
    phase: float = 0
    norm_positive: bool = False

def sin_wave(x: float, args: SinWaveArgs):
    sin_val = math.sin((x + args.phase) / args.wavelength)
    if args.norm_positive:
        sin_val = (1 + sin_val) / 2

    return sin_val * args.amp

def decay(x: float, lifespan_ms: float, max_size: float, end_size: float = 0):
    _r = 1 / lifespan_ms
    return end_size + (1 - _r * x) * (max_size - end_size)

def grow(x: float, lifespan_ms: float, max_size: float, start_size: float = 0):
    _r = 1 / lifespan_ms
    return start_size + (_r * x) * (max_size - start_size)

def pulse(x: float, lifespan_ms: float, max_size: float, min_size: float, period_ms: float):
    pass
