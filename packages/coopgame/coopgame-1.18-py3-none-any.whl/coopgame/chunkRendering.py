from typing import Tuple, Callable, Dict, Any
import math
import numpy as np
import pprint
from cooptools.sectors import sec_u as sec_util

coord_type_resolver= Callable[[Tuple[int, int]], Any]

def get_chunk(target: Tuple[int, int],
               chunk_size: Tuple[int, int],
               tile_type_resolvers: Dict[str, coord_type_resolver]) -> Dict[Tuple[int, int], Dict[str, Any]]:
    chunk_data = {}
    for row in range(chunk_size[1]):
        for col in range(chunk_size[0]):
            target_col = target[1] * chunk_size[1] + col
            target_row = target[0] * chunk_size[0] + row
            coord = (target_col, target_row)

            state = {}
            for type, resolver in tile_type_resolvers.items():
                state[type] = resolver(coord)

            chunk_data[(target_row, target_col)] = state

    return chunk_data

def chunk_of_tile(tile_coord, chunk_shape):
    return (int(math.floor(tile_coord[0] / chunk_shape[0])), int(math.floor(tile_coord[1]/ chunk_shape[1])))


class ChunkRenderer:

    def __init__(self,
                 chunk_size: Tuple[int, int],
                 tile_type_resolvers: Dict[str, coord_type_resolver]):

        """The chunk data is a dictionary that contains k: the chunk coord, v: the list of tile types at coord within
        the chunk"""
        self.chunk_data: Dict[Tuple[int, int], Dict[Tuple[int, int], Dict[str, Any]]] = {}
        self.chunk_size: Tuple[int, int] = chunk_size
        self.tile_type_resolvers: Dict[str, coord_type_resolver] = tile_type_resolvers

    def generate_get_chunk_at_coord(self, coord):
        if coord not in self.chunk_data:
            self.chunk_data[coord] = get_chunk(coord, self.chunk_size, self.tile_type_resolvers)
        return self.chunk_data[coord]

    def tile_pxls(self, chunk_pxls):
        return sec_util.sector_dims(area_dims=chunk_pxls, sector_def=self.chunk_size)

    def renderable_tile_type_array(self,
                                   scroll: Tuple[float, float],
                                   window_size: Tuple[int, int],
                                   chunk_pxls: Tuple[int, int],
                                   key: str,
                                   buffer_tiles: Tuple[int, int] = None
                                   ) -> np.ndarray:
        # get the size of the tile array that can be rendered.
        tile_pxls = self.tile_pxls(chunk_pxls)
        visible_tile_shape = sec_util.sectors_in_window(window_dims=window_size,
                                          sector_dims=tile_pxls,
                                          buffer_sectors=(buffer_tiles[0], buffer_tiles[1], 0, 0))

        # init a zero array of the shape of the renderable tiles
        ret = np.zeros(shape=visible_tile_shape, dtype=int)

        rows, cols = sec_util.sectors_in_window(window_dims=window_size,
                                                sector_dims=tile_pxls,
                                                buffer_sectors=(buffer_tiles[0], buffer_tiles[1], 0, 0))
        # get origin tile
        o_tile = sec_util.sector_from_coord(
            coord=scroll,
            # sec_dims=tile_pxls
            sector_def=(rows, cols),
            area_dims=window_size
        )

        # fill the array with the values of
        for tile_rc in self.visible_tile_generator(scroll, window_size, chunk_pxls, buffer_tiles):
            chunk_coord = chunk_of_tile(tile_rc, self.chunk_size)
            chunk_data = self.generate_get_chunk_at_coord(chunk_coord)
            type = chunk_data[tile_rc]
            ret_coord = (tile_rc[0] - o_tile[0], tile_rc[1] - o_tile[1])
            ret[ret_coord] = type[key]

        return ret

    def visible_tile_idx_by_condition(self,
                                      scroll: Tuple[float, float],
                                      window_size: Tuple[int, int],
                                      chunk_pxls: Tuple[int, int],
                                      tile_evaluator: Callable[[Dict], bool],
                                      buffer_tiles: Tuple[int, int] = None) -> Dict[Tuple[int, int], Dict]:

        ret = {}
        # fill the array with the values of
        for tile_rc in self.visible_tile_generator(scroll, window_size, chunk_pxls, buffer_tiles):
            state = self.tile_state(tile_rc)
            if tile_evaluator(state):
                ret[tile_rc] = state

        return ret

    def visible_chunk_generator(self,
                                scroll: Tuple[float, float],
                                window_size: Tuple[int, int],
                                chunk_pxls: Tuple[int, int]):
        renderable_chunk_shape = sec_util.sectors_in_window(window_size, chunk_pxls, scroll) #self.renderable_chunk_shape(window_size, chunk_pxls, scroll)
        o_chunk_row, o_chunk_col = sec_util.sector_from_coord(scroll, chunk_pxls)

        for col in range(renderable_chunk_shape[1]):
            for row in range(renderable_chunk_shape[0]):
                chunk_row = row + o_chunk_row
                chunk_col = col + o_chunk_col
                yield (chunk_row, chunk_col)

    def visible_tile_generator(self,
                               scroll: Tuple[float, float],
                               window_size: Tuple[int, int],
                               chunk_pxls: Tuple[int, int],
                               buffer_tiles: Tuple[int, int] = None
                               ):

        tile_pxls = sec_util.sector_dims(chunk_pxls, self.chunk_size)
        rows, cols = sec_util.sectors_in_window(window_dims=window_size,
                                          sector_dims=tile_pxls,
                                          buffer_sectors=(buffer_tiles[0], buffer_tiles[1], 0, 0))
        o_tile_coord = sec_util.sector_from_coord(coord=scroll,
                                                  area_dims=window_size,
                                                  sector_def=(rows, cols))
        for col in range(cols):
            for row in range(rows):
                tile_row = row + o_tile_coord[0]
                tile_col = col + o_tile_coord[1]
                yield (tile_row, tile_col)

    def tile_state(self, tile: Tuple[int, int]) -> Dict[str, Any]:
        tile_chunk = chunk_of_tile(tile, self.chunk_size)
        return self.generate_get_chunk_at_coord(tile_chunk)[tile]


if __name__ == "__main__":
    import random as rnd

    chunk_size = (8, 8)
    window_size = (1500, 700)


    def dummy_tile_type_resolver(target: Tuple[int, int]) -> int:
        if target[1] > 10:
            return 2
        if target[1] == 10:
            return 1
        if target[1] == 9:
            return rnd.randint(1, 5) == 1

        return 0


