import pygame
from cooptools.coopEnum import CoopEnum
from coopgame.surfaceManager import SurfaceManager, SurfaceRegistryArgs
from typing import Callable, List, Dict
from coopstructs.geometry.curves.curves import Curve
import coopgame.linedrawing.curve_draw_utils as utils
import coopgame.pygamehelpers as help
import cooptools.geometry_utils.vector_utils as vec

class CurveSurfaceType(CoopEnum):
    STATIC_BUFFER_ID = 'STATIC_BUFFER_ID'
    DYNAMIC_BUFFER_ID = 'DYNAMIC_BUFFER_ID'
    STATIC_CURVES_ID = 'STATIC_CURVES_ID'
    DYNAMIC_CURVES_ID = 'DYNAMIC_CURVES_ID'
    STATIC_OVERLAY_ID = 'OVERLAY_ID'
    DYNAMIC_OVERLAY_ID = 'DYNAMIC_OVERLAY_ID'

CurvesCallback = Callable[[], Dict[Curve, utils.CurveDrawArgs]]

class PyCurveHandler:

    def __init__(self,
                 screen: pygame.Surface,
                 get_static_curves_callback: CurvesCallback,
                 get_dynamic_curves_callback: CurvesCallback,
                 vec_transformer: vec.VecTransformer = None,
                 ):
        self._parent_screen = screen
        self._get_static_curves_callback = get_static_curves_callback
        self._get_dynamic_curves_callback = get_dynamic_curves_callback
        self._vec_transformer = vec_transformer

        self.surface_manager = SurfaceManager(
            surface_draw_callbacks=[
                SurfaceRegistryArgs(CurveSurfaceType.STATIC_BUFFER_ID.value, self.redraw_static_buffer_curves),
                SurfaceRegistryArgs(CurveSurfaceType.DYNAMIC_BUFFER_ID.value, self.redraw_dynamic_buffer_curves),
                SurfaceRegistryArgs(CurveSurfaceType.STATIC_CURVES_ID.value, self.redraw_static_curves),
                SurfaceRegistryArgs(CurveSurfaceType.DYNAMIC_CURVES_ID.value, self.redraw_dynamic_curves),
                SurfaceRegistryArgs(CurveSurfaceType.STATIC_OVERLAY_ID.value, self.redraw_static_overlay),
                SurfaceRegistryArgs(CurveSurfaceType.DYNAMIC_OVERLAY_ID.value, self.redraw_dynamic_overlay),
            ]
        )

    def show_all(self):
        self.surface_manager.show_all()

    def hide_all(self):
        self.surface_manager.hide_all()

    def toggle_surface(self, curveSurfaceTypes: List[CurveSurfaceType]):
        self.surface_manager.toggle_visible([x.value for x in curveSurfaceTypes])

    def redraw_static_buffer_curves(self) -> pygame.Surface:
        curves = self._get_static_curves_callback()
        surf = help.init_surface(self._parent_screen.get_size())
        utils.draw_curves(
            curves={k: v.BufferArgs for k, v in curves.items()},
            surface=surf,
            vec_transformer=self._vec_transformer
        )
        return surf

    def redraw_dynamic_buffer_curves(self) -> pygame.Surface:
        curves = self._get_dynamic_curves_callback()
        surf = help.init_surface(self._parent_screen.get_size())
        utils.draw_curves(
            curves={k: v.BufferArgs for k, v in curves.items()},
            surface=surf,
            vec_transformer=self._vec_transformer
        )
        return surf

    def redraw_static_curves(self) -> pygame.Surface:
        curves = self._get_static_curves_callback()
        surf = help.init_surface(self._parent_screen.get_size())
        utils.draw_curves(
            curves={k: v.BaseArgs for k, v in curves.items()},
            surface=surf,
            vec_transformer=self._vec_transformer
        )
        return surf

    def redraw_dynamic_curves(self) -> pygame.Surface:
        curves = self._get_dynamic_curves_callback()
        surf = help.init_surface(self._parent_screen.get_size())
        utils.draw_curves(
            curves={k: v.BaseArgs for k, v in curves.items()},
            surface=surf,
            vec_transformer=self._vec_transformer
        )
        return surf

    def redraw_static_overlay(self) -> pygame.Surface:
        curves = self._get_static_curves_callback()
        surf = help.init_surface(self._parent_screen.get_size())
        utils.draw_curves(
            curves={k: v.OverlayArgs for k, v in curves.items()},
            surface=surf,
            vec_transformer=self._vec_transformer
        )
        return surf

    def redraw_dynamic_overlay(self) -> pygame.Surface:
        curves = self._get_dynamic_curves_callback()
        surf = help.init_surface(self._parent_screen.get_size())
        utils.draw_curves(
            curves={k: v.OverlayArgs for k, v in curves.items()},
            surface=surf,
            vec_transformer=self._vec_transformer
        )
        return surf

    def update(self):
        self.surface_manager.update_if_visible([
            CurveSurfaceType.DYNAMIC_BUFFER_ID.value,
            CurveSurfaceType.DYNAMIC_CURVES_ID.value,
            CurveSurfaceType.DYNAMIC_OVERLAY_ID.value
        ])

    def redraw(self):
        self.surface_manager.redraw([x.value for x in CurveSurfaceType])

    def invalidate(self):
        self.redraw()

    def render(self,
               surface: pygame.Surface):
        self.update()
        self.surface_manager.render(surface)