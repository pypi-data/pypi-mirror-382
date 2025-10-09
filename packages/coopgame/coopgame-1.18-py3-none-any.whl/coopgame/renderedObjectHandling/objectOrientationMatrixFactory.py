import coopgame.renderedObjectHandling.MatrixManipulation as mm
from coopgame.renderedObjectHandling.objectOrientationArgs import ObjectOrientationArgs
import numpy as np



def object_orientation_matrix(orientation_args: ObjectOrientationArgs, invert:bool = False):
    """
    In order, applies Translation, Rotation, then Scale

    :return: 4x4 np.array matrix
    """


    # Allow inversion of translation vector and radians which is useful if what is being represented is a "viewer" (camera) rather than an object.
    adj = 1
    if invert:
        adj = -1

    # Create Translation Matrix
    translation_matrix = mm.translationMatrix(adj * orientation_args.translation_vector.x,
                                              adj * orientation_args.translation_vector.y,
                                              adj * orientation_args.translation_vector.z)

    # Create Rotation Matrix
    rotation_matrix = mm.rotateAroundAxis(orientation_args.rotation_point.as_tuple(),
                                          orientation_args.rotation_axis.as_tuple(),
                                          radians=orientation_args.rotation_rads * adj)

    # Create Scale Matrix
    # scale_matrix = mm.scaleAroundPoint(orientation_args.scale_point.as_tuple(),
    #                                    orientation_args.scale_vector.as_tuple())
    scale_matrix = mm.scaleAroundPoint((0, 0, 0),
                                       orientation_args.scale_vector.as_tuple())

    scale_translate_matrix = mm.translationMatrix(*orientation_args.scale_adjustment.as_tuple())

    ret = scale_translate_matrix.dot(scale_matrix.dot(rotation_matrix.dot(translation_matrix)))

    return ret


def quaternion_rotation_matrix(Q):
    # https://automaticaddison.com/how-to-convert-a-quaternion-to-a-rotation-matrix/
    # https://stackoverflow.com/questions/1556260/convert-quaternion-rotation-to-rotation-matrix
    """
    Covert a quaternion into a full three-dimensional rotation matrix.

    Input
    :param Q: A 4 element array representing the quaternion (q0,q1,q2,q3)

    Output
    :return: A 4x4 element matrix representing the full 3D rotation matrix.
             This rotation matrix converts a point in the local reference
             frame to a point in the global reference frame.
    """

    # qx = Q[0]
    # qy = Q[1]
    # qz = Q[2]
    # qw = Q[3]
    #
    # ret = np.array([
    #     [1.0 - 2.0 * qy * qy - 2.0 * qz * qz, 2.0 * qx * qy - 2.0 * qz * qw, 2.0 * qx * qz + 2.0 * qy * qw, 0.0],
    #     [2.0 * qx * qy + 2.0 * qz * qw, 1.0 - 2.0 * qx * qx - 2.0 * qz * qz, 2.0 * qy * qz - 2.0 * qx * qw, 0.0],
    #     [2.0 * qx * qz - 2.0 * qy * qw, 2.0 * qy * qz + 2.0 * qx * qw, 1.0 - 2.0 * qx * qx - 2.0 * qy * qy, 0.0],
    #     [0.0, 0.0, 0.0, 1.0],
    # ])
    #
    # return ret



    # Extract the values from Q
    q0 = Q[0]
    q1 = Q[1]
    q2 = Q[2]
    q3 = Q[3]

    # First row of the rotation matrix
    r00 = 2 * (q0 * q0 + q1 * q1) - 1
    r01 = 2 * (q1 * q2 - q0 * q3)
    r02 = 2 * (q1 * q3 + q0 * q2)

    # Second row of the rotation matrix
    r10 = 2 * (q1 * q2 + q0 * q3)
    r11 = 2 * (q0 * q0 + q2 * q2) - 1
    r12 = 2 * (q2 * q3 - q0 * q1)

    # Third row of the rotation matrix
    r20 = 2 * (q1 * q3 - q0 * q2)
    r21 = 2 * (q2 * q3 + q0 * q1)
    r22 = 2 * (q0 * q0 + q3 * q3) - 1

    # 4x4 rotation matrix
    rot_matrix = np.array([[r00, r01, r02, 0],
                           [r10, r11, r12, 0],
                           [r20, r21, r22, 0],
                           [0,     0,   0, 1]])

    return rot_matrix