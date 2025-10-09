import cooptools.sectors.rect_utils as sec_utl
from typing import Tuple

class ScrollHandler:
    def __init__(self,
                 screen_dims: Tuple[int, int],
                 focal_point: Tuple[float, float] = None,
                 width_dim_p: Tuple[float, float] = None,
                 height_dim_p: Tuple[float, float] = None):
        self.scroll = (0, 0)
        self.width_dim_p = width_dim_p or (0.25, 0.75)
        self.height_dim_p = height_dim_p or (0.25, 0.75)
        self.screen_dims = screen_dims
        self.focal_point = None

        if focal_point:
            self.update(focal_point)

    def update(self,
               focal_point: Tuple[float, float],
               screen_dims: Tuple[int, int] = None,
               width_dim_p: Tuple[float, float] = None,
               height_dim_p: Tuple[float, float] = None
               ):
        if width_dim_p is not None:
            self.width_dim_p = width_dim_p

        if height_dim_p is not None:
            self.height_dim_p = height_dim_p

        if screen_dims is not None:
            self.screen_dims = screen_dims

        delta_x = 0
        delta_y = 0

        self.focal_point = focal_point

        ciw = self.WindowCoord
        if ciw[0] > self.screen_dims[0] * self.width_dim_p[1]:
            delta_x = ciw[0] - self.screen_dims[0] * self.width_dim_p[1]

        if ciw[0] < self.screen_dims[0] * self.width_dim_p[0]:
            delta_x = ciw[0] - self.screen_dims[0] * self.width_dim_p[0]

        if ciw[1] > self.screen_dims[1] * self.height_dim_p[1]:
            delta_y = ciw[1] - self.screen_dims[1] * self.height_dim_p[1]

        if ciw[1] < self.screen_dims[1] * self.height_dim_p[0]:
            delta_y = ciw[1] - self.screen_dims[1] * self.height_dim_p[0]

        self.scroll = (self.scroll[0] + delta_x, self.scroll[1] + delta_y)
        return self.scroll

    def coord_in_window(self, coord_actual: Tuple[float, float]):
        return (coord_actual[0] - self.scroll[0], coord_actual[1] - self.scroll[1])

    @property
    def WindowCoord(self) -> Tuple[float, float]:
        return self.coord_in_window(self.focal_point)


class ScrollTileHandler:

    def __init__(self,
                 tile_size: Tuple[float, float],
                 screen_dims: Tuple[int, int],
                 focal_point: Tuple[float, float],
                 width_dim_p: Tuple[float, float] = None,
                 height_dim_p: Tuple[float, float] = None
                 ):
        self.tile_size = tile_size
        self.scroll_handler = ScrollHandler(screen_dims=screen_dims,
                                            focal_point=focal_point,
                                            width_dim_p=width_dim_p,
                                            height_dim_p=height_dim_p)

    def update(self,
               focal_point: Tuple[float, float],
               screen_dims: Tuple[int, int] = None,
               width_dim_p: Tuple[float, float] = None,
               height_dim_p: Tuple[float, float] = None
               ):
        return self.scroll_handler.update(
            focal_point=focal_point,
            screen_dims=screen_dims,
            width_dim_p=width_dim_p,
            height_dim_p=height_dim_p
        )

    def tile_window_coord(self, tile):
        tile_coords = sec_utl.coord_of_sector(
            sector_dims = self.tile_size,
            sector = tile
        )
        return self.scroll_handler.coord_in_window(tile_coords)


    @property
    def ScrollTile(self):
        """What tile is the current scroll value in?"""
        return sec_utl.sector_from_coord(
            coord=self.scroll_handler.scroll,
            sec_dims=self.tile_size)

    @property
    def ScrollTileCoords(self):
        """What are the coords of the tile that we are scrolled in"""
        return sec_utl.coord_of_sector(
            sector_dims=self.tile_size,
            sector=self.ScrollTile
        )

    @property
    def WorldTile(self):
        return sec_utl.sector_from_coord(
            coord=self.scroll_handler.focal_point,
            sec_dims=self.tile_size
        )

    @property
    def WorldTileCoord(self):
        return sec_utl.coord_of_sector(
            sector=self.WorldTile,
            sector_dims=self.tile_size
        )

    @property
    def WindowTile(self):
        return sec_utl.sector_from_coord(
            coord = (self.scroll_handler.focal_point[0] + self.scroll_handler.scroll[0],
                    self.scroll_handler.focal_point[1] + self.scroll_handler.scroll[1]),
            sec_dims=self.tile_size
        )

    @property
    def WindowTileCoord(self):
        return sec_utl.coord_of_sector(
            sector=self.WindowTile,
            sector_dims=self.tile_size
        )

    @property
    def PosInCurrentTile(self):
        world_tile_coord = self.WorldTileCoord
        return (self.scroll_handler.focal_point[0] - world_tile_coord[0],
                self.scroll_handler.focal_point[1] - world_tile_coord[1])

    @property
    def WorldCoordOffsetScrollTileCoord(self):
        return (self.scroll_handler.focal_point[0] - self.ScrollTileCoords[0] - self.scroll_handler.WindowCoord[0],
                self.scroll_handler.focal_point[1] - self.ScrollTileCoords[1] - self.scroll_handler.WindowCoord[1])

    @property
    def WindowCoords(self):
        return self.scroll_handler.WindowCoord

    @property
    def Scroll(self):
        return self.scroll_handler.scroll

