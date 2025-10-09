from coopstructs.geometry.vectors.vectorN import Vector3
from coopgame.models.primitives.coopquaternion import CoopQuaternion

class ObjectOrientationArgs:
    def __init__(self,
                 translation_vector: Vector3 = None,
                 rotation_point: Vector3 = None,
                 rotation_axis: Vector3 = None,
                 rotation_rads: float = None,
                 scale_vector: Vector3 = None,
                 scale_point: Vector3 = None,
                 ):
        self.rotation_axis = rotation_axis if rotation_axis else Vector3(0, 1, 0)
        self.rotation_point = rotation_point if rotation_point else Vector3(0, 0, 0)
        self.rotation_rads = rotation_rads if rotation_rads else 0
        self.scale_vector = scale_vector if scale_vector else Vector3(1, 1, 1)
        self.scale_point = scale_point if scale_point else Vector3(0, 0, 0)
        self.translation_vector = translation_vector if translation_vector else Vector3(0, 0, 0)
        self.quaternion = CoopQuaternion(axis=[0, 1, 0], angle=0)
        self._scale_adjustment = Vector3(0, 0, 0)

    def __str__(self):
        return f"Postion: {self.translation_vector}" \
               f"\nRotated: {self.quaternion.radians} around {self.quaternion.axis}" \
               f"\nScale: {self.scale_vector} at {self.scale_point}"

    def change_rotation(self,
                        rads_delta: float,
                        rotation_axis: Vector3 = None,
                        rotation_point: Vector3 = None):
        new_q = CoopQuaternion(axis=[rotation_axis.x, rotation_axis.y, rotation_axis.z], angle=rads_delta)

        self.quaternion = new_q * self.quaternion

    def change_translation(self, delta_vector: Vector3):
        self.translation_vector += delta_vector

    def change_scale(self, scale_vector: Vector3, scale_point: Vector3 = None):
        adj_scale_point = scale_point.hadamard_product(scale_vector) if scale_point else Vector3(0, 0, 0)
        self._scale_adjustment = self._scale_adjustment.hadamard_product(scale_vector) + scale_point - adj_scale_point
        self.scale_vector = self.scale_vector.hadamard_product(scale_vector)

    def reset_scale(self):
        self.scale_vector = Vector3(1, 1, 1)
        self.scale_point = Vector3(0, 0, 0)
        self._scale_adjustment = Vector3(0, 0, 0)

    @property
    def scale_adjustment(self):
        return self._scale_adjustment