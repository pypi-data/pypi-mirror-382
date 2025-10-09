from typing import List, Callable, Any
from coopstructs.geometry.vectors.vectorN import Vector2
import coopgame.pygamehelpers as help
import pygame

class SnapState:
    def __init__(self, snap_sound: pygame.mixer.Sound = None):
        self.snap_point = None
        self.snap_sound = snap_sound
        self.snappables = []

    def set_snappables(self, snappables: List[Vector2]):
        self.snappables = snappables

    def set_snap_point(self,
                       mouse_pos: Vector2,
                       snap_distance: float,
                       draw_scale_matrix = None,
                       on_snap_callback: Callable[[Vector2], Any] = None,
                       on_unsnap_callback: Callable[[Vector2], Any] = None,
                       snappable_points: List[Vector2] = None) -> Vector2:

        # update snappable list
        if snappable_points:
            self.set_snappables(snappable_points)

        # return if no eligible snappables
        if self.snappables is None or len(self.snappables) == 0:
            return None

        # get the scaled list of points
        normal_array = help.normal_points_to_scaled_points(self.snappables,
                                                                          draw_scale_matrix=draw_scale_matrix)
        normal_snap_points = [Vector2(point[0], point[1]) for point in normal_array]

        # get the closest point in snappable list
        old = self.snap_point
        closest_scaled_point = mouse_pos.closest_within_threshold(normal_snap_points, snap_distance)

        # update snappoint
        self.snap_point = help.scaled_points_to_normal_points([closest_scaled_point], draw_scale_matrix=draw_scale_matrix)[0] if closest_scaled_point else None

        # handle callbacks
        if on_unsnap_callback is not None \
            and ((self.snap_point is None and old is not None)
                or (self.snap_point != old)):
            on_unsnap_callback(old)

        if self.snap_point is not None and old != self.snap_point:
            if on_snap_callback is not None:
                on_snap_callback(self.snap_point)

            # play the snap sound
            if self.snap_sound:
                pygame.mixer.Sound.play(self.snap_sound)

        return self.snap_point
