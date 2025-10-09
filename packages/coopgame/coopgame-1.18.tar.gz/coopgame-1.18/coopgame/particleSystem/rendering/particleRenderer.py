from coopgame.particleSystem.rendering.colorBehaviors import ColorBehaviorProtocol
from dataclasses import dataclass
from cooptools.colors import Color
from typing import Union
from coopgame.particleSystem.particle import Particle
import pygame
from cooptools.coopEnum import CoopEnum, auto

class RenderShape(CoopEnum):
    CIRCLE = auto()

class LifetimeType(CoopEnum):
    PARTICLE = auto()
    EMITTER = auto()

@dataclass(frozen=True)
class ParticleRenderer:
    colorBehavior: Union[Color, ColorBehaviorProtocol]
    shape: RenderShape = RenderShape.CIRCLE
    reverse: bool = False
    lifetime_type: LifetimeType = LifetimeType.PARTICLE

    def resolve_color(self, lifetime_ms):
        if type(self.colorBehavior) == Color:
            return self.colorBehavior.value
        else:
            return self.colorBehavior.resolve_at_t(lifetime_ms)

    def render(self, surface: pygame.Surface, particle: Particle, emitter):
        if self.lifetime_type == LifetimeType.PARTICLE:
            _color = self.resolve_color(particle.Lifetime_ms)
        elif self.lifetime_type == LifetimeType.EMITTER:
            _color = self.resolve_color(emitter.LifetimeMS)
        else:
            raise NotImplementedError(f"lifetime type {self.lifetime_type} has not been implemented for rendering")

        if self.shape == RenderShape.CIRCLE:
            pygame.draw.circle(surface=surface,
                               color=_color,
                               center=particle.pos.as_tuple(),
                               radius=particle.Size)