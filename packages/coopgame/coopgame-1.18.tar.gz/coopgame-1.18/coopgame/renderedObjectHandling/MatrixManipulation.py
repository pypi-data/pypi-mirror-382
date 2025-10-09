import numpy as np

def rotation_unit_vector(axis: np.array):
    return axis / (axis ** 2).sum() ** 0.5

def translationMatrix(dx=0, dy=0, dz=0):
    """ Return matrix for translation along vector (dx, dy, dz). """
    return np.array([[1, 0, 0, dx],
                     [0, 1, 0, dy],
                     [0, 0, 1, dz],
                    [0, 0, 0, 1]])

def scaleMatrix(sx=0, sy=0, sz=0):
    """ Return matrix for scaling equally along all axes centred on the point (cx,cy,cz). """
    return np.array([[sx, 0, 0, 0],
                     [0, sy, 0, 0],
                     [0, 0, sz, 0],
                     [0, 0, 0, 1]])

def rotateXMatrix(radians):
    """ Return matrix for rotating about the x-axis by 'radians' radians """
    c = np.cos(radians)
    s = np.sin(radians)
    return np.array([[1, 0, 0, 0],
                     [0, c, s, 0],
                     [0, -s, c, 0],
                     [0, 0, 0, 1]])

def rotateYMatrix(radians):
    """ Return matrix for rotating about the y-axis by 'radians' radians """
    c = np.cos(radians)
    s = np.sin(radians)
    return np.array([[c, 0, -s, 0],
                     [0, 1, 0, 0],
                     [s, 0, c, 0],
                     [0, 0, 0, 1]])

def rotateZMatrix(radians):
    """ Return matrix for rotating about the z-axis by 'radians' radians """
    c = np.cos(radians)
    s = np.sin(radians)
    return np.array([[c, s, 0, 0],
                     [-s, c, 0, 0],
                     [0, 0, 1, 0],
                     [0, 0, 0, 1]])

def rotateAroundAxis(rotationPoint, rotationAxis, radians):
    # http://www.fastgraph.com/makegames/3drotation/
    # https://sites.google.com/site/glennmurray/Home/rotation-matrices-and-formulas/rotation-about-an-arbitrary-axis-in-3-dimensions
    c = np.cos(radians)
    s = np.sin(radians)
    t = 1 - np.cos(radians)

    u = rotationAxis[0]
    v = rotationAxis[1]
    w = rotationAxis[2]


    ''' Build the transposes into the matrix'''
    x = rotationPoint[0]
    y = rotationPoint[1]
    z = rotationPoint[2]
    calculated_matrix = np.array([[u**2 + (v**2 + w**2) * c, u*v*t-w*s,              u*w*t+v*s,              (x*(v**2 + w**2) - u*(y*v + z*w))*t + (y*w-z*v)*s],
                                 [u*v*t + w*s,              v**2 + (u**2 + w**2)*c, v*w*t-u*s,              (y*(u**2 + w**2) - v*(x*u + z*w))*t + (z*u-x*w)*s],
                                 [u*w*t - v*s,              v*w*t + u*s,            w**2 + (u**2 + v**2)*c, (z*(u**2 + v**2) - w*(x*u + y*v))*t + (x*v-y*u)*s],
                                 [0,                        0,                      0,                      1]])

    # r00 = t * u * u + c
    # r01 = t * u * v - s * w
    # r02 = t * u * w + s * u
    # r10 = t * u * v + s * w
    # r11 = t * v * v + c
    # r12 = t * v * w - s * u
    # r20 = t * u * w - s * u
    # r21 = t * v * w + s * u
    # r22 = t * w * w + c
    # r03 = (x*(v**2 + w**2) - u*(y*v + z*w))*t + (y*w-z*v)*s
    # r13 = (y*(u**2 + w**2) - v*(x*u + z*w))*t + (z*u-x*w)*s
    # r23 = (z*(u**2 + v**2) - w*(x*u + y*v))*t + (x*v-y*u)*s
    # calculated_matrix = np.array([[r00, r01, r02, r03],
    #                               [r10, r11, r12, r13],
    #                               [r20, r21, r22, r23],
    #                               [0,   0,   0,   1]])

    return calculated_matrix

def get_grid_rotation_matrix(rotation_axis_x, rotation_axis_z, x_rot_rads, z_rot_rads):

    # Rot Z
    orientation = np.array([0, 0, 1])
    ruv = rotation_unit_vector(orientation)
    matrixz = rotateAroundAxis((rotation_axis_x, rotation_axis_z, 0), ruv, z_rot_rads)

    # Rot X
    orientation = np.array([1, 0, 0])
    ruv = rotation_unit_vector(orientation)
    matrixx = rotateAroundAxis((rotation_axis_x, rotation_axis_z, 0), ruv,
                                  x_rot_rads)
    matrix = matrixx.dot(matrixz)
    return matrix



    # translationM = translationMatrix(-rotationPoint[0], -rotationPoint[1], -rotationPoint[2])
    # print (f"translationM: \n{translationM}")
    # # return translationM
    # translationMInv = translationMatrix(rotationPoint[0], rotationPoint[1], rotationPoint[2])
    #
    #
    # matrix =  np.array([[t * u ** 2 + c,    t * u * v - s * w,  t * u * w + s * v,  0],
    #                     [t * u * v + s * w, t * v**2 + c,       t*v*w-s*u,          0],
    #                     [t*u*w - s*v,       t*v*w+s*u,          t*w**2+c,           0],
    #                     [0,                 0,                  0,                  1]])
    #
    #
    # # return matrix
    # with np.printoptions(precision=3, suppress=True):
    #     print(f"Rotation \n{matrix}")
    #     print(matrix.dot(translationM))
    #     finalTransform = translationMInv.dot(matrix.dot(translationM))
    #     # finalTransform = translationM.dot(matrix).dot(translationMInv)
    #     print(f"Final Transform: \n{finalTransform}")
    #
    #     print(f"clc: {calculated_matrix}")
    #     print(f"mat: {finalTransform}")
    #
    # return finalTransform


def rotateAroundPoint( point, rotationVector):

    translationM = translationMatrix(-point[0], -point[1], -point[2])


    translationMInv = translationMatrix(point[0], point[1], point[2])
    rX = rotateXMatrix(rotationVector[0])
    rY = rotateYMatrix(rotationVector[1])
    rZ = rotateZMatrix(rotationVector[2])

    return translationM.dot(rX.dot(rY.dot(rZ.dot(translationMInv))))

def scaleAroundPoint(point, scalarVector):
    translationM = translationMatrix(-point[0], -point[1], -point[2])
    translationMInv = translationMatrix(point[0], point[1], point[2])
    scaleM = scaleMatrix(*scalarVector)
    matrix = translationMInv.dot(scaleM.dot(translationM))

    return matrix



if __name__ == "__main__":
    import math
    import time
    from coopstructs.vectors import Vector3
    rot_point = (1, 100, 0)
    start = (1, 2, 0, 1)
    rot_axis = Vector3(1, 1, 1).unit().as_tuple()
    rads = math.pi / 2

    R = rotateAroundAxis(rot_point, rot_axis, rads)
    # print(np.array(start))
    # current = (np.dot(R, np.transpose(start)).round(3))
    # print(current)
    # current = (np.dot(R, np.transpose(current)).round(3))
    # print(current)
    # current = (np.dot(R, np.transpose(current)).round(3))
    # print(current)
    # current = (np.dot(R, np.transpose(current)).round(3))
    # print(current)

    current = np.array(start)
    while True:
        current = (np.dot(R, np.transpose(current)).round(3))
        print(current.round(1))
        time.sleep(.5)