from typing import List
from coopstructs.vectors import Vector2

class GameObject:

    def __init__(self,
                 name: str,
                 pos: Vector2,
                 tags: List[str] = None):
        self.tags = tags if tags else []
        self.name = name
        self.pos = pos

    def is_tagged(self, tags: List[str]):
        return set(tags).issubset(self.tags)

