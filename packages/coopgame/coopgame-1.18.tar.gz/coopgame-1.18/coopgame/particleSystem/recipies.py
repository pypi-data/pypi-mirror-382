from coopgame.particleSystem.emitter import Emitter
from coopgame.particleSystem.destroyers import time_destroyer, time_and_size_destroyer, CompareArgs
from coopstructs.geometry.vectors.vectorN import Vector2
from functools import partial
from typing import Union, Callable, Tuple
import coopgame.particleSystem.utils as utils
from coopgame.particleSystem.callables import vec2_callable, int_callable, float_callable, phase_callback
import random as rnd
from coopgame.particleSystem.rendering.particleRenderer import ParticleRenderer
from coopgame.particleSystem.emitterComposite import EmitterComposite
from coopgame.particleSystem.particleGenerationArgs import ParticleGenerationArgs, BurstArgs, PhaseArgs
from coopgame.particleSystem.emitterArgs import EmitterArgs
from coopgame.particleSystem.protocol import UpdateRenderableProtocol
from coopgame.particleSystem.emitterPhaseController import EmitterPhaseController
from coopgame.particleSystem.particleGenerationArgs import EmitterPhase


def snow(origin_line_start: Vector2,
         origin_line_end: Vector2,
         fall_velo: Vector2,
         lifespan_ms: Union[int, Callable],
         size: float,
         renderer: ParticleRenderer,
         twinkle_ms: float,
         particle_generation_args: ParticleGenerationArgs = None) -> UpdateRenderableProtocol:
    from_top_origin = lambda: utils.rand_between_points(origin_line_start, origin_line_end)
    return Emitter(EmitterArgs(
        origin=from_top_origin,
        velocity=fall_velo,
        destroyers=[partial(time_destroyer, lifespan_ms=lifespan_ms)],
        size=lambda x: max(utils.sin_wave(x, utils.SinWaveArgs(amp=size, wavelength=twinkle_ms, norm_positive=True)), 1),
        renderer=renderer,
        particle_generation_args=particle_generation_args),
        id='snow'
    )

def comet(path: vec2_callable,
          radiate_speed: int,
          lifespan_ms: int,
          start_size: float,
          renderer: ParticleRenderer,
          particle_generation_args: ParticleGenerationArgs = None) -> UpdateRenderableProtocol:
    radiate_velo = lambda: Vector2(rnd.random() * 2 - 1, rnd.random() * 2 - 1) * radiate_speed

    return Emitter(EmitterArgs(
        origin=path,
        velocity=radiate_velo,
        destroyers=[partial(time_destroyer, lifespan_ms=lifespan_ms)],
        size=lambda x: utils.decay(x, lifespan_ms=lifespan_ms, max_size=start_size),
        renderer=renderer,
        particle_generation_args=particle_generation_args),
        id='comet'
    )


def torch(origin: Union[Vector2, vec2_callable],
          fire_lifespan_ms: int,
          smoke_lifespan_ms: int,
          fire_start_size: float,
          smoke_end_size: float,
          fire_raise_velo: Union[Vector2, vec2_callable],
          smoke_raise_velo: Union[Vector2, vec2_callable],
          fire_renderer: ParticleRenderer,
          smoke_renderer: ParticleRenderer,
          fire_generation_args: ParticleGenerationArgs = None,
          smoke_generation_args: ParticleGenerationArgs = None) -> UpdateRenderableProtocol:

    if fire_generation_args is None:
        fire_generation_args = ParticleGenerationArgs(generation_interval_ms=10)
    if smoke_generation_args is None:
        smoke_generation_args = ParticleGenerationArgs(generation_interval_ms=500)

    if not callable(origin):
        origin = lambda: origin

    # if not callable(smoke_raise_velo):
    #     smoke_raise_velo = lambda: smoke_raise_velo
    #
    # if not callable(fire_raise_velo):
    #     fire_raise_velo = lambda : fire_raise_velo

    smoke = Emitter(EmitterArgs(
        origin=lambda: origin() + Vector2((rnd.random() * 2 - 1) * 1, -75),
        velocity=smoke_raise_velo,
        destroyers=[partial(time_destroyer, lifespan_ms=smoke_lifespan_ms)],
        size=lambda x: utils.grow(x, lifespan_ms=smoke_lifespan_ms, max_size=smoke_end_size, start_size=smoke_end_size/4),
        particle_generation_args=smoke_generation_args,
        renderer=smoke_renderer
        ),
        id='torch_smoke'
    )


    flame = Emitter(EmitterArgs(
        origin=lambda: origin() + Vector2((rnd.random() * 2 - 1) * 5, 0),
        velocity=fire_raise_velo,
        destroyers=[partial(time_destroyer, lifespan_ms=fire_lifespan_ms)],
        size=lambda x: utils.decay(x, lifespan_ms=fire_lifespan_ms, max_size=fire_start_size),
        particle_generation_args=fire_generation_args,
        renderer=fire_renderer
       ),
        id='torch_flame'
    )

    torch = EmitterComposite(
        emitters={
            0: smoke,
            1: flame
        }

    )

    return torch


def twinkle_stars(star_gen_args: ParticleGenerationArgs,
                  width_bounds: Tuple[int, int],
                  height_bounds: Tuple[int, int],
                  star_size: int,
                  twinkle_time_ms: Union[int, Callable[[], int]],
                  renderer: ParticleRenderer
                  ):

    origin = lambda: Vector2.from_tuple((rnd.randint(*width_bounds), rnd.randint(*height_bounds)))

    return Emitter(EmitterArgs(
        origin=origin,
        velocity=Vector2(0, 0),
        destroyers=[partial(time_and_size_destroyer, lifespan_ms=twinkle_time_ms, size_compare_args=CompareArgs(le=0))],
        size=lambda x: utils.sin_wave(x + rnd.random(), utils.SinWaveArgs(amp=star_size,wavelength=twinkle_time_ms)),
        particle_generation_args=star_gen_args,
        renderer=renderer
        ),
        id='stars'
    )


def fountain(origin: Vector2,
             spray_intensity: float,
             spray_arc: Tuple[int, int],
             fountain_lifespan_ms: int,
             drop_accel: Vector2,
             droplet_size_start: int,
             droplet_size_end: int,
             droplet_renderer: ParticleRenderer,
             droplet_generation_args: ParticleGenerationArgs = None
             ) -> UpdateRenderableProtocol:

    if droplet_generation_args is None:
        droplet_generation_args = ParticleGenerationArgs(generation_interval_ms=50)

    spray_dir_lam = lambda: Vector2.point_on_circle(rnd.randint(spray_arc[0], spray_arc[1]), center=(0, 0)) * - spray_intensity

    return Emitter(EmitterArgs(
        origin=lambda: origin,
        velocity=spray_dir_lam,
        destroyers=[partial(time_destroyer, lifespan_ms=fountain_lifespan_ms)],
        size=lambda x: utils.decay(x, lifespan_ms=fountain_lifespan_ms, max_size=droplet_size_start, end_size=droplet_size_end),
        particle_generation_args=droplet_generation_args,
        renderer=droplet_renderer,
        accel=drop_accel
        ),
        id='fountain'
    )

def firework(origin: Union[Vector2, vec2_callable],
             launch_speed: Union[float, float_callable],
             spread: Union[float, float_callable],
             lifespan_ms: int,
             drop_accel: Vector2,
             size_start: int,
             size_end: int,
             arms: Union[int, int_callable],
             burst_interval_ms: Union[int, int_callable],
             explosion_renderer: ParticleRenderer,
             launch_renderer: ParticleRenderer,
             spread_arc: Tuple[int, int] = None,
             max_fireworks: int = None,
             launch_start_callback: phase_callback = None,
             launch_end_callback: phase_callback = None,
             explosion_start_callback: phase_callback = None,
             explosion_end_callback: phase_callback = None
             ) -> UpdateRenderableProtocol:

    if callable(spread):
        spread = spread()

    if callable(launch_speed):
        launch_speed = launch_speed()

    spread_arc_lam = lambda min, max: (rnd.randint(min, max), rnd.randint(min, max))
    spray_dir_lam = lambda min, max, speed: Vector2.point_on_circle(rnd.randint(*sorted(spread_arc_lam(min, max))),
                                                    center=(0, 0)) * - launch_speed


    launch_lam = lambda x: Emitter(EmitterArgs(
        origin=origin,
        velocity=lambda: spray_dir_lam(60, 120, launch_speed),
        accel=Vector2(0, 100),
        destroyers=[lambda part: part.velo_u_s.y > 0],
        size=3,
        renderer=launch_renderer,
        particle_generation_args=ParticleGenerationArgs(generation_interval_ms=75, max_particles=1)),
        id='firework_launch',
        trail_args=EmitterArgs(
            origin=Vector2(0, 0),
            velocity=Vector2(0, 0),
            destroyers=[partial(time_destroyer, lifespan_ms=300)],
            size=1,
            renderer=launch_renderer,
            particle_generation_args=ParticleGenerationArgs(generation_interval_ms=75)
        )
    )

    explosion_generation_args = ParticleGenerationArgs(
        generation_interval_ms=50,
        burst_args=BurstArgs(
            burst_interval_ms=burst_interval_ms,
            particles_per_burst=arms,
            max_bursts=1
        )
    )


    explosion_lam = lambda x: Emitter(EmitterArgs(
        origin=lambda: x.LastPos,
        velocity=lambda: spray_dir_lam(0, 360, spread),
        destroyers=[partial(time_destroyer, lifespan_ms=lifespan_ms)],
        size=lambda x: utils.decay(x, lifespan_ms=lifespan_ms, max_size=size_start, end_size=size_end),
        particle_generation_args=explosion_generation_args,
        renderer=explosion_renderer,
        accel=drop_accel
        ),
        trail_args=EmitterArgs(
            origin=Vector2(0, 0),
            velocity=Vector2(0, 0),
            destroyers=[partial(time_destroyer, lifespan_ms=300)],
            size=1,
            renderer=explosion_renderer,
            particle_generation_args=ParticleGenerationArgs(generation_interval_ms=75)
        ),
        id='firework_explosion'
    )

    return Emitter(
        EmitterArgs(
            origin=origin,
            velocity=Vector2(0, 0),
            particle_generation_args=ParticleGenerationArgs(
                phase_args=PhaseArgs(
                    phases=[
                        EmitterPhase(emitter_provider=launch_lam,
                                     phase_end_trigger=lambda me: len(me.Particles) == 0 and me.LifetimeMS > 100,
                                     phase_start_callback=launch_start_callback,
                                     phase_end_callback=launch_end_callback), #lambda x: x.LifetimeMS > rnd.randint(1000, 2500)
                        EmitterPhase(emitter_provider=explosion_lam,
                                     phase_end_trigger=lambda me: me.LifetimeMS > lifespan_ms,
                                     phase_start_callback=explosion_start_callback,
                                     phase_end_callback=explosion_end_callback)
                    ],
                    max_phasers=max_fireworks
                ),
                generation_interval_ms=burst_interval_ms
            ),
            destroyers=[partial(time_destroyer, lifespan_ms=5000)],
            renderer=explosion_renderer,
            size=1
        ),
        id='fireworks',
        context='fireworks'
    )