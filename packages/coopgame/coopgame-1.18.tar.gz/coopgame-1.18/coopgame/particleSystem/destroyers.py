from coopgame.particleSystem import Particle
from typing import Callable, Union
from dataclasses import dataclass

particle_destroyer = Callable[[Particle], bool]


@dataclass
class CompareArgs:
    lt: int = None
    gt: int = None
    le: int = None
    ge: int = None

    def compare(self, val):
        if self.lt is not None and val < self.lt:
            return True

        if self.gt is not None and val > self.gt:
            return True

        if self.le is not None and val <= self.le:
            return True

        if self.ge is not None and val >= self.ge:
            return True

        return False


def time_destroyer(particle: Particle, lifespan_ms: Union[int, Callable]) -> bool:
    if callable(lifespan_ms):
        lifespan_ms = lifespan_ms()

    return CompareArgs(gt=lifespan_ms).compare(particle.Lifetime_ms)

def size_destroyer(particle: Particle, compareArgs: CompareArgs):
    return compareArgs.compare(particle.Size)

def time_and_size_destroyer(particle: Particle,
                            lifespan_ms: Union[int, Callable],
                            size_compare_args: CompareArgs) -> bool:
    return time_destroyer(particle=particle, lifespan_ms=lifespan_ms) and \
           size_destroyer(particle=particle, compareArgs=size_compare_args)
