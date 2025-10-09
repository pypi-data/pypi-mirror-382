from cooptools.colors import Color
import pygame
from coopgraph.graphs import Graph, AStarResults, Node, Edge
import coopgame.pygamehelpers as help
from typing import List, Callable, Iterable
import coopgame.grids_graphs.draw_graph_utils as utils
import coopgame.linedrawing.line_draw_utils as lutils
import coopgame.label_drawing.label_drawing_utils as labutils
from cooptools.coopEnum import CoopEnum
from coopgame.surfaceManager import SurfaceManager, SurfaceRegistryArgs, SurfaceGroup
import coopgame.pointdrawing.point_draw_utils as putils
import cooptools.geometry_utils.vector_utils as vec
import logging

logger = logging.getLogger(__name__)

class GraphSurfaceType(CoopEnum):
    EDGES_SURFACE_ID = 'EDGES_SURFACE_ID'
    NODES_SURFACE_ID = 'NODES_SURFACE_ID'
    NODE_LABELS_SURFACE_ID = 'NODE_LABELS_SURFACE_ID'
    EDGE_LABELS_SURFACE_ID = 'EDGE_LABELS_SURFACE_ID'
    OVERLAY_SURFACE_ID = 'OVERLAY_SURFACE_ID'
    ROUTES_SURFACE_ID = 'ROUTES_SURFACE_ID'
    NODE_LABELS_SURFACE_GROUP_ID = 'NODE_LABELS_SURFACE_GROUP_ID'
    EDGE_LABELS_SURFACE_GROUP_ID = 'EDGE_LABELS_SURFACE_GROUP_ID'

DEFAULT_DRAW_CONFIG = utils.GraphDrawArgs(
            node_draw_args=putils.DrawPointArgs(
                color=Color.DARK_BLUE,
                radius=5,
            ),
            enabled_edge_args=lutils.DrawLineArgs(
                color=Color.ORANGE,
                directionality_draw_args=lutils.DirectionalityIndicatorDrawArgs(
                    color=Color.ORANGE,
                    height=10,
                    width=10
                ),
                draw_label_args=labutils.DrawLabelArgs(
                    color=Color.WHEAT
                )
            ),
            disabled_edge_args=lutils.DrawLineArgs(
                color=Color.BROWN,
                directionality_draw_args=lutils.DirectionalityIndicatorDrawArgs(
                    color=Color.BROWN,
                    height=10,
                    width=10
                ),
                draw_label_args=labutils.DrawLabelArgs(
                    color=Color.BROWN
                )
            ),
            node_label_args=labutils.DrawLabelArgs(
                color=Color.WHEAT
            ),
            articulation_points_args=putils.DrawPointArgs(
                outline_color=Color.PURPLE,
                radius=10,
                outline_width=3
            ),
            sink_node_args=putils.DrawPointArgs(
                color=Color.RED,
                radius=10
            ),
            source_node_args=putils.DrawPointArgs(
                color=Color.GREEN,
                radius=10
            ),
            orphan_node_args=putils.DrawPointArgs(
                outline_color=Color.RED,
                radius=10
            )
        )

GraphGetter = Callable[[], Graph]
RouteDrawArgsGetter = Callable[[], List[utils.RouteDrawArgs]]

class PyGraphHandler:
    def __init__(self,
                 screen: pygame.Surface,
                 graph_getter: GraphGetter,
                 draw_config: utils.GraphDrawArgs = None,
                 route_draw_args_getter: RouteDrawArgsGetter = None,
                 vec_transformer: vec.VecTransformer = None):
        self.parent_screen = screen
        self.graph_getter = graph_getter
        self._draw_config: utils.GraphDrawArgs = draw_config if draw_config else DEFAULT_DRAW_CONFIG
        self._route_draw_args_getter = route_draw_args_getter
        self._vec_transformer = vec_transformer

        self.surface_manager = SurfaceManager(
            surface_draw_callbacks=[
                SurfaceRegistryArgs(GraphSurfaceType.EDGES_SURFACE_ID.value, self.redraw_edges_surface),
                SurfaceRegistryArgs(GraphSurfaceType.NODES_SURFACE_ID.value, self.redraw_nodes_surface),
                SurfaceRegistryArgs(GraphSurfaceType.EDGE_LABELS_SURFACE_ID.value, self.redraw_edge_labels_surface, default_visible=False),
                SurfaceRegistryArgs(GraphSurfaceType.NODE_LABELS_SURFACE_ID.value, self.redraw_node_labels_surface, default_visible=False),
                SurfaceRegistryArgs(GraphSurfaceType.OVERLAY_SURFACE_ID.value, self.redraw_overlay_surface),
                SurfaceRegistryArgs(GraphSurfaceType.ROUTES_SURFACE_ID.value, self.redraw_routes_surface),
                SurfaceRegistryArgs(GraphSurfaceType.NODE_LABELS_SURFACE_GROUP_ID.value, self.redraw_node_labels_surface_group),
                SurfaceRegistryArgs(GraphSurfaceType.EDGE_LABELS_SURFACE_GROUP_ID.value, self.redraw_edge_labels_surface_group),
            ]
        )

        self._surface_group_id_whitelist = {

        }

    def set_config(self,
                   draw_config: utils.GraphDrawArgs):
        self._draw_config = draw_config

    def redraw_edges_surface(self):
        surf = help.init_surface(self.parent_screen.get_size())
        utils.draw_to_surface(
            surface=surf,
            graph=self.graph_getter(),
            args=self._draw_config.EdgesBaseArgs,
            vec_transformer=self._vec_transformer
        )
        return surf

    def redraw_nodes_surface(self):
        surf = help.init_surface(self.parent_screen.get_size())
        utils.draw_to_surface(
            surface=surf,
            graph=self.graph_getter(),
            args=self._draw_config.NodesBaseArgs,
            vec_transformer=self._vec_transformer
        )
        return surf

    def redraw_node_labels_surface(self):
        surf = help.init_surface(self.parent_screen.get_size())
        utils.draw_to_surface(
            surface=surf,
            graph=self.graph_getter(),
            args=self._draw_config.NodesLabelArgs,
            vec_transformer=self._vec_transformer
        )
        return surf

    def redraw_edge_labels_surface(self):
        surf = help.init_surface(self.parent_screen.get_size())
        utils.draw_to_surface(
            surface=surf,
            graph=self.graph_getter(),
            args=self._draw_config.EdgesLabelArgs,
            vec_transformer=self._vec_transformer
        )
        return surf

    def redraw_overlay_surface(self):
        surf = help.init_surface(self.parent_screen.get_size())
        utils.draw_to_surface(
            surface=surf,
            graph=self.graph_getter(),
            args=self._draw_config.OverlayArgs,
            vec_transformer=self._vec_transformer
        )
        return surf

    def redraw_routes_surface(self):
        surf = help.init_surface(self.parent_screen.get_size())

        if self._route_draw_args_getter is not None:
            utils.draw_to_surface(
                surface=surf,
                graph=self.graph_getter(),
                routes=self._route_draw_args_getter(),
                vec_transformer=self._vec_transformer
            )

        return surf

    def redraw_node_labels_surface_group(self):
        return utils.get_node_label_surface_group(
            graph=self.graph_getter(),
            args=self._draw_config,
            vec_transformer=self._vec_transformer
        )

    def redraw_edge_labels_surface_group(self):
        return utils.get_edge_label_surface_group(
            graph=self.graph_getter(),
            args=self._draw_config,
            vec_transformer=self._vec_transformer
        )

    def invalidate(self, surfaces: Iterable[GraphSurfaceType] = None):
        surf_names = [x.name for x in surfaces] if surfaces is not None else None
        self.surface_manager.invalidate(surf_names)

    def redraw(self):
        self.surface_manager.redraw([x.id for x in GraphSurfaceType])

    def render(self,
               surface: pygame.Surface):
        self.update()
        self.surface_manager.render(surface,
                                    surface_group_ids_whitelist=self._surface_group_id_whitelist)

    def toggle_surface(self, graphSurfaceTypes: List[GraphSurfaceType]):
        self.surface_manager.toggle_visible([x.value for x in graphSurfaceTypes])

    def show_all(self):
        self.surface_manager.show_all()

    def hide_all(self):
        self.surface_manager.hide_all()


    def _naive_mouse_close_to_nodes(self,
                                    graph: Graph,
                                    mouse_pos: Iterable[float],
                                    threshold: float
                                    ) -> List[Node]:
        ret = []
        for node in graph.nodes:
            if vec.distance_between(a=mouse_pos,
                                    b=vec.resolve_vec_transformed_points([node.pos], self._vec_transformer)[0],
                                    allow_diff_lengths=True) <= threshold:
                ret.append(node)

        return ret

    def _naive_mouse_close_to_edges(self,
                                    graph: Graph,
                                    mouse_pos: Iterable[float],
                                    threshold: float
                                    ) -> List[Edge]:
        ret = []
        for edge in graph.edges:
            end = vec.resolve_vec_transformed_points([edge.end.pos], self._vec_transformer)[0]
            start = vec.resolve_vec_transformed_points([edge.start.pos], self._vec_transformer)[0]
            projection = vec.project_onto(a=mouse_pos,
                                          b=end,
                                          origin=start,
                                          allow_diff_lengths=True)
            if vec.distance_between(mouse_pos, projection, allow_diff_lengths=True) <= threshold\
                    and vec.bounded_by(projection, start, end):
                ret.append(edge)

        return ret

    def handle_hover(self):
        close_nodes = self._naive_mouse_close_to_nodes(
            graph=self.graph_getter(),
            mouse_pos=help.mouse_pos(),
            threshold=15
        )

        close_edges = self._naive_mouse_close_to_edges(
            graph=self.graph_getter(),
            mouse_pos=help.mouse_pos(),
            threshold=15
        )

        logger.debug(f"CloseNodes: {close_nodes}")
        logger.debug(f"CloseEdges: {close_edges}")

        self._surface_group_id_whitelist = {
            GraphSurfaceType.NODE_LABELS_SURFACE_GROUP_ID.value: [x.name for x in close_nodes],
            GraphSurfaceType.EDGE_LABELS_SURFACE_GROUP_ID.value: [x.id for x in close_edges]
        }

    def update(self):
        self.handle_hover()

