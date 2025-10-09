from typing import Protocol, Iterable, Self, Dict
from coopstructs.geometry import Rectangle
from cooptools.protocols import UniqueIdentifier
from cooptools.geometry_utils import vector_utils as vec
from cooptools.geometry_utils import polygon_utils as ply


class CollisionProtocol(Protocol):
    def check_collides(self, colliders: Dict[UniqueIdentifier, Self]) -> Dict[UniqueIdentifier, bool]:
        pass


class TwoDimensionConvexPolyCollider:
    def __init__(self,
                 poly: vec.IterVec):
        self.poly = poly

    def check_collides(self, colliders: Dict[UniqueIdentifier, Self]) -> Dict[UniqueIdentifier, bool]:
        ret = {}
        for id, collider in colliders:
            ret[id] = ply.do_convex_polygons_intersect(self.poly, collider.poly)
        return ret

if __name__ == "__main__":
    import math
    def test_01():
        c1 = TwoDimensionConvexPolyCollider(poly =Rectangle.from_meta(0, 0, 100, 200, math.pi/4).Corners)
        c2 = TwoDimensionConvexPolyCollider(poly =Rectangle.from_meta(0, 0, 100, 200, math.pi/4).Corners)