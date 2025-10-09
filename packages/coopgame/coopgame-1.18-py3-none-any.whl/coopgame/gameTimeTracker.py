import time
import coopgame.pygamehelpers as help
import pygame


class GameTimeTracker:
    def __init__(self, max_fps):
        self.ticks = 0
        self.frames = 0
        self.frame_times = []
        self.fps = None
        self.max_fps = max_fps

        self.clock = pygame.time.Clock()
        self.game_start = None

    def recalculate_fps(self, ticks_last_frame: int):
        if len(self.frame_times) > 20:
            self.frame_times.pop(0)

        self.frame_times.append(ticks_last_frame)

        self.fps = help.calculate_fps(self.frame_times)
        return self.fps

    def set_start(self):
        self.game_start = time.perf_counter()

    @property
    def run_time(self):
        return (time.perf_counter() - self.game_start) if self.game_start else None

    def update(self, time_multiplier: int|float = 1.0) -> int:
        t = pygame.time.get_ticks()
        delta_time_ms = (t - self.ticks) * (time_multiplier * 1.0)
        self.ticks = t
        self.recalculate_fps(delta_time_ms)
        self.frames += 1
        self.clock.tick(self.max_fps)

        return delta_time_ms
