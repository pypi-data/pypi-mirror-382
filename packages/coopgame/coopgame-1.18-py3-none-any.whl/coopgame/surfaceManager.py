import pygame
from typing import Callable, Tuple, Dict
from cooptools.toggles import BooleanToggleable
from typing import List, Any, Callable
from dataclasses import dataclass, field
from cooptools.register import Register
import logging

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class SurfaceGroup:
    surfaces_lookup: Dict[str, pygame.Surface]
    surface_pos: Dict[str, Tuple[int, int]]

DrawCallback = Callable[[], pygame.Surface | SurfaceGroup]

@dataclass(frozen=True)
class SurfaceRegistryArgs:
    id: str
    callback: DrawCallback
    frame_update: bool = False
    default_visible: bool = True

@dataclass
class SurfaceRegister:
    registry_args: SurfaceRegistryArgs
    visibility_toggle: BooleanToggleable = field(init=False, default_factory=lambda: BooleanToggleable(default=True))

    def __post_init__(self):
        if self.registry_args.default_visible == False:
            self.visibility_toggle.set_value(False)

class SurfaceManager:
    def __init__(self,
                 surface_draw_callbacks: List[SurfaceRegistryArgs] = None):
        self.surface_register: Register = Register[SurfaceRegister]()

        if surface_draw_callbacks:
            self.register_surface_ids(surface_draw_callbacks)

        self.surfaces: Dict[str, pygame.Surface] = {}

    @property
    def RegisteredSurfaceIds(self) -> List[str]:
        return list(self.surface_register.Registry.keys())

    @property
    def FrameUpdateSurfaceIds(self) -> List[str]:
        return [surf.registry_args.id for id, surf in self.surface_register.Registry.items() if surf.registry_args.frame_update]

    def register_surface_ids(self,
                             surface_draw_callbacks: List[SurfaceRegistryArgs]):
        self.surface_register.register(
            to_register=[SurfaceRegister(x) for x in surface_draw_callbacks],
            ids=[x.id for x in surface_draw_callbacks]
        )
        logger.info(f"Registered surfaces: [{[x.id for x in surface_draw_callbacks]}]")

    def invalidate(self, ids: List[str] = None):
        if ids is not None:
            logger.info(f"Invalidating {ids}")
        else:
            logger.info(f"Invalidating")

        self.redraw(ids=ids)

    def redraw(self,
               ids: List[str] = None):
        if ids is None:
            ids = list(self.surface_register.Registry.keys())

        for id in ids:
            logger.info(f"Drawing surface {id}...")
            self.surfaces[id] = self.surface_register.Registry[id].registry_args.callback()
            logger.info(f"Surface {id} drawn")

    def update(self):
        self.update_if_visible(self.FrameUpdateSurfaceIds)

    def render(self,
               surface: pygame.Surface,
               at_pos: Tuple[int, int] = None,
               frame_update: bool = False,
               surface_group_ids_whitelist: Dict[str, List[str]] = None):
        if frame_update:
            self.update()

        if at_pos is None:
            at_pos = (0, 0)

        for id, sr in self.surface_register.Registry.items():
            if sr.visibility_toggle.value:
                to_render = self.get_surfaces(ids=[id], dims=surface.get_size())[id]

                # Handle a surface group where specific surfaceGroup ids are provided
                if type(to_render) == SurfaceGroup and surface_group_ids_whitelist is not None and id in surface_group_ids_whitelist.keys():
                    logger.debug(f"Rendering surface group {id} [{surface_group_ids_whitelist[id]}]")
                    for to_render_sub_id in surface_group_ids_whitelist[id]:
                        surface.blit(to_render.surfaces_lookup[to_render_sub_id], dest=to_render.surface_pos[to_render_sub_id])

                # Handle a surface group where no specific surfaceGroup ids are provided
                if type(to_render) == SurfaceGroup and surface_group_ids_whitelist is None:
                    logger.debug(f"Rendering surface group {id}")
                    for id, surf in to_render.surfaces_lookup.items():
                        surface.blit(surf, dest=at_pos)

                # Handle if the type is not a surface group
                if type(to_render) == pygame.Surface:
                    logger.debug(f"Rendering surface {id}")
                    surface.blit(self.get_surfaces(ids=[id], dims=surface.get_size())[id], dest=at_pos)

    def get_surfaces(self,
                     ids: List[str],
                     dims: Tuple[int, int],
                     force_update: bool = False) -> Dict[str, pygame.Surface | SurfaceGroup]:
        # update surfaces that dont exist or that dont match dims
        for id in ids:
            if id not in self.surfaces.keys():
                logger.info(f"Redrawing surface [{id}] because it was not cached")
                self.redraw([id])

            elif type(self.surfaces[id]) == pygame.Surface and self.surfaces[id].get_size() != dims:
                logger.info(f"Redrawing surface [{id}] because it was not the correct size")
                self.redraw([id])

            elif force_update:
                logger.info(f"Redrawing surface [{id}] because it was forced")
                self.redraw([id])

        # return the surfaces
        return {id: self.surfaces[id] for id in ids}

    def get_toggled_state(self, ids: List[str]) -> Dict[str, bool]:
        return {
            x: self.surface_register.Registry[x].visibility_toggle.value for x in ids
        }

    def toggle_visible(self, ids: List[str]) -> Dict[str, bool]:
        logger.info(f"Toggling visibility for {ids}")
        # toggle
        [self.surface_register.Registry[x].visibility_toggle.toggle() for x in ids]

        return self.get_toggled_state(ids)

    def set_visiblility(self, ids: List[str], visible: bool):
        logger.info(f"Setting visibility [{visible}] for {ids}")
        # toggle
        [self.surface_register.Registry[x].visibility_toggle.set_value(visible) for x in ids]
        return self.get_toggled_state(ids)

    def hide_all(self) -> Dict[str, bool]:
        logger.info(f"Hiding all surfaces")
        self.set_visiblility(ids=self.RegisteredSurfaceIds, visible=False)
        return self.get_toggled_state(self.RegisteredSurfaceIds)

    def show_all(self) -> Dict[str, bool]:
        logger.info(f"Showing all surfaces")
        self.set_visiblility(ids=self.RegisteredSurfaceIds, visible=True)
        return self.get_toggled_state(self.RegisteredSurfaceIds)

    def update_if_visible(self, ids: List[str]):
        self.redraw([id for id, visible in self.get_toggled_state(ids).items() if visible])

