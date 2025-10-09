import time
import pygame
from cooptools.dictPolicies import TogglePolicy
from cooptools.sectors.grids import RectGrid
from cooptools.dictPolicies import IActOnDictPolicy
from coopgraph.gridgraph import GridGraph
from coopgame.grids_graphs.pygridhandler import PyGridHandler
from coopgame.grids_graphs.pygraphhandler import PyGraphHandler
from cooptools.toggles import BooleanToggleable
import numpy as np
from cooptools.colors import Color
from coopstructs.geometry.vectors.vectorN import Vector2
from typing import Callable, Any, Dict, Type, List
import logging
from coopgame.enums import GridDrawType
from coopstructs.geometry import Line, Rectangle
import uuid
from coopstructs.geometry.curves.curves import LineCurve
from coopgraph.graphs import AStarResults
import coopgame.pygamehelpers as help
from coopgame.linedrawing.pyCurveHandler import PyCurveHandler

class MouseGridResolverArgs:
    def __init__(self,
                 windowRect: Rectangle,
                 mousePos: Vector2,
                 color: Color):
        self.windowRect = windowRect
        self.mousePos = mousePos
        self.color = color


class PathFinderFactory():
    def __init__(self,
                 grid_graph: GridGraph,
                 astar_start_point: Vector2 = None,
                 wait_timer_ms: int = None):

        if wait_timer_ms is None:
            wait_timer_ms = 0

        super().__init__()
        self.astar_start_point = astar_start_point
        self.astar_result = None
        self.grid_graph = grid_graph
        self.wait_timer_ms = wait_timer_ms
        self.start_timer = None
        self.last_calc = None

    def calculate_astar_from_cached_pos(self,
                                        new_pos: Vector2):
        self.astar_result = self.grid_graph.astar_between_grid_pos(self.astar_start_point, new_pos)
        self.last_calc = time.perf_counter()
        logging.info(f"Route calculated from {self.astar_start_point}-->{new_pos}")

    def calculate_if_passed_threshold(self, new_pos: Vector2):
        if self.last_calc is not None:
            return

        if (self.wait_timer_ms is None) or \
                (self.start_timer and time.perf_counter() - self.start_timer > self.wait_timer_ms / 1000):
            self.calculate_astar_from_cached_pos(new_pos)

    def set_astar_origin(self, grid_coords: Vector2):
        self.astar_start_point = grid_coords
        self.astar_result = None

    def set_start_timer(self):
        self.last_calc = None
        self.astar_result = None
        self.start_timer = time.perf_counter()


def astar_curves(surface_rect: Rectangle,
                 grid_graph: GridGraph,
                 astar_results: AStarResults,
                 ):
    if astar_results and astar_results.path is not None:
        astr_curves = []
        last = None
        for ii in range(0, len(astar_results.path)):
            if last is not None:
                astr_curves.append(LineCurve(str(uuid.uuid4()),
                                             grid_graph.grid.coord_from_grid_pos(last.pos, surface_rect),
                                             grid_graph.grid.coord_from_grid_pos(astar_results.path[ii].focal_point,
                                                                                 surface_rect)))
            last = astar_results.path[ii]

        return astr_curves
    else:
        return None


def toggled_grids(grid: Type[RectGrid], toggle_key):
    grid_value_array = grid.state_value_as_array(keys=[toggle_key])
    toggleds = []
    for x in range(0, grid.nColumns):
        for y in range(0, grid.nRows):
            if grid_value_array[y][x].value:
                toggleds.append(Vector2(x, y))
    return toggleds


def define_highlighted_grids(grid: RectGrid,
                             predefined_highlights: Dict[Vector2, Color] = None,
                             highlight_toggled: bool = False,
                             toggle_key: Any = None):
    highlights = {}

    if highlight_toggled and toggle_key:
        for toggled in toggled_grids(grid, toggle_key):
            highlights[toggled] = Color.ORANGE

    if predefined_highlights:
        highlights.update(predefined_highlights)

    return highlights


class PyGridGraphHandler():

    @classmethod
    def draw_calculated_path(cls,
                             grid_graph: GridGraph,
                             astar_results: AStarResults,
                             path_color: Color,
                             window_rect: Rectangle,
                             surface: pygame.Surface,
                             rotation_matrix: np.ndarray,
                             path_node_color: Color = None):

        PyCurveHandler.draw_curves({x: path_color for x in astar_curves(window_rect,
                                                                        grid_graph,
                                                                        astar_results) or []},
                                   surface,
                                   draw_scale_matrix=rotation_matrix,
                                   control_point_color=path_node_color
                                   )

    def __init__(self,
                 x: int = None,
                 y: int = None,
                 init_condition: Dict[Any, Any] = None):
        super().__init__()
        self.toggle_key = 'toggle'
        self.toggle_bool_policy = TogglePolicy(key=self.toggle_key, toggle=BooleanToggleable(default=False))
        self.show_toggled = BooleanToggleable(default=False)
        self.allow_diag = BooleanToggleable(default=True,
                                            on_toggle_callbacks=[
                                                lambda x: self.grid_graph.toggle_allow_diagonal_connections('diag'),
                                                lambda x: self.pff.set_start_timer()])

        self.grid_graph: GridGraph = None
        self.pff = None

        if x and y:
            self.init_grid(x, y, init_condition)

        self.grid_handler = PyGridHandler(screen=self.screen,
                                          grid_provider=lambda: self.grid_graph.grid,
                                          get_game_area_rect_callback=self.get
                                          )
        self.graph_handler = PyGraphHandler(self.grid_graph.graph)

        self.graph_draw_invalidated: bool = True

        self._invalidated_highlights = True
        self._cached_highlighted_static = {}
        self._predefined_highlights = {}

    def highlighted_static(self, predefined_highlights):
        # if self._invalidated_highlights:
        #     self._cached_highlighted_static = define_highlighted_grids(self.grid, predefined_highlights, self.show_toggled.value, toggle_key=self.toggle_key)
        #     self._invalidated_highlights = False
        self._cached_highlighted_static = define_highlighted_grids(self.grid, predefined_highlights,
                                                                   self.show_toggled.value, toggle_key=self.toggle_key)
        return self._cached_highlighted_static

    @property
    def grid(self):
        if self.grid_graph is not None:
            return self.grid_graph.grid

    @property
    def graph(self):
        if self.grid_graph is not None:
            return self.grid_graph.graph

    def __getitem__(self, item):
        if item is None:
            return None

        if type(item) != Vector2:
            raise TypeError(f"Type item must be Vector2. {type(item)} was provided")
        return self.grid.at(item.y, item.x)[self.toggle_key]

    def init_grid(self,
                  rows,
                  cols,
                  init_condition: np.ndarray = None,
                  path_finder_delay_ms: int = None):
        grid = RectGrid(rows, cols)

        self.grid_graph = GridGraph(grid)

        if init_condition is not None:
            for ii, row in enumerate(init_condition):
                for jj, col in enumerate(row):
                    self.grid_graph.grid.at(ii, jj).state = init_condition

        self.pff = PathFinderFactory(self.grid_graph, wait_timer_ms=path_finder_delay_ms)

    def mouse_grid_pos(self, window_rect: Rectangle, mouse_pos: Vector2, draw_scale_matrix: np.array = None):
        return self.grid_handler.get_mouse_grid_pos(window_rect,
                                                    mouse_pos,
                                                    coord_to_grid_converter=self.grid_graph.grid.grid_from_coord,
                                                    draw_scale_matrix=draw_scale_matrix)

    def redefine_grid(self, rows: int, cols: int, grid_update_callback: Callable[[Any], Any] = None):
        if rows is None or cols is None:
            return

        logging.info(f"Creating grid...")
        self.init_grid(rows, cols)
        logging.info(f"Done creating grid...")

        if grid_update_callback is not None:
            grid_update_callback(...)

    def _resolve_predefined_highlights(self,
                                       highlight_mouse_pos: MouseGridResolverArgs = None,
                                       predefined_highlights: Dict[Vector2, Color] = None,
                                       rotation_matrix=None):

        if predefined_highlights == None and highlight_mouse_pos:
            pd_highlights = {}
        else:
            pd_highlights = predefined_highlights.copy()

        if highlight_mouse_pos:
            mouse_grid = self.mouse_grid_pos(highlight_mouse_pos.windowRect, highlight_mouse_pos.mousePos,
                                             draw_scale_matrix=rotation_matrix)

            if mouse_grid is not None: pd_highlights[mouse_grid] = highlight_mouse_pos.color

        return pd_highlights

    def _define_highlighted_grids(self, predefined_highlights):
        return self.highlighted_static(predefined_highlights, highlight_toggled=self.show_toggled.value)
        # return define_highlighted_grids(grid=self.grid_graph.grid,
        #                                   predefined_highlights=predefined_highlights,
        #                                   highlight_toggled=self.show_toggled.value,
        #                                   toggle_key=self.toggle_key)

    def draw(self,
             grid_surface: pygame.Surface = None,
             graph_surface: pygame.Surface = None,
             overlay_surface: pygame.Surface = None,
             # hover_pos_surface: pygame.Surface = None,
             grid_draw_type: GridDrawType = None,
             rotation_matrix: np.ndarray = None,
             predefined_highlights: Dict[Vector2, Color] = None,
             highlight_mouse_pos: MouseGridResolverArgs = None,
             grid_color: Color = None,
             ):

        if grid_draw_type is None:
            grid_draw_type = GridDrawType.LINES

        # draw grid base
        if grid_surface:
            if grid_color is None: grid_color = Color.DIM_GRAY
            self.grid_handler.draw_base_to_surface(grid_surface,
                                                   self.grid_graph.grid,
                                                   grid_color=grid_color,
                                                   grid_draw_type=grid_draw_type,
                                                   draw_scale_matrix=rotation_matrix)

        # draw graph
        if self.grid_graph.graph and graph_surface:
            coord_converter = lambda p: Vector2.from_tuple(self.grid_graph.grid.coord_from_grid_pos(p.as_tuple(), graph_surface.get_rect()))
            self.graph_handler.draw_to_surface(graph_surface,
                                               self.grid_graph.graph,
                                               draw_scale_matrix=rotation_matrix,
                                               coordinate_converter=coord_converter)

        # draw overlay
        if overlay_surface:
            predefined_highlights = self._resolve_predefined_highlights(highlight_mouse_pos,
                                                                        predefined_highlights,
                                                                        rotation_matrix=rotation_matrix)

            highlights = self.highlighted_static(predefined_highlights)

            self.grid_handler.draw_overlay_to_surface(overlay_surface,
                                                      self.grid_graph.grid,
                                                      additional_highlight_grid_cells=highlights,
                                                      draw_scale_matrix=rotation_matrix,

                                                      )
        # if hover_pos_surface:
        #     self.redraw_hover_grid_pos_overlay(hover_grid_surface=hover_pos_surface,
        #                                        highlight_mouse_grid_pos_color=hi)

    def handle_hover_over(self, window_rect: Rectangle, grid_rotation_matrix=None):
        self.grid_handler.handle_hover_over(grid=self.grid,
                                            area_rect=window_rect,
                                            on_hover_handlers=[
                                                lambda hover: self.pff.calculate_if_passed_threshold(hover)],
                                            on_hover_changed_handlers=[lambda old, new: self.pff.set_start_timer()],
                                            draw_scale_matrix=grid_rotation_matrix)

    def redraw_graph_grid_overlay(self,
                                  grid_surface: pygame.Surface,
                                  graph_surface: pygame.Surface,
                                  overlay_surface: pygame.Surface,
                                  rotation_matrix: np.ndarray,
                                  highlight_mouse_grid_pos_color: Color = Color.AQUA,
                                  predefined_highlights: Dict[Vector2, Color] = None,
                                  path_color: Color = Color.MAGENTA,
                                  path_node_color: Color = None
                                  ):

        # Resolve params into mouse pos args
        mouse_pos_args = self._resolve_mouse_highlight_args(overlay_surface,
                                                            highlight_mouse_grid_pos_color)

        # draw graph/grid
        self.draw(grid_surface=grid_surface,
                  graph_surface=graph_surface,
                  overlay_surface=overlay_surface,
                  rotation_matrix=rotation_matrix,
                  predefined_highlights=predefined_highlights,
                  highlight_mouse_pos=mouse_pos_args
                  )

        # Draw ASTAR Lines onto overlay
        self.draw_calculated_path(grid_graph=self.grid_graph,
                                  astar_results=self.pff.astar_result,
                                  path_color=path_color,
                                  window_rect=mouse_pos_args.windowRect,
                                  surface=overlay_surface,
                                  rotation_matrix=rotation_matrix,
                                  path_node_color=path_node_color)

    def redraw_graph(self,
                     graph_surface: pygame.Surface,
                     rotation_matrix: np.ndarray,
                     ):

        # draw graph
        self.draw(graph_surface=graph_surface,
                  rotation_matrix=rotation_matrix
                  )

    def redraw_grid_overlay(self,
                            overlay_surface: pygame.Surface,
                            rotation_matrix: np.ndarray,
                            highlight_mouse_grid_pos_color: Color = Color.AQUA,
                            predefined_highlights: Dict[Vector2, Color] = None,
                            path_color: Color = Color.MAGENTA,
                            path_node_color: Color = None):

        # Resolve params into mouse pos args
        mouse_pos_args = self._resolve_mouse_highlight_args(overlay_surface,
                                                            highlight_mouse_grid_pos_color)

        # draw overlay
        self.draw(overlay_surface=overlay_surface,
                  rotation_matrix=rotation_matrix,
                  predefined_highlights=predefined_highlights,
                  highlight_mouse_pos=mouse_pos_args
                  )

        # Draw ASTAR Lines onto overlay
        self.draw_calculated_path(grid_graph=self.grid_graph,
                                  astar_results=self.pff.astar_result,
                                  path_color=path_color,
                                  window_rect=mouse_pos_args.windowRect,
                                  surface=overlay_surface,
                                  rotation_matrix=rotation_matrix,
                                  path_node_color=path_node_color)

    # def redraw_hover_grid_pos_overlay(self,
    #                                   hover_grid_surface: pygame.Surface,
    #                                   highlight_mouse_grid_pos_color: Color,
    #                                   rotation_matrix: np.ndarray):
    #     # Resolve params into mouse pos args
    #     mouse_pos_args = self._resolve_mouse_highlight_args(hover_grid_surface,
    #                                                         highlight_mouse_grid_pos_color)
    #
    #     # draw overlay
    #     self.draw(hover_pos_surface=hover_grid_surface,
    #               rotation_matrix=rotation_matrix,
    #               highlight_mouse_pos=mouse_pos_args
    #               )

    def resolve_mouse_highlight_args(self,
                                      surface: pygame.Surface,
                                      highlight_mouse_grid_pos_color: pygame.Color):
        surface_rect = surface.get_rect()
        window_rect = Rectangle.from_tuple(surface_rect)
        mouse_pos_args = MouseGridResolverArgs(window_rect,
                                               help.mouse_pos_as_vector(),
                                               color=highlight_mouse_grid_pos_color) if highlight_mouse_grid_pos_color else None
        return mouse_pos_args

    def act_on_grid(self, grid_pos: Vector2, policies=List[IActOnDictPolicy]):
        state = self.grid.act_on_grid(grid_pos.y, grid_pos.x, [self.toggle_bool_policy])
        self._invalidated_highlights = True