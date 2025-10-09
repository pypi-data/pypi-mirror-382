from typing import List
from coopstructs.geometry.vectors.vectorN import VectorN, Vector2, Vector3
import numpy as np
import coopgame.pygamehelpers as help
from coopstructs.geometry import Rectangle
import math
from coopgame.renderedObjectHandling.objectOrientationArgs import ObjectOrientationArgs
from coopgame.renderedObjectHandling.objectOrientationMatrixFactory import object_orientation_matrix
from coopgame.renderedObjectHandling.renderedViewArgs import RenderedViewArgs

class DrawMatrixState:

    def __init__(self,
                 cameras_vision_matrix=None,
                 perspective_matrix=None):
        self.cameras_vision_matrix = cameras_vision_matrix
        self.perspective_matrix = perspective_matrix

    def set_matricies(self, rendered_view_args: RenderedViewArgs):
        self.cameras_vision_matrix = self._create_cameras_vision_matrix(camera_orientation=rendered_view_args.camera_orientation)
        self.perspective_matrix = self._create_viewport_projection_matrix(near_plane_dist=rendered_view_args.near_plane_dist,
                                                                        far_plane_dist=rendered_view_args.far_plane_dist,
                                                                        field_of_view_rads=rendered_view_args.field_of_view_rads)
    @staticmethod
    def _create_cameras_vision_matrix(camera_orientation: ObjectOrientationArgs):
        return object_orientation_matrix(camera_orientation)

    @staticmethod
    def _create_viewport_projection_matrix(near_plane_dist: float = None,
                                           far_plane_dist: float = None,
                                           field_of_view_rads: float = None):
        # https://www.scratchapixel.com/lessons/3d-basic-rendering/perspective-and-orthographic-projection-matrix/building-basic-perspective-projection-matrix

        if near_plane_dist is None:
            near_plane_dist = 0

        if far_plane_dist is None:
            far_plane_dist = 1000000

        if field_of_view_rads is None:
            field_of_view_rads = math.pi / 2

        # field_of_view_degrees = field_of_view_rads * 180 / math.pi
        S = 1 / math.tan(field_of_view_rads / 2)

        a = - far_plane_dist / (far_plane_dist - near_plane_dist)
        b = - (far_plane_dist * near_plane_dist) / (far_plane_dist - near_plane_dist)

        # Transpose because we assume we apply S * x (matrix on left)
        return np.array([[S, 0, 0, 0],
                         [0, S, 0, 0],
                         [0, 0, a, b],
                         [0, 0, -1, 0]])


class MultiPerspectivePointConverter:

    def __init__(self):

        self._real_world_points = None
        self._camera_view_world_points = None
        self._projection_points = None
        self._viewport_points = None

    @property
    def real_world_points(self):
        return self._real_world_points

    @property
    def camera_view_world_points(self):
        return self._camera_view_world_points

    @property
    def viewport_points(self):
        return self._viewport_points

    @property
    def projection_points(self):
        return self._projection_points

    def convert_real_to_viewport(self,
                real_points: List[Vector3],
                matrix_state: DrawMatrixState,
                game_area_rect: Rectangle,
                ):
        self._real_world_points = real_points
        self._camera_view_world_points = CoordinateConverter.world_to_scaled_points(self.real_world_points, matrix_state.cameras_vision_matrix)

        self._projection_points = CoordinateConverter.scale_points(self._camera_view_world_points, matrix_state.perspective_matrix)

        self._viewport_points = [Vector2(min(game_area_rect.width - 1, ((point.x + 1) * 0.5 * game_area_rect.width)),
                                         min(game_area_rect.height - 1, ((1 - (point.y + 1) * 0.5) * game_area_rect.height)
                                             )) for point in self._projection_points]
        return self._viewport_points

    def convert_viewport_to_real(self,
                                  viewport_points: List[Vector2],
                                  game_area_rect: Rectangle,
                                  world_plane_points: List[Vector3],
                                  matrix_state: DrawMatrixState,
                                  ):
        self._viewport_points = viewport_points
        self._camera_view_world_points = CoordinateConverter.viewport_points_on_a_world_plane(viewport_points=viewport_points,
                                                                                           game_area_rect=game_area_rect,
                                                                                           world_plane_points=world_plane_points)


        inv_camera_mat = np.linalg.inv(matrix_state.cameras_vision_matrix)
        self._real_world_points = CoordinateConverter.scale_points(self._camera_view_world_points, inv_camera_mat)


class CoordinateConverter:
    @classmethod
    def world_to_scaled_points(cls, world_points: List[VectorN], matrix=None):
        return cls.scale_points(world_points, matrix=matrix)

    @classmethod
    def mouse_viewport_pos_as_vector(cls, viewport: Rectangle):
        return help.game_area_coords_from_parent_coords(parent_coords=help.mouse_pos_as_vector(),
                                                        game_area_surface_rectangle=viewport)

    @classmethod
    def _scaled_rectangle_points(cls, rectangle: Rectangle, matrix=None):
        rec_points = [Vector2(point[0], point[1]) for point in rectangle.points_tuple()]
        return cls.scale_points(rec_points,
                                  matrix=matrix)

    @classmethod
    def mouse_world_pos(cls, game_area_rect: Rectangle, draw_scale_matrix=None):
        points_on_plane = cls._scaled_rectangle_points(game_area_rect, draw_scale_matrix)
        mouse_viewport_pos = cls.mouse_viewport_pos_as_vector(game_area_rect)

        mouse_pos_in_world = cls.viewport_points_on_a_world_plane([mouse_viewport_pos],
                                                                  game_area_rect=game_area_rect,
                                                                  world_plane_points=points_on_plane)[0]
        return mouse_pos_in_world

    @classmethod
    def viewport_points_on_a_world_plane(cls,
                                         viewport_points: List[Vector2],
                                         game_area_rect: Rectangle,
                                         world_plane_points: List[Vector3] = None) -> List[Vector3]:

        if world_plane_points is None:
            viewport_points = game_area_rect.points_tuple()
            world_plane_points = [Vector3(point[0], point[1], 0) for point in viewport_points]
        elif len(world_plane_points) < 3:
            raise ValueError(f"plane needs to be defined by at least 3 points but {len(world_plane_points)} were given")

        plane_point = cls.points_projected_to_plane(viewport_points, world_plane_points[0], world_plane_points[1], world_plane_points[2])

        return plane_point

    @staticmethod
    def points_projected_to_plane(viewport_points: List[Vector2],
                                      plane_point_1: Vector3,
                                      plane_point_2: Vector3,
                                      plane_point_3: Vector3) -> List[Vector3]:

        vec1 = plane_point_1 - plane_point_2
        vec2 = plane_point_3 - plane_point_2

        normal = np.cross(vec1.as_tuple(), vec2.as_tuple())
        a = normal[0]
        b = normal[1]
        c = normal[2]
        d = a * plane_point_1.x + b * plane_point_1.y + c * plane_point_1.z

        z_val_lam = lambda point: (d - a * point.x - b * point.y) / c
        # z_val = (d - a * viewport_point.x - b * viewport_point.y) / c

        return [Vector3(point.x, point.y, z_val_lam(point)) for point in viewport_points]



    @staticmethod
    def apply_matrix_to_array(array: np.array, matrix=None, round_digits: int = 10):
        if matrix is None:
            matrix = np.identity(4)

        # Multiply the points by the transform matrix for drawing'''
        transformed_points = matrix.dot(
            np.transpose(array))  # Transpose the points to appropriately multiply

        ret = np.transpose(transformed_points)

        if ret.size == 4:
            ret = ret / ret[3]
        else:
            ret = ret / ret[:, 3].reshape((ret.shape[0], 1))
        return ret.round(round_digits)

    @classmethod
    def scale_points(cls, points: List[VectorN], matrix=None) -> List[VectorN]:

        if len(points) == 0 or matrix is None:
            return points

        '''Convert the point to a 4-dim point for multiplication'''
        normal_array = [(point.x, point.y, point.z if point.z else 0, 1) for point in points]

        # Scale the array
        scaled_array = cls.apply_matrix_to_array(normal_array, matrix=matrix)

        # Convert back to points
        scaled_points = [VectorN({'x': point[0], 'y':point[1], 'z': point[2]}) for point in scaled_array]
        for ii, point in enumerate(points):
            if type(point) == Vector2:
                scaled_points[ii] = Vector2(scaled_points[ii].x, scaled_points[ii].y)
            elif type(point) == Vector3:
                scaled_points[ii] = Vector3(scaled_points[ii].x, scaled_points[ii].y, scaled_points[ii].z)


        return scaled_points

if __name__ == "__main__":
    from pprint import pprint
    real_points = [
        Vector3(1, 1, 3),
        Vector3(2, 5, 6),
        Vector3(1, 8, 1),
        Vector3(10, -5, 100)
    ]

    viewport_points = [
        Vector2(10, 5),
        Vector2(100, 25)
    ]

    world_plane_points = [
        Vector3(0, 0, -10),
        Vector3(10, 0, -10),
        Vector3(0, 10, -10)
    ]

    game_area = Rectangle(0, 0, 1000, 1000)

    translation_vector = Vector3(0, 0, 0)
    rotation_point = Vector3(0, 0, 0)
    rotation_vector = None
    rotation_rads = None
    scale_vector = None
    near_plane_dist = 1
    far_plane_dist = 5
    field_of_view_rads = math.pi / 2
    matrix_state = DrawMatrixState()

    camera_orientation_args = ObjectOrientationArgs(
        translation_vector=translation_vector,
        rotation_point=rotation_point,
        rotation_axis=rotation_vector,
        rotation_rads=rotation_rads,
        scale_vector=scale_vector,
    )

    rendered_view_args = RenderedViewArgs(
        near_plane_dist=near_plane_dist,
        far_plane_dist=far_plane_dist,
        field_of_view_rads=field_of_view_rads,
        camera_orientation_args=camera_orientation_args
    )
    matrix_state.set_matricies(rendered_view_args=rendered_view_args)
    pc = MultiPerspectivePointConverter()



    pc.convert_real_to_viewport(real_points=real_points,
                                matrix_state=matrix_state,
                                game_area_rect=game_area)
    pprint(pc.real_world_points)
    pprint(pc.camera_view_world_points)
    pprint(pc.projection_points)
    pprint(pc.viewport_points)

    pc.convert_viewport_to_real(viewport_points=viewport_points,
                                game_area_rect=game_area,
                                world_plane_points=world_plane_points,
                                matrix_state=matrix_state)

    pprint(pc.real_world_points)
    pprint(pc.camera_view_world_points)
    pprint(pc.viewport_points)