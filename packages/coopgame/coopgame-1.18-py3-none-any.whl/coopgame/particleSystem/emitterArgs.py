from coopgame.particleSystem.destroyers import particle_destroyer
from coopgame.particleSystem.callables import vec2_callable, float_from_ms_callable
from coopstructs.geometry.vectors.vectorN import Vector2
from typing import List, Union
from coopgame.particleSystem.rendering.particleRenderer import ParticleRenderer
from coopgame.particleSystem.particleGenerationArgs import ParticleGenerationArgs
from dataclasses import dataclass
from functools import partial
from coopgame.particleSystem.destroyers import time_destroyer
from coopgame.particleSystem.rendering.particleRenderer import RenderShape
from cooptools.colors import Color

@dataclass(frozen=True)
class EmitterArgs:
    origin: Union[Vector2, vec2_callable]
    velocity: Union[Vector2, vec2_callable]
    destroyers: List[particle_destroyer]
    size: Union[float, float_from_ms_callable]
    renderer: ParticleRenderer
    accel: Union[Vector2, vec2_callable] = None
    particle_generation_args: ParticleGenerationArgs = None

    def __post_init__(self):
        if self.destroyers is None or len(self.destroyers) == 0:
            raise ValueError(f"At least one particle destroyer must be provided")

        if self.particle_generation_args is None:
            object.__setattr__(self, 'particle_generation_args', ParticleGenerationArgs())

        if self.renderer is None:
            object.__setattr__(self, 'renderer', ParticleRenderer(
            shape=RenderShape.CIRCLE,
            colorBehavior=Color.SNOW
        ))

    def resolve_origin(self):
        if callable(self.origin):
            _o = self.origin()
        else:
            _o = self.origin

        return _o

    def resolve_velocity(self):
        if callable(self.velocity):
            _v = self.velocity()
        else:
            _v = self.velocity

        return _v

    def resolve_size(self, x):
        if callable(self.size):
            _s = self.size(x)
        else:
            _s = self.size

        return _s

def emitter_args_factory(
        args: EmitterArgs = None,
        origin: Union[Vector2, vec2_callable] = None,
        velocity: Union[Vector2, vec2_callable] = None,
        destroyers: List[particle_destroyer] = None,
        size: Union[float, float_from_ms_callable] = None,
        renderer: ParticleRenderer = None,
        accel: Union[Vector2, vec2_callable] = None,
        particle_generation_args: ParticleGenerationArgs = None) -> EmitterArgs:

    origin = origin or (args.origin if args else None) or Vector2(0,0)
    velocity = velocity or (args.velocity if args else None) or Vector2(0,0)
    destroyers = destroyers or (args.destroyers if args else None) or [partial(time_destroyer, lifespan_ms=2500)]
    size = size or (args.size if args else None) or 5
    renderer = renderer or (args.renderer if args else None)
    accel = accel or (args.accel if args else None) or Vector2(0, 0)
    particle_generation_args = particle_generation_args or (args.particle_generation_args if args else None)

    return EmitterArgs(
        origin=origin,
        velocity=velocity,
        destroyers=destroyers,
        size=size,
        renderer=renderer,
        accel=accel,
        particle_generation_args=particle_generation_args
    )


