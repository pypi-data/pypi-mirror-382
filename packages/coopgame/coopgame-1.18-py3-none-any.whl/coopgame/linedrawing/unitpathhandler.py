from coopgraph.grids import RectGrid
from typing import Hashable, Callable
from coopstructs.curves import LineCurve, Arc, Orientation
from coopstructs.geometry import Rectangle
from coopstructs.geometry.vectors.vectorN import Vector2

class UnitPathHandler():

    def __init__(self, toggled_key: Hashable):
        self.toggled_key = toggled_key

    def generate(self
             , grid: RectGrid
             , grid_box_rect: Rectangle
             , naming_provider: Callable[[], str]):

        curves = []

        for row in range(0, grid.nRows):
            for col in range(0, grid.nColumns):

                cell = grid.at(row, col)
                if not cell.state[self.toggled_key].value:
                    continue

                left = cell.left.state[self.toggled_key].value if cell.left else None
                right = cell.right.state[self.toggled_key].value if cell.right else None
                up = cell.up.state[self.toggled_key].value if cell.up else None
                down = cell.down.state[self.toggled_key].value if cell.down else None
                connection_count = sum(x for x in [left, right, up, down] if x)

                if left and right:
                    # Horizontal Line
                    start = Vector2(col * grid_box_rect.width, (row + .5) * grid_box_rect.height)
                    end = Vector2((col + 1) * grid_box_rect.width, (row + .5) * grid_box_rect.height)

                    curves.append(LineCurve(id=naming_provider(), origin=start, destination=end))

                if up and down:

                    # Vertical Line
                    start = Vector2((col + .5) * grid_box_rect.width, row * grid_box_rect.height)
                    end = Vector2((col + 0.5) * grid_box_rect.width, ((row + 1) * grid_box_rect.height))

                    curves.append(LineCurve(id=naming_provider(), origin=start, destination=end))

                if up and right:
                    origin = Vector2((col + .5) * grid_box_rect.width, (row) * grid_box_rect.height)
                    curves.append(Arc(id = naming_provider(),
                                      orientation=Orientation.DOWN_RIGHT,
                                      origin=origin,
                                      arc_box_size=Vector2(grid_box_rect.width, grid_box_rect.height)))

                if up and left:
                    origin = Vector2((col) * grid_box_rect.width, (row + 0.5) * grid_box_rect.height)
                    curves.append(Arc(id=naming_provider(),
                                      orientation=Orientation.RIGHT_UP,
                                      origin=origin,
                                      arc_box_size=Vector2(grid_box_rect.width, grid_box_rect.height)))

                if right and down:
                    origin = Vector2((col + .5) * grid_box_rect.width, (row + 1) * grid_box_rect.height)
                    curves.append(Arc(id=naming_provider(),
                                      orientation=Orientation.UP_RIGHT,
                                      origin=origin,
                                      arc_box_size=Vector2(grid_box_rect.width, grid_box_rect.height)))


                if down and left:
                    origin = Vector2((col) * grid_box_rect.width, (row + .5) * grid_box_rect.height)
                    curves.append(Arc(id=naming_provider(),
                                      orientation=Orientation.RIGHT_DOWN,
                                      origin=origin,
                                      arc_box_size=Vector2(grid_box_rect.width, grid_box_rect.height)))

                if connection_count == 1:
                    if up:
                        # Vertical Line
                        start = Vector2((col + .5) * grid_box_rect.width, row * grid_box_rect.height)
                        end = Vector2((col + 0.5) * grid_box_rect.width, ((row + 0.5) * grid_box_rect.height))

                        curves.append(LineCurve(id=naming_provider(), origin=start, destination=end))
                    elif down:
                        # Vertical Line
                        start = Vector2((col + .5) * grid_box_rect.width, (row + .5) * grid_box_rect.height)
                        end = Vector2((col + 0.5) * grid_box_rect.width, ((row + 1) * grid_box_rect.height))

                        curves.append(LineCurve(id=naming_provider(), origin=start, destination=end))

                    elif right:
                        # Horizontal Line
                        start = Vector2((col + .5) * grid_box_rect.width, (row + .5) * grid_box_rect.height)
                        end = Vector2((col + 1) * grid_box_rect.width, (row + .5) * grid_box_rect.height)

                        curves.append(LineCurve(id=naming_provider(), origin=start, destination=end))

                    elif left:
                        # Horizontal Line
                        start = Vector2(col * grid_box_rect.width, (row + .5) * grid_box_rect.height)
                        end = Vector2((col + .5) * grid_box_rect.width, (row + .5) * grid_box_rect.height)

                        curves.append(LineCurve(id=naming_provider(), origin=start, destination=end))

                elif connection_count == 0:
                    # Horizontal Line
                    start = Vector2((col + 0.25) * grid_box_rect.width, (row + .5) * grid_box_rect.height)
                    end = Vector2((col + .75) * grid_box_rect.width, (row + .5) * grid_box_rect.height)

                    curves.append(LineCurve(id=naming_provider(), origin=start, destination=end))

                    # Vertical Line
                    start = Vector2((col + .5) * grid_box_rect.width, (row + .25) * grid_box_rect.height)
                    end = Vector2((col + .5) * grid_box_rect.width, (row + .75) * grid_box_rect.height)

                    curves.append(LineCurve(id=naming_provider(), origin=start, destination=end))

        return curves