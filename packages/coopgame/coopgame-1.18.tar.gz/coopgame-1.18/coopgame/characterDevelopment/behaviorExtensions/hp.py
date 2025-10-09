import math

import coopgame.characterDevelopment.character as char
from coopgame.characterDevelopment import stats as stat
import logging

logger = logging.getLogger(__name__)

HP = 'HP'
MAX_HP = 'MAX_HP'

def current_hp(character: char.Character,
               hp_stat_name: str = HP) -> float:
    return character.stats.State.resolve_stat(stat_name=hp_stat_name).val

def max_hp(character: char.Character,
           max_hp_stat_name: str = MAX_HP) ->float:
    return character.stats.State.resolve_stat(stat_name=max_hp_stat_name).val

def alive(character: char.Character,
          hp_stat_name: str = HP) -> bool:
    return not dead(character=character,
                    hp_stat_name=hp_stat_name)

def dead(character: char.Character,
          hp_stat_name: str = HP) -> bool:
    current = current_hp(character=character, hp_stat_name=hp_stat_name)
    return math.isclose(current, 0)


def heal(character: char.Character,
         amount: float = None,
         hp_stat_name: str = HP,
         max_hp_stat_name: str = MAX_HP
         ):
    if amount is None:
        amount = missing_hp(character=character,
                            hp_stat_name=hp_stat_name,
                            max_hp_stat_name=max_hp_stat_name)

    character.stats.register_events(events=[stat.DeltaStatStatsPackageStateEvent(stat_name=hp_stat_name, delta=amount)])

    log_txt = f"Character: {character.name} gained {amount} of hp!"
    current = current_hp(character=character, hp_stat_name=hp_stat_name)
    max = max_hp(character=character, max_hp_stat_name=max_hp_stat_name)
    if math.isclose(max, current):
        log_txt += " Character is at full health!"
    logger.info(log_txt)
    return character

def damage(character: char.Character,
           amount: float,
           hp_stat_name: str = HP):
    character.stats.register_events(events=[stat.DeltaStatStatsPackageStateEvent(stat_name=hp_stat_name, delta=-amount)])

    current = current_hp(character=character, hp_stat_name=hp_stat_name)

    log_txt = f"Character: {character.name} lost {amount} of hp! ({current} remaining)"
    if math.isclose(current, 0):
        log_txt += " Character was killed..."
    logger.info(log_txt)

    return character

def missing_hp(character: char.Character,
               hp_stat_name: str = HP,
               max_hp_stat_name: str = MAX_HP):
    current = current_hp(character, hp_stat_name=hp_stat_name)
    max = max_hp(character, max_hp_stat_name=max_hp_stat_name)

    return max - current

def kill(character: char.Character,
           hp_stat_name: str = HP
         ):
    current = current_hp(character=character,
                         hp_stat_name=hp_stat_name)
    damage(character=character,
           hp_stat_name=hp_stat_name,
           amount=current)
    return character

if __name__ == "__main__":
    import pprint

    default_stats = [
        stat.StatState(HP, val=1000, meta=stat.StatMeta(0, 1000)),
        stat.StatState(MAX_HP, val=1000, meta=stat.StatMeta()),
    ]

    me = char.Character(args=char.CharacterGeneratorArgs(
                            name_provider="Ralphius",
                            init_stats_package=stat.StatsPackageState(
                                base_stats=stat.StatStates({x.stat_name: x for x in default_stats})
                            )
                        )
    )

    pprint.pprint(me.stats.State.Summary)
    damage(me, 19)
    pprint.pprint(me.stats.State.Summary)
    heal(me, 10)
    pprint.pprint(me.stats.State.Summary)
    heal(me)
    pprint.pprint(me.stats.State.Summary)

    kill(me)
    pprint.pprint(me.stats.State.Summary)


