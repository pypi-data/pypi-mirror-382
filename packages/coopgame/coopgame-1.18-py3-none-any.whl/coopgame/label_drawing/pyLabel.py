from cooptools.coopEnum import CoopEnum
from coopstructs.geometry.vectors.vectorN import Vector2

class TextAlignmentType(CoopEnum):
    TOPLEFT = 'topleft'
    TOPRIGHT = 'topright'
    TOPCENTER = 'midtop'
    BOTTOMLEFT = 'bottomleft'
    BOTTOMRIGHT = 'bottomright'
    RIGHTCENTER = 'midright'
    BOTTOMCENTER = 'midbottom'
    LEFTCENTER = 'midleft'
    CENTER = 'center'

class PyLabel:
    def __init__(self, font, text, color, position, alignment: TextAlignmentType = TextAlignmentType.TOPLEFT):

        self.alignment = alignment
        self.image = font.render(text, 1, color)
        self.rect = self.image.get_rect()
        self.pos = position

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def set_alignment(self, alignment: TextAlignmentType, pos: Vector2 = None):
        self.alignment = alignment
        self.pos = pos
        setattr(self.rect, self.alignment.value, self.pos.as_tuple())