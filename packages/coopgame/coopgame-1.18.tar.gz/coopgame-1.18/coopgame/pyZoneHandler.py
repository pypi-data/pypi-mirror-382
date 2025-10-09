import logging

from coopstructs.zones import ZoneManager, ZoneAlreadyExistsException, ZoneDoesntExistException, zoneLogger
from coopstructs.vectors import Vector2
from coopstructs.geometry import Rectangle
from cooptools.colors import Color
import pygame
from coopgame.pygamehelpers import draw_polygon, draw_text
from typing import List, Callable, Any
import coopgame.pygamehelpers as help
from coopstructs.toggles import IntegerRangeToggleable

class PyZoneHandler:

    def __init__(self):
        self.zm = ZoneManager()
        self.colors = {}
        self.active_zone_name: str = None
        self.layer_selector = IntegerRangeToggleable(min=0, max=0, starting_value=0)
        self.origin = None

    def set_active_zone(self, point: Vector2):
        zOptions = self.zm.member_zones([point])[point]
        self.active_zone_name = zOptions[self.layer_selector.value]

    def add_to_active_zone(self, point: Vector2, at_idx: int = None):
        if self.active_zone_name is not None:
            try:
                self.zm.add_to_zone(self.active_zone_name, point, at_idx=at_idx)
            except Exception as e:
                logging.error(f"Skip adding point {point}: {e}")

    def remove_from_active_zone(self):
        if self.active_zone_name is not None:
            self.zm.remove_last_point_from_zone(self.active_zone_name)

    def init_new_zone(self,
                      naming_provider: Callable[[], str] = None,
                      initial_points: List[Vector2] = None,
                      set_active: bool = True):
        name = naming_provider()

        if name is None:
            return

        color = Color.random()

        self.zm.init_new_zone(name, initial_points=initial_points)
        self.colors[name] = color
        if set_active: self.active_zone_name = name

    def draw_zones(self,
                   surface: pygame.Surface,
                   alpha: int = 90,
                   draw_zone_label: bool = True,
                   draw_point_labels: bool = True,
                   draw_scale_matrix=None,
                   excluded_zones: List[str] = None):
        for name, zone in self.zm.zones.items():
            if excluded_zones and name in excluded_zones:
                continue

            self.draw_zone(zone_name=name,
                           surface=surface,
                           alpha=alpha,
                           draw_zone_label=draw_zone_label,
                           draw_point_labels=draw_point_labels,
                           draw_scale_matrix=draw_scale_matrix)

    def draw_zone(self,
                  zone_name: str,
                  surface: pygame.Surface,
                  alpha: int = 90,
                  draw_zone_label: bool = True,
                  draw_point_labels: bool = True,
                  draw_scale_matrix=None,
                  ):

        zone = self.zm.zones[zone_name]
        if zone.valid:
            scaled_points = help.scaled_points(zone.boundary_points, transform_matrix=draw_scale_matrix)

            width = 0 if zone_name != self.active_zone_name else 10
            draw_polygon(surface, scaled_points, self.colors[zone_name], alpha=alpha, width=width)

            if draw_zone_label:
                center = help.scaled_points([zone.center], transform_matrix=draw_scale_matrix)[0]
                draw_text(zone_name, surface, offset_rect=Rectangle(center.x, center.y, 100, 100),
                          color=Color.furthest_color(self.colors[zone_name].value))

            if draw_point_labels:
                for idx, point in enumerate(zone.boundary_points):
                    draw_text(str(idx), surface, offset_rect=Rectangle(point.x, point.y, 100, 100),
                              color=Color.furthest_color(self.colors[zone_name].value))


