from coopgame.characterDevelopment import character as char
import coopgame.characterDevelopment.stats as stat

MANA = 'MANA'
MAX_MANA = 'MAX_MANA'

class CastSpellCharacterEvent(stat.DeltaStatStatsPackageStateEvent):
    def __init__(self,
                 spell_name: str,
                 spell_cost: float,
                 mana_stat_name: str = MANA):
        super().__init__(
            description=f"Cast Spell \"{spell_name}\" for {spell_cost} mana",
            stat_name=mana_stat_name,
            delta=-spell_cost
        )

def current_mana(character: char.Character,
               mana_stat_name: str = MANA) -> float:
    return character.stats.State.resolve_stat(stat_name=mana_stat_name).val

def max_mana(character: char.Character,
           max_mana_stat_name: str = MAX_MANA) ->float:
    return character.stats.State.resolve_stat(stat_name=max_mana_stat_name).val

def missing_mana(character: char.Character,
               mana_stat_name: str = MANA,
               max_mana_stat_name: str = MAX_MANA):
    current = current_mana(character, mana_stat_name=mana_stat_name)
    max = max_mana(character, max_mana_stat_name=max_mana_stat_name)

    return max - current

def cast_spell(character: char.Character,
               spell_name: str,
               mana_cost: float,
               mana_stat_name: str = MANA):
    current = current_mana(character=character,
                           mana_stat_name=mana_stat_name)

    if mana_cost > current:
        raise ValueError(f"Tried to cast spell {spell_name}, but not enough mana. Current: {current}, Cost: {mana_cost}")

    character.stats.register_events(events=[CastSpellCharacterEvent(spell_name=spell_name, spell_cost=mana_cost)])
    return character


def restore(character: char.Character,
         amount: float = None,
         mana_stat_name: str = MANA,
         max_mana_stat_name: str = MAX_MANA
         ):
    if amount is None:
        amount = missing_mana(character=character,
                            mana_stat_name=mana_stat_name,
                            max_mana_stat_name=max_mana_stat_name)

    character.stats.register_events(events=[stat.DeltaStatStatsPackageStateEvent(stat_name=mana_stat_name, delta=amount)])
    return character

