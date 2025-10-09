from cooptools.colors import Color
import pygame
from coopgraph.graphs import Graph, Edge, Node
from coopstructs.geometry.vectors.vectorN import Vector2
from coopstructs.geometry import Rectangle
import coopgame.pygamehelpers as help
from typing import Callable, Tuple, Dict, Iterable
from coopstructs.geometry.curves.curves import LineCurve, Curve
from cooptools.coopEnum import Directionality
from dataclasses import dataclass, asdict
import numpy as np
from coopgame.pointdrawing import point_draw_utils as putils
from coopgame.label_drawing import label_drawing_utils as lutils
from coopgame.linedrawing import line_draw_utils as nutils
from coopstructs.geometry.lines import Line
import cooptools.matrixManipulation as mm
import cooptools.geometry_utils.vector_utils as vec
from cooptools.common import flattened_list_of_lists
from coopgame.surfaceManager import SurfaceGroup

@dataclass(frozen=True)
class RouteDrawArgs:
    id: str
    route: Iterable[Edge]
    edge_draw_args: nutils.DrawLineArgs = None
    node_draw_args: putils.DrawPointArgs = None
    node_label_args: lutils.DrawLabelArgs = None

    @property
    def Nodes(self):
        if self.route is None:
            return []

        return flattened_list_of_lists([[x.start, x.end] for x in self.route], unique=True)

@dataclass(frozen=True)
class GraphDrawArgs:
    node_draw_args: putils.DrawPointArgs = None
    enabled_edge_args: nutils.DrawLineArgs = None
    disabled_edge_args: nutils.DrawLineArgs = None
    node_label_args: lutils.DrawLabelArgs = None
    articulation_points_args: putils.DrawPointArgs = None
    source_node_args: putils.DrawPointArgs = None
    sink_node_args: putils.DrawPointArgs = None
    orphan_node_args: putils.DrawPointArgs = None

    def with_(self, **kwargs):
        definition = self.__dict__
        for kwarg, val in kwargs.items():
            definition[kwarg] = val

        return type(self)(**definition)

    @classmethod
    def from_(cls, args, **kwargs):
        kw = asdict(args)
        kw.update(kwargs)
        return GraphDrawArgs(**kw)

    @property
    def EdgesBaseArgs(self):
        return GraphDrawArgs(
            enabled_edge_args=self.enabled_edge_args.BaseArgs,
            disabled_edge_args=self.disabled_edge_args.BaseArgs
        )

    @property
    def EdgesLabelArgs(self):
        return GraphDrawArgs(
            enabled_edge_args=self.enabled_edge_args,
            disabled_edge_args=self.disabled_edge_args
        )

    @property
    def NodesBaseArgs(self):
        return GraphDrawArgs(
            node_draw_args=self.node_draw_args
        )

    @property
    def NodesLabelArgs(self):
        return GraphDrawArgs(
            node_label_args=self.node_label_args
        )

    @property
    def OverlayArgs(self):
        return GraphDrawArgs(
            articulation_points_args=self.articulation_points_args,
            source_node_args=self.source_node_args,
            sink_node_args=self.sink_node_args,
            orphan_node_args=self.orphan_node_args
        )


def get_node_label_surface_group(
    graph: Graph,
    args: GraphDrawArgs,
    vec_transformer: vec.VecTransformer = None
) -> SurfaceGroup:
    positions = {x.name: vec.resolve_vec_transformed_points([x.pos], vec_transformer)[0][:2] for x in graph.nodes}

    return lutils.label_surface_group(
        labels={x.name: x.name for x in graph.nodes},
        draw_label_args=args.node_label_args,
        positions=positions
    )

def get_edge_label_surface_group(
    graph: Graph,
    args: GraphDrawArgs,
    vec_transformer: vec.VecTransformer = None
) -> SurfaceGroup:
    positions = {x.id: vec.resolve_vec_transformed_points(points=[vec.interpolate(x.start.pos, x.end.pos)],
                                                          vec_transformer=vec_transformer)[0][:2]
                 for x in graph.edges}

    return lutils.label_surface_group(
        labels={x.id: str(x) for x in graph.edges},
        draw_label_args={x.id: args.enabled_edge_args.draw_label_args
        if x.enabled else args.disabled_edge_args.draw_label_args
                         for x in graph.edges},
        positions=positions
    )

def draw_to_surface(surface: pygame.Surface,
                    graph: Graph,
                    args: GraphDrawArgs = None,
                    routes: Iterable[RouteDrawArgs] = None,
                    vec_transformer: vec.VecTransformer = None):
    if graph is None:
        return

    if args is not None and (args.enabled_edge_args or args.disabled_edge_args):
        _draw_edges(
            surface=surface,
            edge_draw_args={
                e: args.enabled_edge_args if e.enabled() else args.disabled_edge_args for e in graph.edges
            },
            vec_transformer=vec_transformer
        )

    if args is not None and (args.node_draw_args or args.node_label_args):
        draw_graph_nodes(surface,
                         nodes=graph.nodes,
                         node_draw_args=args.node_draw_args,
                         vec_transformer=vec_transformer,
                         draw_label_args=args.node_label_args)

    if routes is not None:
        draw_routes(
            surf=surface,
            routes=routes,
            vec_transformer=vec_transformer
        )


    if args is not None and args.articulation_points_args:
        putils.draw_points(
            points={x.pos: args.articulation_points_args for x in graph.AP()},
            surface=surface,
            vec_transformer=vec_transformer
        )

    if args is not None and args.source_node_args:
        putils.draw_points(
            points={x.pos: args.source_node_args for x in graph.Sources},
            surface=surface,
            vec_transformer=vec_transformer
        )

    if args is not None and args.sink_node_args:
        putils.draw_points(
            points={x.pos: args.sink_node_args for x in graph.Sinks},
            surface=surface,
            vec_transformer=vec_transformer
        )

    if args is not None and args.orphan_node_args:
        putils.draw_points(
            points={x.pos: args.orphan_node_args for x in graph.Orphans},
            surface=surface,
            vec_transformer=vec_transformer
        )
def _draw_edges(
    surface: pygame.Surface,
    edge_draw_args: Dict[Edge, nutils.DrawLineArgs],
    vec_transformer: vec.VecTransformer = None
):
    line_args = {Line(Vector2.from_tuple(k.start.pos),
                      Vector2.from_tuple(k.end.pos)): v.with_(label_text=str(k))
                 for k, v in edge_draw_args.items() if k.start.pos != k.end.pos}

    nutils.draw_lines(lines=line_args,
                      surface=surface,
                      vec_transformer=vec_transformer
                      )

def draw_graph_nodes(surface: pygame.Surface,
                     nodes: Iterable[Node],
                     node_draw_args: putils.DrawPointArgs = None,
                     draw_label_args: lutils.DrawLabelArgs = None,
                     vec_transformer: vec.VecTransformer = None):
    txt_dict = {}
    for node in nodes:
        if node_draw_args:
            putils.draw_points({node.pos: node_draw_args},
                               surface=surface,
                               vec_transformer=vec_transformer)


        scaled = vec.resolve_vec_transformed_points([node.pos], vec_transformer=vec_transformer)[0]
        txt_dict.setdefault(scaled, []).append(node.name)


    if draw_label_args:
        for pos, labels in txt_dict.items():
            lutils.draw_label(
                hud=surface,
                args=lutils.LabelArgs(
                    text=",".join(labels),
                    draw_args=draw_label_args,
                    pos=pos
                )
            )

def draw_articulation_points(surface: pygame.Surface,
                             graph: Graph,
                             color: Color = None,
                             vec_transformer: vec.VecTransformer = None
                             ):
    if graph is None:
        return

    articulation_points = graph.AP()

    if color is None:
        color = Color.ORANGE


    scaled_pos = vec.resolve_vec_transformed_points(points=[node.pos for node in articulation_points.keys()],
                                                    vec_transformer=vec_transformer)

    for point in scaled_pos:
        pygame.draw.circle(surface, color.value, (int(point[0]), int(point[1])), 10, 1)

def draw_directionality_indicators(curves: Dict[Curve, Directionality],
                                   surface: pygame.Surface,
                                   indicator_color: Color,
                                   num_arrows: int = 5,
                                   size: float = 1,
                                   indicator_points_color: Color | Tuple[Color, ...]=None,
                                   vec_transformer: vec.VecTransformer = None):
    arrow_ts = [1.0 / (num_arrows - 1) * x for x in range(0, num_arrows)] if num_arrows > 1 else [0.5]


    for curve, direction in curves.items():
        for t in arrow_ts:
            centre = curve.point_at_t(t)

            try:
                # get derivative of curve for drawing
                derivative = curve.derivative_at_t(t)
                d_unit = derivative.unit()
            except:
                # most likely a vertical curve (no derivative), handle by pointing up or down.
                d_unit = (curve.EndPoint - curve.origin).unit()

            if d_unit is None or d_unit.y == 0:
                continue

            d_foreward = d_unit.scaled_to_length(size)
            d_ort_1 = Vector2(1, - d_unit.x / d_unit.y).scaled_to_length(size / 2)
            # d_ort_2 = d_ort_1 * -1

            a = b = c = d = e = f = None
            if direction in [Directionality.FOREWARD, Directionality.BIDIRECTIONAL]:
                a = centre
                b = centre - d_foreward + d_ort_1
                c = centre - d_foreward - d_ort_1

                scaled_polygon_points = vec.resolve_vec_transformed_points(points=[a.as_tuple(), b.as_tuple(), c.as_tuple()],
                                                                           vec_transformer=vec_transformer)

                help.draw_polygon(surface, scaled_polygon_points, color=indicator_color)

            if direction in [Directionality.BACKWARD, Directionality.BIDIRECTIONAL]:
                d = centre
                e = centre + d_foreward + d_ort_1
                f = centre + d_foreward - d_ort_1

                scaled_polygon_points = vec.resolve_vec_transformed_points(points=[d.as_tuple(), e.as_tuple(), f.as_tuple()],
                                                                           vec_transformer=vec_transformer)

                help.draw_polygon(surface, scaled_polygon_points, color=indicator_color)

            ip_color_getter = lambda ii: indicator_points_color[ii % len(indicator_points_color)] \
                if type(indicator_points_color) == tuple \
                else indicator_points_color

            if indicator_points_color:
                points = [a, b, c, d, e, f]
                putils.draw_points(
                    points={
                        x.as_tuple(): putils.DrawPointArgs(
                            color=ip_color_getter,
                            outline_color=None,
                            radius=2
                        ) for ii, x in enumerate(points)
                    },
                    surface=surface,
                    vec_transformer=vec_transformer
                )

def draw_routes(
        surf: pygame.Surface,
        routes: Iterable[RouteDrawArgs],
        vec_transformer: vec.VecTransformer = None
):
    if routes is None:
        return

    for route in routes:
        if route.route is None:
            continue

        _draw_edges(surface=surf,
                    edge_draw_args={e: route.edge_draw_args for e in route.route},
                    vec_transformer=vec_transformer)
        draw_graph_nodes(
            surface=surf,
            nodes=route.Nodes,
            node_draw_args=route.node_draw_args,
            draw_label_args=route.node_label_args,
            vec_transformer=vec_transformer
        )