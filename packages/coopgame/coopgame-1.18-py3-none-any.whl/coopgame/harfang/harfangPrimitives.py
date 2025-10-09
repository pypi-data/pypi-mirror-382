import harfang as hg
from coopstructs.vectors import Vector2

def draw_circle(plus):
    # plus.Circle2D()
    draw_triangle(plus)

def draw_square(plus, pos: Vector2, size: int):
    cube = plus.CreateGeometry(plus.CreateCube())
    plus.Geometry2D(int(pos.x), int(pos.y), cube, 0, 0, 0, size)

def draw_triangle(plus, a: Vector2, b: Vector2, c: Vector2, hcolor: hg.Color):
    # plus.Triangle2D(a.x, a.y, b.x, b.y, c.x, c.y, hcolor, hcolor, hcolor)

    x_adj = 0
    y_adj = 0

    plus.Triangle2D(x_adj + int(a.x), y_adj + int(a.y), x_adj + int(c.x), y_adj + int(c.y), x_adj + int(b.x), y_adj + int(b.y), hcolor, hcolor, hcolor)

    # plus.Triangle2D(int(a.x) + x_adj, int(a.y) + y_adj, int(b.x) + x_adj, int(b.y) + y_adj, int(c.x) + x_adj, int(c.y) + y_adj,
    #                 hg.Color.Red, hg.Color.Blue, hg.Color.Green)
    # plus.Triangle2D(40, 40, 200, 260, 360, 40, hg.Color.Red, hg.Color.Blue, hg.Color.Green)