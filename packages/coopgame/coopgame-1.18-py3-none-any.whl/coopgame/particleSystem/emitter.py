import pygame

from coopgame.particleSystem.particle import Particle
from coopstructs.geometry.vectors.vectorN import Vector2
from typing import List, Dict
from coopgame.particleSystem.emitterArgs import EmitterArgs, emitter_args_factory
import uuid
from cooptools.toggles import BooleanToggleable
from coopgame.particleSystem.emitterPhaseController import EmitterPhaseController

class Emitter:

    def __init__(self,
                 args: EmitterArgs,
                 trail_args: EmitterArgs = None,
                 id = None,
                 context = None,
                 start_on_init: bool = True
                 ):

        self.particles: List[Particle] = []
        self.args = args
        self.trail_args = trail_args

        self.trails: Dict[Particle, Emitter] = {}

        self._last_creation = 0
        self._next_burst = 0
        self._now = 0
        self._n = 0
        self._n_bursts = 0

        self._lifetime_ms = 0

        self._started = BooleanToggleable(default=start_on_init)
        self.id = id or uuid.uuid4()
        self.context = context

        self._phase_controllers: List[EmitterPhaseController] = []
        self._n_phasers = 0
        self._next_phaser = 0

        self._last_pos = None

        if self.args.particle_generation_args.init_particles is not None:
            self.add_new_particles(self.args.particle_generation_args.init_particles)

    def _update_particles(self, delta_ms):
        to_remove = []
        for particle in self.particles:
            # update the particle
            particle.update(delta_ms)

            # check if particle needs destroyed
            if any(x(particle) for x in self.args.destroyers):
                to_remove.append(particle)

        # remove the particles need to be removed
        for particle in to_remove:
            self.particles.remove(particle)

    def _update_trails(self, delta_ms):
        for part, trail in self.trails.items():
            trail.update(delta_ms)

        # remove empty trails
        trails_to_remove = []
        for part, trail in self.trails.items():
            if part not in self.particles and trail.Running:
                trail.toggle_started(False)

            if part not in self.particles and trail.N_Particles == 0:
                trails_to_remove.append(part)


        for part in trails_to_remove:
            del self.trails[part]

    def _update_phases(self, delta_ms):
        to_remove = []
        for phase_controller in self._phase_controllers:
            phase_controller.update(delta_ms)
            if phase_controller.Expired:
                to_remove.append(phase_controller)

        for phase_controller in to_remove:
            self._phase_controllers.remove(phase_controller)

    def toggle_started(self, value: bool = None):
        if value:
            self._started.set_value(value)
        else:
            self._started.toggle()

    def emit(self):
        # dont handle bc passed max particles
        if self.args.particle_generation_args.MaxParticles is not None and self._n >= self.args.particle_generation_args.MaxParticles:
            return

        if self.args.particle_generation_args.burst_args is not None:
            self.handle_bursts()
        elif self.args.particle_generation_args.phase_args is not None:
            self.handle_phases()
        else:
            self.handle_stream()


    def update(self, delta_ms: int):
        self._now += delta_ms
        self._lifetime_ms += delta_ms

        if self._started.value:
            self.emit()
        else:
            self._last_creation = self._now

        # update particles
        self._update_particles(delta_ms)

        # update trails
        self._update_trails(delta_ms)

        # update phases
        self._update_phases(delta_ms)

        # store last pos
        if len(self.Particles) > 0:
            self._last_pos = self.Particles[-1].pos

    def create_trail(self, particle: Particle):
        trail = Emitter(emitter_args_factory(args=self.trail_args, origin=lambda: particle.pos), id='tail')
        self.trails[particle] = trail

    def add_new_particles(self, n_to_create, origin: Vector2 = None):
        for n in range(n_to_create):
            if origin is not None:
                _o = origin
            else:
                _o = self.args.resolve_origin()

            # create particle
            if self.args.particle_generation_args.MaxParticles is not None and self._n >= self.args.particle_generation_args.MaxParticles:
                return

            new_part = Particle(
                pos=_o,
                velo_u_s=self.args.resolve_velocity(),
                accel_u_s2=self.args.accel,
                size=self.args.resolve_size(self._lifetime_ms),
                id=f"{self.context}_{self._n}" if self.context else None
            )
            self.particles.append(new_part)

            # create a trail for the particle
            if self.trail_args:
                self.create_trail(new_part)

            self._n += 1
            self._last_creation = self._now

    def handle_phases(self):
        # dont hanlde bc passed max phasers
        if self.args.particle_generation_args.phase_args.max_phasers is not None and self._n_phasers >= self.args.particle_generation_args.phase_args.max_phasers:
            return

        # dont handle bc invterval hasnt passed
        if self._now < self._next_phaser:
            return

        # determine next phaser
        self._next_phaser = self.args.particle_generation_args.GenerationIntervalMS + self._now

        self._n_phasers += 1
        self._phase_controllers.append(EmitterPhaseController(
            self.args.particle_generation_args.phase_args
        ))


    def handle_bursts(self):
        # dont hanlde bc passed max bursts
        if self.args.particle_generation_args.burst_args.MaxBursts is not None and self._n_bursts >= self.args.particle_generation_args.burst_args.MaxBursts:
            return

        # dont handle bc invterval hasnt passed
        if self._now < self._next_burst:
            return

        self._next_burst = self.args.particle_generation_args.burst_args.BurstIntervalMS + self._now

        # determine n to create
        n_to_burst = self.args.particle_generation_args.burst_args.ParticlesPerBurst

        # add new
        self._n_bursts += 1
        self.add_new_particles(n_to_burst, origin=self.args.resolve_origin())

    def handle_stream(self):
        # dont handle bc invterval hasnt passed
        if self._now - self._last_creation < self.args.particle_generation_args.GenerationIntervalMS:
            return

        # determine n to create
        n_to_create = int((self._now - self._last_creation) / self.args.particle_generation_args.GenerationIntervalMS)

        # add new
        self.add_new_particles(n_to_create)


    def render(self, surf: pygame.Surface):
        # render my particles
        if self.args.renderer.reverse:
            for particle in reversed(self.particles):
                self.args.renderer.render(surf, particle, self)
        else:
            for particle in self.particles:
                self.args.renderer.render(surf, particle, self)

        # render my trails
        for part, trail in self.trails.items():
            trail.render(surf)

        # render phases
        for phaser in self._phase_controllers:
            phaser.render(surf)

    def n_particles(self):
        return len(self.particles) + \
               sum(trail.N_Particles for _, trail in self.trails.items()) + \
               sum(phaser.N_Particles for phaser in self._phase_controllers)

    @property
    def N_Particles(self):
        return self.n_particles()

    @property
    def Running(self):
        return self._started.value

    @property
    def Particles(self):
        return self.particles

    @property
    def LifetimeMS(self):
        return self._lifetime_ms

    @property
    def LastPos(self):
        return self._last_pos