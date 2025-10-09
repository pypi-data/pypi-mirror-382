from cooptools.matrixManipulation import point_transform_3d, scaled_array
from coopstructs.geometry import Line
import pygame
import numpy as np
from typing import List, Dict
from dataclasses import dataclass, asdict
from cooptools.colors import Color
import coopgame.pointdrawing.point_draw_utils as putils
import coopgame.label_drawing.label_drawing_utils as lutils
from cooptools.coopEnum import Directionality
import coopgame.pygamehelpers as help
from cooptools.coopEnum import CoopEnum, auto
from cooptools.common import property_name
import cooptools.matrixManipulation as mm
import cooptools.geometry_utils.vector_utils as vec

class DirectionalityIndicatorType(CoopEnum):
    ALONG = auto()
    END = auto()

@dataclass(frozen=True)
class DirectionalityIndicatorDrawArgs:
    color: Color = None
    height: int = 10
    width: int = 10
    direction: Directionality = None

@dataclass(frozen=True)
class DrawLineArgs:
    color: Color = None
    width: int = None
    control_point_args: putils.DrawPointArgs = None
    directionality_draw_args: DirectionalityIndicatorDrawArgs = None
    draw_label_args: lutils.DrawLabelArgs = None
    label_text: str = None
    buffer_color: Color = None

    def __post_init__(self):
        if type(self.draw_label_args) == dict:
            object.__setattr__(self, 'draw_label_args', lutils.DrawLabelArgs(**self.draw_label_args))
        if type(self.control_point_args) == dict:
            object.__setattr__(self, 'control_point_args', putils.DrawPointArgs(**self.control_point_args))
        if type(self.directionality_draw_args) == dict:
            object.__setattr__(self, 'directionality_draw_args', DirectionalityIndicatorDrawArgs(**self.directionality_draw_args))

    def with_(self, **kwargs):
        kw = asdict(self)
        kw.update(kwargs)
        return DrawLineArgs(**kw)

    @property
    def BaseArgs(self):
        return DrawLineArgs(
            color=self.color,
            width=self.width,
            directionality_draw_args = self.directionality_draw_args,
        )

    def get_label_args(self,
                       line: Line,
                       vec_transformer: vec.VecTransformer = None) -> lutils.LabelArgs:
        adjusted = vec.resolve_vec_transformed_points(
            points=[line.origin, line.destination],
            vec_transformer=vec_transformer
        )

        return lutils.LabelArgs(
            draw_args=self.draw_label_args,
            pos=((adjusted[0][0] + adjusted[1][0]) / 2, (adjusted[0][1] + adjusted[1][1]) / 2),
            text=self.label_text
        )

    @property
    def OverlayArgs(self):
        return DrawLineArgs(
            control_point_args=self.control_point_args
        )

def draw_lines(lines: Dict[Line, DrawLineArgs],
               surface: pygame.Surface,
               vec_transformer: vec.VecTransformer = None):
    for line, args in lines.items():
        if args is None:
            continue

        # update the points based on the arg transformer
        adjusted = vec.resolve_vec_transformed_points(
            points=[line.origin, line.destination],
            vec_transformer=vec_transformer
        )

        # Draw the lines
        if args.color:
            w = args.width if args.width is not None else 1
            pygame.draw.line(surface,
                             args.color.value,
                             (adjusted[0][0], adjusted[0][1]),
                             (adjusted[1][0], adjusted[1][1]),
                             width=w)

        # Draw the points
        if args.control_point_args:
            putils.draw_points(
                points={
                    (x[0], x[1]): args.control_point_args for x in adjusted
                },
                surface=surface,
                vec_transformer=vec_transformer
            )

        # Draw Directionality
        if args.directionality_draw_args:
            help.draw_arrow(surface=surface,
                            color=args.directionality_draw_args.color,
                            start=(adjusted[0][0], adjusted[0][1]),
                            end=(adjusted[1][0], adjusted[1][1]),
                            arrow_height=args.directionality_draw_args.height,
                            arrow_width=args.directionality_draw_args.width)

        # Draw Label
        if args.draw_label_args is not None and args.label_text is not None:
            lutils.draw_label(hud=surface,
                              args=args.get_label_args(
                                  line=line,
                                  vec_transformer=vec_transformer
                              ))