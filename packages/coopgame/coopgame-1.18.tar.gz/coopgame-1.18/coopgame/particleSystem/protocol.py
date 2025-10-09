from typing import Protocol
import pygame


class UpdateRenderableProtocol(Protocol):
    def update(self, delta_ms: int):
        pass

    def render(self, surf: pygame.Surface):
        pass

    def n_particles(self):
        pass
