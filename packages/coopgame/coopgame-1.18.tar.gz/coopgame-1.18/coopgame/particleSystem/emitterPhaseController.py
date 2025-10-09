import pygame
from typing import List, Tuple, Callable, Any
from coopgame.particleSystem.particleGenerationArgs import PhaseArgs
from dataclasses import dataclass
from coopgame.particleSystem.protocol import UpdateRenderableProtocol
from coopgame.particleSystem.callables import UpdateRenderableProtocol_provider

class EmitterPhaseController:
    def __init__(self,
                 args: PhaseArgs,
                 context = None
                 ):
        self.args = args
        self.context = context


        self.phases = self.resolved_phases()
        self.phase_idx = None

    def resolved_phases(self):
        phases = []
        for idx, x in enumerate(self.args.phases):
            if idx==0:
                phases.append((x.resolve(None), x))
            else:
                phases.append((x.resolve(phases[-1][0]), x))

        return phases

    def update(self, delta_ms):
        epoch_start_phase = self.phase_idx

        if self.phase_idx is None:
            self.phase_idx = 0

        if self.phase_idx >= len(self.phases):
            return

        emitter, phase_args = self.phases[self.phase_idx]

        emitter.update(delta_ms)

        if phase_args.phase_end_trigger is not None and phase_args.phase_end_trigger(self.phases[self.phase_idx][0]):
            self.phase_idx += 1

        if self.phase_idx >= len(self.phases) and self.args.loop:
            self.phase_idx = 0

        #handle callbacks
        if epoch_start_phase is None:
            # play first start callback
            self.phases[self.phase_idx][1].phase_start_callback(self.phases[self.phase_idx][0])
        elif self.phase_idx != epoch_start_phase:
            # end last callback
            self.phases[epoch_start_phase][1].phase_end_callback(self.phases[epoch_start_phase][0])
            # start new callback
            if self.phase_idx < len(self.phases):
                self.phases[self.phase_idx][1].phase_start_callback(self.phases[self.phase_idx][0])


    def render(self, surf: pygame.Surface):
        if self.phase_idx < len(self.phases):
            emitter, _ = self.phases[self.phase_idx]
            emitter.render(surf)

    def n_particles(self):
        if self.phase_idx < len(self.phases):
            return self.phases[self.phase_idx][0].n_particles()
        else:
            return 0

    @property
    def N_Particles(self) -> int:
        return self.n_particles()

    @property
    def Expired(self) -> bool:
        return self.phase_idx > len(self.phases)