from typing import Protocol

class GameModelProtocol(Protocol):
    def update(self, delta_time_ms: int):
        pass
