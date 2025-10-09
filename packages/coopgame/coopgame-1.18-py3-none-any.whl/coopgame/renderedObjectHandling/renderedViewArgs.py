from coopgame.renderedObjectHandling.objectOrientationArgs import ObjectOrientationArgs
import math

class RenderedViewArgs:
    def __init__(self,
                 near_plane_dist: float = None,
                 far_plane_dist: float = None,
                 field_of_view_rads: float = None,
                 camera_orientation_args: ObjectOrientationArgs = None
                 ):
        self.camera_orientation = camera_orientation_args if camera_orientation_args else ObjectOrientationArgs()
        self.near_plane_dist = near_plane_dist if near_plane_dist else .1
        self.far_plane_dist = far_plane_dist if far_plane_dist else 100
        self.field_of_view_rads = field_of_view_rads if field_of_view_rads else math.pi / 2