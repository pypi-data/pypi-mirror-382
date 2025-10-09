from coopgame.models.primitives.coopquaternion import CoopQuaternion
from typing import Tuple
import cooptools.geometry_utils.vector_utils as vec
from cooptools.common import rads_to_degrees, degree_to_rads
import cooptools.geometry_utils.circle_utils as circ

class Rotation:
    def __init__(self,
                 rads: Tuple[float, float, float] = None,
                 rotation_point: Tuple[float, float, float] = None
                 ):
        self._rotation_point = rotation_point if rotation_point else (0, 0, 0)
        self._rads = (0, 0, 0)
        self._quaternion = CoopQuaternion(axis=[0, 1, 0], angle=0)

        if rads is not None:
            self.update(rads=rads)


    @classmethod
    def from_rotation(cls, rotation):
        return Rotation(rads=rotation.Rads, rotation_point=rotation.RotationPoint)

    def __repr__(self):
        return str(self._rads)

    def update(self,
                rads: Tuple[float, float, float] = None,
                delta_rads: Tuple[float, float, float] = None,
                degrees: Tuple[float, float, float] = None,
                delta_degrees: Tuple[float, float, float] = None,
                rotation_point: Tuple[float, float, float] = None
                ):
        if rads is not None:
            self._rads = rads

        if delta_rads is not None:
            self._rads = tuple(map(lambda i, j: i + j, self._rads, delta_rads))

        # recursive call for degrees
        if degrees is not None or delta_degrees is not None:
            self.update(rads=tuple([degree_to_rads(x) for x in degrees]) if degrees else None,
                        delta_rads=tuple([degree_to_rads(x) for x in delta_degrees]) if delta_degrees else None)

        # set rotation point
        if rotation_point is not None:
            self._rotation_point = rotation_point


    @property
    def RotationPoint(self):
        return self._rotation_point

    @property
    def Rads(self):
        return self._rads

    @property
    def Degrees(self):
        return tuple(rads_to_degrees(x) for x in self._rads)

class Translation:
    def __init__(self,
                 translation_vector: Tuple[float, float, float] = None):
        self._translation_vector = (0, 0, 0)

        if translation_vector is not None:
            self.update(vector=translation_vector)

    def from_translation(self, translation):
        return Translation(translation_vector=translation.Vector)

    def __repr__(self):
        return str(self._translation_vector)

    def update(self,
               vector: Tuple[float, ...] = None,
               delta_vector: Tuple[float, ...] = None):
        if vector is not None:
            self._translation_vector = vector

        if delta_vector is not None:
            self._translation_vector = vec.add_vectors([self._translation_vector, delta_vector], allow_diff_lengths=True)

    @property
    def Vector(self):
        return self._translation_vector

class Scale:
    def __init__(self,
                 scale_vector: Tuple[float, float, float] = None,
                 scale_point: Tuple[float, float, float] = None,
                 ):
        self._scale_vector = scale_vector if scale_vector else (1, 1, 1)
        self._scale_point = scale_point if scale_point else (0, 0, 0)
        self._scale_adjustment = (0, 0, 0)

    def from_scale(self, scale):
        return Scale(
            scale_vector=scale.Vector,
            scale_point=scale.ScalePoint
        )

    def __repr__(self):
        return str(self._scale_vector)

    def update(self,
               scale_vector: Tuple[float, ...],
               scale_point: Tuple[float, ...] = None):
        adj_scale_point = vec.hadamard_product(scale_point, scale_vector) if scale_point else (0, 0, 0)
        self._scale_adjustment = vec.add_vectors(
            [vec.hadamard_product(self._scale_adjustment, scale_vector, allow_different_lengths=True), adj_scale_point,
             tuple(-1 * x for x in adj_scale_point)])
        self._scale_vector = vec.hadamard_product(self._scale_vector, scale_vector, allow_different_lengths=True)

    @property
    def ScaleAdjustment(self):
        return self._scale_adjustment


    @property
    def ScalePoint(self):
        return self._scale_point


    @property
    def Vector(self):
        return self._scale_vector


class Transform:
    def __init__(self, translation: vec.FloatVec = None,
                 rotation: vec.FloatVec = None ,
                 scale: vec.FloatVec = None):
        self._translation: Translation = Translation(translation_vector=translation)
        self._rotation: Rotation = Rotation(rads=rotation)
        self._scale: Scale = Scale(scale_vector=scale)

    @classmethod
    def from_transform(cls, transform):
        return Transform(
            translation=transform.Translation.Vector,
            scale=transform.Scale.Vector,
            rotation=transform.Rotation.Rads
        )


    @property
    def Translation(self):
        return self._translation

    @property
    def Rotation(self):
        return self._rotation

    @property
    def Scale(self):
        return self._scale

    def __repr__(self):
        return f"T{self.Translation}, R{self.Rotation}, S{self.Scale}"
