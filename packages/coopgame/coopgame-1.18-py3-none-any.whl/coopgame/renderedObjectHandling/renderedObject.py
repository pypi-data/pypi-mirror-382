from coopgame.renderedObjectHandling.wireframes import Wireframe
from coopgame.renderedObjectHandling.objectOrientationArgs import ObjectOrientationArgs
from coopgame.coordinateConverter import CoordinateConverter as cc
from coopgame.renderedObjectHandling.objectOrientationMatrixFactory import object_orientation_matrix
from coopgame.renderedObjectHandling.renderedViewArgs import RenderedViewArgs
import math
import coopgame.renderedObjectHandling.MatrixManipulation as mm
import numpy as np
from coopgame.models.primitives.coopquaternion import CoopQuaternion

class RenderedObject:
    def __init__(self,
                 wireframe: Wireframe):
        self._object_wireframe = wireframe
        self.orientation = ObjectOrientationArgs()

    @property
    def world_nodes(self):
        centre = self._object_wireframe.object_centre[:3] + self.orientation.translation_vector.as_tuple()
        return self._apply_orientation(points=self._object_wireframe.nodes,
                                       orientation_args=self.orientation,
                                       centre=centre)

        # # Apply translation
        # translated_nodes = cc.apply_matrix_to_array(self._object_wireframe.nodes, self._translation_matrix(self.orientation))
        #
        # # Apply Quaternion rotation
        # centre = self._object_wireframe.object_centre[:3] + self.orientation.translation_vector.as_tuple()
        # rotated_points = self.orientation.quaternion.rotate_all(translated_nodes, centre)
        #
        # # Scale the points
        # scaled_nodes = cc.apply_matrix_to_array(rotated_points, self._scale_matrix(self.orientation))
        #
        # return scaled_nodes


    @property
    def world_edges(self):
        return self._object_wireframe.translated_edges(object_orientation_matrix(self.orientation))

    @property
    def world_center(self):
        ret = self._object_wireframe.findCentre(object_orientation_matrix(self.orientation))

        if not math.isclose(ret[0], self._object_wireframe.nodes[0][0] + self._object_wireframe.size / 2 + self.orientation.translation_vector.x):
            print(ValueError("Error calculating the world_center"))

        return ret

    def camera_nodes(self, render_view_args: RenderedViewArgs):
        centre = self.world_center
        return self._apply_orientation(self.world_nodes,
                                       render_view_args.camera_orientation,
                                       centre=centre,
                                       invert=True)
        # return cc.apply_matrix_to_array(self.world_nodes,
        #                                 object_orientation_matrix(render_view_args.camera_orientation,
        #                                                           invert=True))

    def camera_edges(self, render_view_args: RenderedViewArgs):
        cam_nodes = self.camera_nodes(render_view_args)
        return [(cam_nodes[n1][:2], cam_nodes[n2][:2]) for n1, n2 in self._object_wireframe.edge_node_ids]

    def camera_center(self, render_view_args: RenderedViewArgs):
        centre = self.world_center
        return self._apply_orientation(self.world_center,
                                       render_view_args.camera_orientation,
                                       centre=centre,
                                       invert=True)
        # return cc.apply_matrix_to_array(self.world_center,
        #                                 object_orientation_matrix(render_view_args.camera_orientation,
        #                                                           invert=True))

    @staticmethod
    def _translation_matrix(orientation_args: ObjectOrientationArgs, invert:bool = False):
        # Allow inversion of translation vector and radians which is useful if what is being represented is a "viewer" (camera) rather than an object.
        adj = 1
        if invert:
            adj = -1

        # Create Translation Matrix
        translation_matrix = mm.translationMatrix(adj * orientation_args.translation_vector.x,
                                                  adj * orientation_args.translation_vector.y,
                                                  adj * orientation_args.translation_vector.z)

        return translation_matrix

    @staticmethod
    def _scale_matrix(orientation_args: ObjectOrientationArgs):
        # Create Scale Matrix
        scale_matrix = mm.scaleAroundPoint(orientation_args.scale_point.as_tuple(),
                                           orientation_args.scale_vector.as_tuple())

        return scale_matrix


    def _apply_orientation(self, points: np.array, orientation_args: ObjectOrientationArgs, centre: np.array, invert:bool=False):
        # Apply translation
        translated_nodes = cc.apply_matrix_to_array(points, self._translation_matrix(orientation_args,
                                                                                     invert=invert))

        # Apply Quaternion rotation
        if invert:
            axis = orientation_args.quaternion.axis if orientation_args.quaternion.angle != 0 else [1, 0, 0]
            quat = CoopQuaternion(axis=axis, angle=-orientation_args.quaternion.angle)
        else:
            quat = orientation_args.quaternion
        rotated_points = quat.rotate_all(translated_nodes, centre)

        # Scale the points
        scaled_nodes = cc.apply_matrix_to_array(rotated_points, self._scale_matrix(orientation_args))

        return scaled_nodes
