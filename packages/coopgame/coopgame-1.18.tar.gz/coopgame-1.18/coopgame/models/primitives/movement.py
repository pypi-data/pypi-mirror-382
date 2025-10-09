import time
from typing import Tuple, Optional
import cooptools.geometry_utils.vector_utils as vec


def accrued_s(delta_time_ms: int,
              time_scale_seconds_per_second: int = 1) -> float:
    return delta_time_ms / 1000.0 * time_scale_seconds_per_second

def updated_velo(velocity: vec.FloatVec,
                 accel: vec.FloatVec,
                 delta_time_ms: int,
                 time_scale_seconds_per_second: int = 1,
                 ) -> vec.FloatVec:
    ''' Calculate the amount of accrued velocity in delta time and apply to position'''
    accrued_sec = accrued_s(delta_time_ms=delta_time_ms, time_scale_seconds_per_second=time_scale_seconds_per_second)
    accrued_accel = vec.scale_vector_length(accel, accrued_sec)
    return vec.add_vectors([velocity, accrued_accel])


class TimeTracker:
    def __init__(self):
        self._first = time.perf_counter()
        self._now = self._first
        self._last = self._first
        self._delta = None
        self._n_updates = 0

    def update(self, perf: int = None):
        self._last = self._now
        self._n_updates += 1
        self._now = perf if perf else time.perf_counter()
        self._delta = self._now - self._last

    def adjusted_delta_ms(self, time_scale_seconds_per_second: int = 1):
        return self.Delta_S * time_scale_seconds_per_second * 1000

    def accrued_s(self, time_scale_seconds_per_second: int = 1):
        return self.Duration_S * time_scale_seconds_per_second * 1000

    @property
    def Now(self):
        return self._now

    @property
    def Last(self):
        return self._last

    @property
    def Duration_S(self):
        return self._now - self._first

    @property
    def Delta_S(self):
        return self._delta

    @property
    def Delta_MS(self):
        return self.Delta_S * 1000

    @property
    def Avg_Update_MS(self):
        return (self._now - self._first) / self._n_updates * 1000

class Velocity:
    def __init__(self,
                 initial_m_s_vec: vec.FloatVec,
                 max_m_s: float = None,
                 ):
        self._max_m_per_s = max_m_s
        self._current_m_s_vec = initial_m_s_vec

    def set(self,
            m_s_vec: vec.FloatVec = None,
            delta_m_s_vec: vec.FloatVec = None):
        if m_s_vec is not None:
            self._current_m_s_vec = m_s_vec

        if delta_m_s_vec is not None:
            self._current_m_s_vec = vec.add_vectors([self._current_m_s_vec, delta_m_s_vec])

        self._verify()

    @staticmethod
    def _time_scale_of_vector(vector: vec.FloatVec, delta_time_ms: int, time_scale_seconds_per_second: float):
        return vec.scale_vector_length(vector, delta_time_ms / 1000.0 * time_scale_seconds_per_second)

    def _verify(self):
        if self._max_m_per_s is not None and vec.vector_len(self._current_m_s_vec) > self._max_m_per_s:
            self._current_m_s_vec = vec.scaled_to_length(self._current_m_s_vec, self._max_m_per_s)

    def update(self,
               delta_time_ms: int,
               accel: vec.FloatVec = None
               ) -> Optional[vec.FloatVec]:

        if delta_time_ms is None or delta_time_ms <= 0:
            return None

        ''' Accrued velo'''
        accrued_velo = vec.scale_vector_length(self._current_m_s_vec, delta_time_ms / 1000)

        ''' Update the velo'''
        self.set(delta_m_s_vec=accel)

        return accrued_velo

    @property
    def CurrentVelocity_M_S(self) -> vec.FloatVec:
        return self._current_m_s_vec

    def __repr__(self):
        return str(self.CurrentVelocity_M_S)

class Acceleration:
    def __init__(self,
                 initial_m_s2_vec: vec.FloatVec,
                 max_m_s2: float = None,
                 ):
        self._max_m_s2 = max_m_s2
        self._current_m_s2_vec = initial_m_s2_vec

    def set(self,
            m_s2_vec:  vec.FloatVec = None,
            delta_m_s2_vec: vec.FloatVec = None):
        if m_s2_vec is not None:
            self._current_m_s2_vec = m_s2_vec

        if delta_m_s2_vec is not None:
            self._current_m_s2_vec = vec.add_vectors([self._current_m_s2_vec, delta_m_s2_vec])

        self._verify()

    @staticmethod
    def _time_scale_of_vector(vector: vec.FloatVec, delta_time_ms: int, time_scale_seconds_per_second: float):
        return vec.scale_vector_length(vector, delta_time_ms / 1000.0 * time_scale_seconds_per_second)

    def _verify(self):
        if self._max_m_s2 is not None and vec.vector_len(self._current_m_s2_vec) > self._max_m_s2:
            self._current_m_s2_vec = vec.scaled_to_length(self._current_m_s2_vec, self._max_m_s2)

    def update(self,
               delta_time_ms: int
               ) -> Optional[vec.FloatVec]:

        if delta_time_ms is None or delta_time_ms <= 0:
            return None

        return vec.scale_vector_length(self._current_m_s2_vec, delta_time_ms / 1000)

    @property
    def CurrentAccel_M_S(self):
        return self._current_m_s2_vec

    def __repr__(self):
        return str(self.CurrentAccel_M_S)

if __name__ =="__main__":
    v = Velocity((0, 0))
    a = Acceleration((0, 0))
    tt = TimeTracker()

    while True:
        tt.update()
        if tt.Duration_S > 5:
            a.set(m_s2_vec=(1, 1))
        if tt.Duration_S > 10:
            a.set(m_s2_vec=(0, 0))

        accel = a.update(tt.Delta_MS)
        v.update(delta_time_ms=tt.Delta_MS, accel=accel)
        print(v)
        time.sleep(0.5)

