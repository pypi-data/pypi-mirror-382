import pygame

from coopgame.particleSystem.emitter import Emitter
from typing import Dict

class EmitterComposite:

    def __init__(self, emitters: Dict[int, Emitter]):
        self._emitters = emitters

    def update(self, delta_ms: int):
        for component in self.Components:
            component.update(delta_ms)

    def render(self, surface: pygame.Surface):
        for component in sorted(self._emitters.values(), key=lambda x: self._emitters.keys()):
            component.render(surface)

    def n_particles(self):
        return sum(x.N_Particles for x in self._emitters.values())

    def toggle(self, value: bool):
        for x in self._emitters.values():
            x.toggle_started(value=value)

    @property
    def Components(self):
        return list(self._emitters.values())

    @property
    def N_Particles(self):
        return self.n_particles()