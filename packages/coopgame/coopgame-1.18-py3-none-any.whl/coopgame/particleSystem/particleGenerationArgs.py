from dataclasses import dataclass
from coopgame.particleSystem.callables import int_callable, UpdateRenderableProtocol_provider, phase_callback
from typing import Union
from coopgame.particleSystem.protocol import UpdateRenderableProtocol
from typing import List, Tuple, Callable, Optional

@dataclass(frozen=True)
class BurstArgs:
    burst_interval_ms: Union[int, int_callable]
    particles_per_burst: Union[int, int_callable]
    max_bursts: Union[int, int_callable] = None

    @property
    def BurstIntervalMS(self):
        if callable(self.burst_interval_ms):
            return self.burst_interval_ms()
        return self.burst_interval_ms

    @property
    def MaxBursts(self):
        if callable(self.max_bursts):
            return self.max_bursts()
        return self.max_bursts

    @property
    def ParticlesPerBurst(self):
        if callable(self.particles_per_burst):
            return self.particles_per_burst()
        return self.particles_per_burst

phase_end_trigger = Callable[[UpdateRenderableProtocol], bool]


@dataclass(frozen=True)
class EmitterPhase:
    emitter_provider: UpdateRenderableProtocol_provider
    phase_end_trigger: phase_end_trigger
    phase_end_callback: phase_callback = None
    phase_start_callback: phase_callback = None

    def resolve(self, previous_phase: UpdateRenderableProtocol = None) -> UpdateRenderableProtocol:
        return self.emitter_provider(previous_phase)

@dataclass(frozen=True)
class PhaseArgs:
    phases: List[EmitterPhase]
    loop: bool = False
    max_phasers: int = None

@dataclass(frozen=True)
class ParticleGenerationArgs:
    generation_interval_ms: Union[int, int_callable] = 20
    burst_args: BurstArgs = None
    phase_args: PhaseArgs = None
    max_particles: Union[int, int_callable] = None
    init_particles: int = None

    @property
    def GenerationIntervalMS(self):
        if callable(self.generation_interval_ms):
            return self.generation_interval_ms()
        return self.generation_interval_ms

    @property
    def MaxParticles(self):
        if callable(self.max_particles):
            return self.max_particles()
        return self.max_particles



