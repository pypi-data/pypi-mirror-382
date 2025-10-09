from pyquaternion import Quaternion
import numpy as np

class CoopQuaternion(Quaternion):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def rotate_all(self, points: np.array, rotation_point: np.array):
        return self._rotate_all_mat(points, rotation_point)

    def _rotate_all_mat(self, points: np.array, rotation_point: np.array):
        if len(rotation_point) < 4:
            rotation_point = np.append(rotation_point, 0)

        centre = rotation_point[:4]
        centered_points = points - centre

        rotated_points = np.transpose(self.transformation_matrix.dot(np.transpose(centered_points)))
        recentered_points = rotated_points + centre

        return recentered_points
        # return np.vstack(recentered_points, np.ones(recentered_points.shape[0]))


    def _rotate_all_iter(self, points: np.array, rotation_point: np.array):
        # https://math.stackexchange.com/questions/18382/quaternion-and-rotation-about-an-origin-and-an-arbitrary-axis-origin-help
        centre = rotation_point[:3]
        centered_points = points[:, :3] - centre

        rotated_list = []

        # TODO: find an optimization that doesnt require iterating on the list of points
        for ii in range(0, len(points)):
            point = self.rotate(centered_points[ii]) + centre
            rotated_list.append(tuple(point) + (1, ))

        return np.array(rotated_list)