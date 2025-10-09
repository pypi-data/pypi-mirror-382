from coopgame.characterDevelopment import character as char
import coopgame.characterDevelopment.stats as stat
from typing import Iterable
import logging

logger = logging.getLogger(__name__)


def acquire_traits(character: char.Character, traits: Iterable[stat.StatEffectPackage]):
    character.stats.register_events(events=[stat.StatsPackageStateEvent(description="Add Traits", added_stat_modifiers=traits)])
    logger.info(f"Character: {character} gained traits: {traits}")
    return character

def lose_traits(character: char.Character, traits: Iterable[stat.StatEffectPackage]):
    character.stats.register_events(events=[stat.StatsPackageStateEvent(description="Remove Traits", removed_stat_modifiers=traits)])
    logger.info(f"Character: {character} lost traits: {traits}")
    return character
