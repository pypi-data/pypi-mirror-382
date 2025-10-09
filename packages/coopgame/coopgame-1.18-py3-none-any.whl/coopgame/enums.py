from cooptools.coopEnum import CoopEnum, add_succ_and_pred_maps, auto

@add_succ_and_pred_maps
class Orientation(CoopEnum):
    UP=1
    RIGHT=2
    DOWN=3
    LEFT=4

@add_succ_and_pred_maps
class ConnectionType(CoopEnum):
    ARC = 1
    LINE = 2
    BEZIER = 3

@add_succ_and_pred_maps
class EntryType(CoopEnum):
    CRAWLER = 1
    GRIDCLICK = 2

@add_succ_and_pred_maps
class GridDrawType(CoopEnum):
    BOXES = 1
    LINES = 2

@add_succ_and_pred_maps
class Rarity(CoopEnum):
    COMMON = auto()
    UNCOMMON = auto()
    RARE = auto()
    EPIC = auto()
    LEGENDARY = auto()
    MYTHIC = auto()
    DIVINE = auto()
