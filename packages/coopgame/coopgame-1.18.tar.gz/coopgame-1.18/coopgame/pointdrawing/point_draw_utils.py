from cooptools.matrixManipulation import point_transform_3d, scaled_array
import pygame
import numpy as np
from typing import List, Dict, Tuple, Callable
from dataclasses import dataclass
from cooptools.colors import Color
import cooptools.geometry_utils.vector_utils as vec

ColorGetter = Callable[[int], Color]

@dataclass(frozen=True)
class DrawPointArgs:
    color: Color | ColorGetter = None
    outline_color: Color | ColorGetter = None
    radius: int = 1
    outline_width: int = None

    def get_color(self, ii) -> Color:
        if type(self.color) == ColorGetter:
            return self.color(ii)
        return self.color

    def get_outline_color(self, ii) -> Color:
        if type(self.outline_color) == ColorGetter:
            return self.outline_color(ii)
        return self.outline_color

def draw_points(points: Dict[Tuple[int, int], DrawPointArgs],
                surface: pygame.Surface,
                vec_transformer: vec.VecTransformer = None):

    pt_args = [(k, v) for k, v in points.items()]

    # update the points based on the arg transformer
    scaled = vec.resolve_vec_transformed_points(
        points=[x[0] for x in pt_args],
    vec_transformer=vec_transformer)

    for ii, x in enumerate(pt_args):
        args = x[1]
        if args.color:


            pygame.draw.circle(surface,
                               args.get_color(ii).value,
                               center=tuple(scaled[ii][:2]),
                               radius=args.radius,
                               )

        if args.outline_color:
            olw = args.outline_width if args.outline_width is not None else 1
            pygame.draw.circle(surface,
                               args.get_outline_color(ii).value,
                               center=tuple(scaled[ii][:2]),
                               width=olw,
                               radius=args.radius,
                               )