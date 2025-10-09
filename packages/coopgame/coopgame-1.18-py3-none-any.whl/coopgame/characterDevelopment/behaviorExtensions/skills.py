from coopgame.characterDevelopment import character as char
import coopgame.characterDevelopment.stats as stat
from typing import Iterable

def acquire_skills(character: char.Character, skills: Iterable[stat.StatEffectPackage]):
    character.stats.register_events(events=[stat.StatsPackageStateEvent(description="Add Skills", added_stat_modifiers=skills)])
    return character

def lose_skills(character: char.Character, skills: Iterable[stat.StatEffectPackage]):
    character.stats.register_events(events=[stat.StatsPackageStateEvent(description="Lose Skills", removed_stat_modifiers=skills)])
    return character
