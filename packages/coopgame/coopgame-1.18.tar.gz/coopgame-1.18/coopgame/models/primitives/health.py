import time

class Health:

    def __init__(self,
                 max_health: float,
                 current_health: float = None):
        self._max_health = max_health
        self._current_health = current_health if current_health is not None else self._max_health
        self._death_timer = None

    def change_max_health(self, delta):
        self._max_health += delta

    def change_current_health(self, delta, game_perf: int = None):
        if self._current_health + delta <= 0:
            self._current_health = 0
            self._death_timer = time.perf_counter() if game_perf is None else game_perf
        elif self._current_health + delta > self._max_health:
            self._current_health = self._max_health
        else:
            self._current_health += delta

        return self._current_health

    def set_full(self):
        self._current_health = self._max_health

    @property
    def Alive(self):
        return self._current_health > 0

    @property
    def Remaining(self):
        return self._current_health

    @property
    def Max(self):
        return self._max_health

    @property
    def LastDeathTime(self):
        return self._death_timer