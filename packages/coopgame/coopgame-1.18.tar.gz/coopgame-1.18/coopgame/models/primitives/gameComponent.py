from abc import ABC, abstractmethod

class Component:
    def __init__(self):
        pass

    @abstractmethod
    def update(self, game_perf: int):
        pass