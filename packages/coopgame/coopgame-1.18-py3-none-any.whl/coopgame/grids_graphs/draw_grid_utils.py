import time

from cooptools.sectors.grids import RectGrid
from cooptools.coopEnum import CardinalPosition
from coopstructs.geometry import Rectangle
import pygame
from cooptools.colors import Color
from typing import Dict, Tuple, List, Iterable, Callable
from coopgame.enums import GridDrawType
import coopgame.pygamehelpers as help
from coopstructs.geometry.vectors.vectorN import Vector2
from cooptools.sectors.rect_utils import sector_from_coord
from dataclasses import dataclass
import numpy as np
import coopgame.linedrawing.line_draw_utils as ldu
from coopstructs.geometry.lines import Line
from coopgame.gameTemplate import tt
from cooptools.decor import timer
import logging
import cooptools.matrixManipulation as mm
import cooptools.geometry_utils.vector_utils as vec

logger = logging.getLogger('coopgame.draw_grid_utils')

@dataclass(frozen=True)
class GridDrawArgs:
    grid_draw_type: GridDrawType = None
    grid_color: Color = None
    margin: int = 0
    center_guide_color: Color = None
    hover_color: Color = None
    crosshairs_color: Color = None

def draw_to_surface(
        surface: pygame.Surface,
        grid: RectGrid,
        grid_draw_type: GridDrawType = None,
        grid_color: Color = None,
        margin: int = 0,
        center_guide_color: Color = None,
        highlights: Dict[Vector2, Color] = None,
        hover: Tuple[Vector2, Color] = None,
        toggled_key_colors: Dict[str, Color] = None,
        outlined_grid_cells: Dict[Vector2, Color] = None,
        highlight_rows: Dict[int, Color] = None,
        highlight_cols: Dict[int, Color] = None,
        crosshairs_color: Color = None,
        vec_transformer: vec.VecTransformer = None
):
    if grid is None:
        return

    if grid_color is not None:
        _draw_grid(
            grid=grid,
            surf=surface,
            grid_draw_type=grid_draw_type,
            grid_color=grid_color,
            margin=margin,
            vec_transformer=vec_transformer
        )


    highlights = _resolve_highlights(
        grid=grid,
        toggled_key_colors=toggled_key_colors,
        hover=hover,
        rows=highlight_rows,
        cols=highlight_cols,
        center_guide_color=center_guide_color,
        crosshairs_color=crosshairs_color,
        additional_highlight_grid_cells=highlights
    )

    grid_box_rect = grid_box_rectangle_at_pos(surface.get_width(), surface.get_height(), grid, margin)
    _draw_highlighted_grids(surface,
                            grid=grid,
                            vec_transformer=vec_transformer,
                            highlights=highlights)


    _draw_outlined_grids(surface=surface
                         , grid_box_rect=grid_box_rect
                         , outlined_grid_cells=outlined_grid_cells
                         , margin=margin
                         , vec_transformer=vec_transformer)


@timer(logger=logger, time_tracking_class=tt)
def _draw_grid(
        grid: RectGrid,
        surf: pygame.Surface,
        grid_draw_type: GridDrawType = None,
        grid_color: Color = None,
        margin: int = 1,
        vec_transformer: vec.VecTransformer = None
):
    if grid_draw_type is None:
        grid_draw_type = GridDrawType.LINES

    if grid_color is None:
        grid_color = Color.DARK_GREY

    if grid_draw_type == GridDrawType.BOXES:
        _draw_grid_boxes(surface=surf,
                         grid=grid,
                         margin=margin,
                         grid_color=grid_color,
                         vec_transformer=vec_transformer)
    elif grid_draw_type == GridDrawType.LINES:
        _draw_grid_lines(surface=surf,
                         grid=grid,
                         margin=margin,
                         grid_color=grid_color,
                         vec_transformer=vec_transformer)

@timer(logger=logger, time_tracking_class=tt)
def _resolve_highlights(grid: RectGrid,
                        toggled_key_colors: Dict[str, Color] = None,
                        hover: Tuple[Vector2, Color] = None,
                        rows: Dict[int, Color] = None,
                        cols: Dict[int, Color] = None,
                        center_guide_color: Color = None,
                        crosshairs_color: Color = None,
                        additional_highlight_grid_cells: Dict[Vector2, Color] = None
                        ):
    ret = {}

    if hover is not None and crosshairs_color is not None:
        rows[hover[0].x] = crosshairs_color
        cols[hover[0].y] = crosshairs_color

    highligted_rc = _rc_highlight_definition(
        grid=grid,
        rows=rows,
        cols=cols,
        center_guide_color=center_guide_color,
    )
    ret = {**ret, **highligted_rc}

    if additional_highlight_grid_cells:
        ret = {**ret, **additional_highlight_grid_cells}

    if toggled_key_colors:
        for k, color in toggled_key_colors.items():
            toggled_highlights = _toggled_highlighted_grids(
                grid=grid,
                toggle_key=k,
                color=color
            )

            ret = {**ret, **toggled_highlights}

    if hover:
        ret[hover[0]] = hover[1]

    return ret

@timer(logger=logger, time_tracking_class=tt)
def _rc_highlight_definition(
        grid: RectGrid,
        rows: Dict[int, Color] = None,
        cols: Dict[int, Color] = None,
        center_guide_color: Color = None,
) -> Dict[Vector2, Color]:
    highlights = {}

    if rows is None:
        rows = {}
    if cols is None:
        cols = {}
    if center_guide_color:
        rs, cs = define_center_grids(grid, color=center_guide_color)
        rows = {**rows, **rs}
        cols = {**cols, **cs}

    row_highlights = {Vector2(r, c): color for r, color in rows.items() for c in range(0, grid.nColumns)}
    col_highlights = {Vector2(r, c): color for r in range(0, grid.nRows) for c, color in cols.items()}
    highlights.update(col_highlights)
    highlights.update(row_highlights)
    return highlights

@timer(logger=logger, time_tracking_class=tt)
def define_center_grids(grid: RectGrid,
                        color: Color) -> Tuple[Dict[int, Color], Dict[int, Color]]:
    if grid.nRows % 2 == 0:
        center_rows = [grid.nRows // 2 - 1, grid.nRows // 2]
    else:
        center_rows = [((grid.nRows - 1) // 2)]

    if grid.nColumns % 2 == 0:
        center_cols = [grid.nColumns // 2 - 1, grid.nColumns // 2]
    else:
        center_cols = [((grid.nColumns - 1) // 2)]

    return ({x: color for x in center_rows}, {x: color for x in center_cols})


# @timer
def _draw_outlined_grids(surface: pygame.Surface,
                         grid_box_rect: Rectangle,
                         margin=0,
                         outlined_grid_cells: Dict[Vector2, Color] = None,
                         vec_transformer: vec.VecTransformer = None):

    if vec_transformer is not None:
        raise ValueError("Draw grid outlines does not support a transform")

    if outlined_grid_cells is None or len(outlined_grid_cells) == 0:
        return

    for grid_pos, color in outlined_grid_cells.items():
        if color is None:
            color = Color.YELLOW

        rect = Rectangle.from_tuple(((margin + grid_box_rect.width) * grid_pos.x + margin
                                     , (margin + grid_box_rect.height) * grid_pos.y + margin
                                     , grid_box_rect.height
                                     , grid_box_rect.width))
        my_image = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(my_image, color.value, my_image.get_rect(), 3)
        surface.blit(my_image, (rect.x, rect.y))

@timer(logger=logger, time_tracking_class=tt)
def _toggled_highlighted_grids(grid: RectGrid,
                              toggle_key: str,
                              color: Color) -> Dict[Vector2, Color]:
    highlights = {}

    if toggle_key in grid.GridKeys:
        grid_value_array = grid.state_value_as_array(key=toggle_key)
        for x in range(0, grid.nColumns):
            for y in range(0, grid.nRows):
                if grid_value_array[y][x].value:
                    highlights[Vector2(y, x)] = color

    return highlights

@timer(logger=logger, time_tracking_class=tt)
def _scaled_rect_points(rects: List[Rectangle],
                        vec_transformer: vec.VecTransformer = None):
    points = []
    for rect in rects:
        [points.append(x) for x in rect.Corners]

    scaled = points
    if vec_transformer is not None:
        scaled = vec_transformer(points)

    ret = []
    for ii in range(0, len(scaled), 4):
        ret.append(scaled[ii: ii+4])

    return ret

@timer(logger=logger, time_tracking_class=tt)
def _rect_at_pos(
    surface: pygame.Surface,
    grid: RectGrid,
    highlights: Dict[Vector2, Color],
    margin: int = 0
):
    pos_rects = [
        (grid_pos, grid_box_rectangle_at_pos(
                width=surface.get_width(),
                height=surface.get_height(),
                grid=grid,
                margin=margin,
                grid_pos=grid_pos))
        for grid_pos in highlights.keys()
    ]
    return pos_rects


@timer(logger=logger, time_tracking_class=tt)
def _draw_highlighted_grids(surface: pygame.Surface,
                            grid: RectGrid,
                            highlights: Dict[Vector2, Color],
                            vec_transformer: vec.VecTransformer = None,
                            margin: int = 0):
    pos_rects = _rect_at_pos(
        surface=surface,
        grid=grid,
        highlights=highlights,
        margin=margin
    )

    scaled_rects = _scaled_rect_points(
        rects=[x[1] for x in pos_rects],
        vec_transformer=vec_transformer
    )

    _draw_plygons(
        pos_rects,
        surface,
        scaled_rects,
        highlights
    )
    # for ii, x in enumerate(pos_rects):
    #     help.draw_polygon(surface, scaled_rects[ii], highlights[x[0]])

@timer(logger=logger, time_tracking_class=tt)
def _draw_plygons(pos_rects,
                  surface,
                  scaled_rects,
                  highlights):
    for ii, x in enumerate(pos_rects):
        help.draw_polygon(surface, scaled_rects[ii], highlights[x[0]])


# @timer
def _draw_grid_boxes(surface: pygame.Surface,
                     grid: RectGrid,
                     margin=0,
                     grid_color: Color = None,
                     vec_transformer: vec.VecTransformer = None):

    for y in range(0, grid.nRows):
        for x in range(0, grid.nColumns):
            grid_box_rect = grid_box_rectangle_at_pos(
                width=surface.get_width(),
                height=surface.get_height(),
                grid=grid,
                grid_pos=Vector2(x, y),
                margin=margin)
            points = help.scaled_points_of_a_rect(
                rect=grid_box_rect,
                vec_transformer=vec_transformer)[:, :2]
            help.draw_polygon(surface, list(points), grid_color)


# @timer
def _draw_grid_lines(surface: pygame.Surface,
                     grid: RectGrid,
                     margin=0,
                     grid_color: Color = None,
                     vec_transformer: vec.VecTransformer = None):
    grid_box_rect = grid_box_rectangle_at_pos(
        width=surface.get_width(),
        height=surface.get_height(),
        grid=grid,
        grid_pos=Vector2(0, 0),
        margin=margin)

    '''Draw each line'''
    lines = []

    for x in range(0, grid.nColumns + 1):
        point_x1 = x * (grid_box_rect.width + margin)
        point_y1 = 0
        point_x2 = x * (grid_box_rect.width + margin)
        point_y2 = (grid_box_rect.height + margin) * grid.nRows
        lines.append(Line(
            origin=(point_x1, point_y1),
            destination=(point_x2, point_y2),
        ))
    for y in range(0, grid.nRows + 1):
        s = (0, y * (grid_box_rect.height + margin))
        e = ((grid_box_rect.width + margin) * grid.nColumns, y * (grid_box_rect.height + margin))
        lines.append(Line(
            origin=s,
            destination=e
        ))

    ldu.draw_lines(
        lines={x: ldu.DrawLineArgs(
            color=grid_color) for x in lines},
        surface=surface,
        vec_transformer=vec_transformer
    )

# @timer
def get_mouse_grid_pos(grid: RectGrid,
                       game_area_rect: Rectangle,
                       mouse_pos: Vector2,
                       vec_transformer: vec.VecTransformer = None,
                       inv_vec_transformer: vec.VecTransformer = None
                       ):

    """Gets the mouse position and converts it to a grid position"""
    mouse_game_area_coord = help.game_area_coords_from_parent_coords(parent_coords=mouse_pos, game_area_surface_rectangle=game_area_rect)
    mouse_over_grid_coords = help.viewport_point_on_plane(
        mouse_game_area_coord,
        game_area_rect,
        vec_transformer=vec_transformer,
    )

    if inv_vec_transformer is not None:
        mouse_over_grid_coords = inv_vec_transformer([mouse_over_grid_coords])[0]


    grid_pos = sector_from_coord(coord=mouse_over_grid_coords[:2],
                                 sector_def=(grid.nRows, grid.nColumns),
                                 area_dims=game_area_rect.as_tuple()[2:4]
                                 )

    return grid_pos


def get_mouse_grid_rect(grid: RectGrid,
                        game_area_rect: Rectangle,
                        mouse_pos: Vector2,
                        vec_transformer: vec.VecTransformer = None,
                        inv_vec_transformer: vec.VecTransformer = None
                        ):
    mouse_grid_pos = get_mouse_grid_pos(
        grid=grid,
        game_area_rect=game_area_rect,
        mouse_pos=mouse_pos,
        vec_transformer=vec_transformer,
        inv_vec_transformer=inv_vec_transformer
    )

    return grid.grid_rect_at_pos(
        grid_pos=mouse_grid_pos,
        area_wh=(game_area_rect.width, game_area_rect.height)
    )

# @timer
def grid_point_to_viewport_point(surface: pygame.Surface,
                                 grid,
                                 grid_pos: Vector2,
                                 grid_point_type: CardinalPosition = CardinalPosition.CENTER,
                                 margin: int = 0,
                                 vec_transformer: vec.VecTransformer = None):
    grid_box_rect = grid_box_rectangle_at_pos(
        width=surface.get_width(),
        height=surface.get_height(),
        grid=grid,
        margin=margin,
        grid_pos=grid_pos
    )

    grid_box_scaled_points = help.scaled_points_of_a_rect(grid_box_rect,
                                                          vec_transformer=vec_transformer)

    if grid_point_type == CardinalPosition.CENTER:
        x = sum(point[0] for point in grid_box_scaled_points) / len(grid_box_scaled_points)
        y = sum(point[1] for point in grid_box_scaled_points) / len(grid_box_scaled_points)
        return Vector2(x, y)
    elif grid_point_type == CardinalPosition.ORIGIN:
        return Vector2(grid_box_scaled_points[0][0], grid_box_scaled_points[0][1])
    else:
        raise NotImplementedError(f"Unimplemented grid_point_type {grid_point_type}")

def grid_box_rectangle_at_pos(width,
                              height,
                              grid: RectGrid,
                              margin: int = 0,
                              grid_pos: Vector2 = None
                              ) -> Rectangle:
    if grid_pos is None:
        grid_pos = Vector2(0, 0)

    grid_box_height = height / grid.nRows
    grid_box_width = width / grid.nColumns

    # get basic grid pos rect at grid_pos
    rect = Rectangle.from_tuple((grid_pos.y * grid_box_width,
                                 grid_pos.x * grid_box_height,
                                 grid_box_width,
                                 grid_box_height))

    # add the margin
    rect = rect.with_margin(margin=margin)


    return rect

if __name__ == "__main__":

    grid = RectGrid(100, 100)
    rect = Rectangle.from_tuple((0, 0, 500, 1000))
    n=0
    t0 = time.perf_counter()
    while True:
        get_mouse_grid_pos(
            grid=grid,
            game_area_rect=rect,
            mouse_pos=Vector2(10, 10),
            draw_transform_matrix=None
        )
        n+=1
        print(n)
        t1 = time.perf_counter()
        if t1-t0 > 10:
            break