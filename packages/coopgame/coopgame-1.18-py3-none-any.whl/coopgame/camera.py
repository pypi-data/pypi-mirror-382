from cooptools.transform import Transform
from typing import Iterable
import cooptools.geometry_utils.vector_utils as vec
import cooptools.matrixManipulation as mm
from coopstructs.geometry.rectangles.rectangle import Rectangle
import math
from cooptools.coopEnum import CardinalPosition

class Camera3d:

    def __init__(self):
        self._transform = Transform()
        self._field_of_view_rads = math.pi / 2
        self._near_plane_dist = 0.01
        self._far_plane_dist = 100

    def get_viewport_rect(self,
                          viewport_dims: vec.FloatVec) -> Rectangle:
        cx, cy = self._transform.Translation.Vector[:2]

        ox = cx - viewport_dims[0] / 2
        oy = cy - viewport_dims[1] / 2

        return Rectangle.from_tuple((ox, oy, viewport_dims[0], viewport_dims[1]))

    def scroll(self, delta_vector):
        self._transform.Translation.update(delta_vector=delta_vector)


    def zoom(self,
             rads_scalar: float = None):

        self._field_of_view_rads *= rads_scalar

    #TODO: Figure out the calc for field of view given the input rect
    # def zoom_to_rect(self,
    #                  pos: Iterable[float],
    #                  dims: Iterable[float],
    #                  cardinality: CardinalPosition = None
    #                  ):
    #
    #     if cardinality is None:
    #         cardinality = CardinalPosition.BOTTOM_LEFT
    #
    #     center = CardinalPosition.alignment_conversion(
    #         dims=dims,
    #         anchor=pos,
    #         from_cardinality=cardinality,
    #         to_cardinality=CardinalPosition.CENTER
    #     )
    #
    #     self.center_at(
    #         pos=center
    #     )
    #




    def center_around_points(self,
                             points: vec.IterVec):
        minX = min(x[0] for x in points)
        maxX = max(x[0] for x in points)
        minY = min(x[1]for x in points)
        maxY = max(x[1] for x in points)
        minZ = min(x[2]for x in points)
        maxZ = max(x[2] for x in points)

        o = (minX + (maxX - minX) / 2, minY + (maxY - minY) / 2, minZ + (maxZ - minZ) / 2)

        self.center_at(pos=o)

    def center_at(self,
                  pos: vec.FloatVec
    ):
        self._transform.Translation.update(
            vector=pos
        )

    @property
    def PerspectiveMatrix(self):
        p = mm.perspective_matrix(
            near_plane_dist=self._near_plane_dist,
            far_plane_dist=self._far_plane_dist,
            field_of_view_rads=self._field_of_view_rads
        )
        return p

    @property
    def TransformMatrix(self):
        t = self._transform.transform_matrix(
            inversions=['x', 'y', 'z']
        )
        return t

    def get_screen_adjustment_matrix(self,viewport_dims: vec.FloatVec):
        return mm.translationMatrix(viewport_dims[0] / 2, viewport_dims[1] / 2, 0)

    def view_points(self,
                    points: vec.IterVec,
                    viewport_dims: vec.FloatVec) -> vec.LstVec:
        transformed = mm.point_transform_3d(
            points=points,
            translationM=self._transform.Translation.inversion(inversion_idxs=[0, 1, 2]).TranslationMatrix,
            scaleM=self._transform.Scale.ScaleMatrix,
            rotationM=self._transform.Rotation.RotationMatrix,
            perspectiveM=self.PerspectiveMatrix,
            post_perspective_translationM=self.get_screen_adjustment_matrix(viewport_dims),
        )
        return transformed



    def viewing_matrix(self,
                       viewport_dims: vec.FloatVec,
                       swaps: Iterable[str] = None,
                       near_plane_dist: float = None,
                       far_plane_dist: float = None):

        t = self._transform.transform_matrix(
            swaps=swaps,
            inversions=['x', 'y', 'z'],
        )

        screen_center_adj = mm.translationMatrix(viewport_dims[0] / 2, viewport_dims[1] / 2, 0)

        p = mm.perspective_matrix(
            near_plane_dist=near_plane_dist,
            far_plane_dist=far_plane_dist,
            field_of_view_rads=self._field_of_view_rads
        )

        pt = p.dot(t)



        ret1 = screen_center_adj.dot(pt)
        ret = pt
        return ret


if __name__ == "__main__":
    cam = Camera3d()
    cam.center_at((500, 500))

    print(cam.get_true_pos(
        viewport_points=[(0, 0, 0), (100, 250, 0)],
        viewport_dims=(500, 250)
    ))


