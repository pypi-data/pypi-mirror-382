from coopgame.enums import Rarity
class ItemBase:
    def __init__(self,
                 rarity: Rarity):
        self._rarity: Rarity = rarity

    @property
    def Rarity(self) -> Rarity:
        return self._rarity
