import pygame
from cooptools.colors import Color
from typing import List, Dict, Callable
from coopstructs.geometry.curves.curves import Curve
from coopstructs.geometry import Line, PolygonRegion
import numpy as np
from shapely.geometry import LineString
import coopgame.pygamehelpers as help
from dataclasses import dataclass
import coopgame.linedrawing.line_draw_utils as lutils
import coopgame.pointdrawing.point_draw_utils as putils
import cooptools.matrixManipulation as mm
import cooptools.geometry_utils.vector_utils as vec
from cooptools.common import flattened_list_of_lists

@dataclass(frozen=True)
class CurveDrawArgs:
    line_args: lutils.DrawLineArgs = None
    control_point_args: putils.DrawPointArgs = None
    control_line_args: lutils.DrawLineArgs = None
    buffer: int = None
    buffer_color: Color = None
    resolution: int = 30

    @property
    def BaseArgs(self):
        return CurveDrawArgs(
            line_args=self.line_args.BaseArgs,
            resolution=self.resolution
        )

    @property
    def OverlayArgs(self):
        return CurveDrawArgs(
            control_point_args=self.control_point_args,
            control_line_args=self.control_line_args
        )

    @property
    def BufferArgs(self):
        return CurveDrawArgs(
            buffer=self.buffer,
            buffer_color=self.buffer_color,
        )

def draw_curves(curves: Dict[Curve, CurveDrawArgs],
                surface: pygame.Surface,
                vec_transformer: vec.VecTransformer = None):

    line_reps = {curve: (args, curve.line_representation(resolution=args.resolution)) for curve, args in curves.items() if args.line_args}
    flat_line_reps = flattened_list_of_lists([[(arg_linereps[0], line) for line in arg_linereps[1]] for curve, arg_linereps in line_reps.items()])

    # Draw Lines
    lutils.draw_lines(
        lines={line: args for args, line in flat_line_reps},
        surface=surface,
        vec_transformer=vec_transformer
    )

    for curve, args in curves.items():
        # draw control lines
        if args.control_line_args:
            lutils.draw_lines(
                {x: args.control_line_args for x in curve.ControlLines},
                surface=surface,
                vec_transformer=vec_transformer
            )

        # draw control points
        if args.control_point_args:
            putils.draw_points(
                points={
                    x.as_tuple(): args.control_point_args for x in curve.ControlPoints
                },
                surface=surface,
                vec_transformer=vec_transformer
            )

        # draw buffer
        if args.buffer_color:
            line = LineString([
                line_reps[curve][1].origin] +
                [x.destination for x in line_reps[curve][1]]
            )

            dilated = line.buffer(args.buffer)
            poly = PolygonRegion.from_shapely_polygon(dilated)
            buffer_color = Color.GREEN if args.buffer_color is None else args.buffer_color
            help.draw_polygon(surface, [x.as_tuple() for x in poly.boundary_points], buffer_color)


    # for curve, args in curves.items():
    #     line_rep = curve.line_representation(resolution=args.resolution)
    #
    #     if args.buffer_color:
    #         line = LineString([
    #             line_rep[0].origin] +
    #             [x.destination for x in line_rep]
    #         )
    #
    #         dilated = line.buffer(args.buffer)
    #         poly = PolygonRegion.from_shapely_polygon(dilated)
    #         buffer_color = Color.GREEN if args.buffer_color is None else args.buffer_color
    #         help.draw_polygon(surface, [x.as_tuple() for x in poly.boundary_points], buffer_color)
    #
    #     if args.control_line_args:
    #         lutils.draw_lines(
    #             {x: args.control_line_args for x in curve.ControlLines},
    #             surface=surface,
    #             vec_transformer=vec_transformer
    #         )
    #
    #     lutils.draw_lines(
    #         lines={x: args.line_args for x in line_rep},
    #         surface=surface,
    #         vec_transformer=vec_transformer
    #     )
    #
    #     if args.control_point_args:
    #         putils.draw_points(
    #             points={
    #                 x.as_tuple(): args.control_point_args for x in curve.ControlPoints
    #             },
    #             surface=surface,
    #             vec_transformer=vec_transformer
    #         )