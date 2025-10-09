from coopgame.characterDevelopment.behaviorExtensions import hp as hp
from coopgame.characterDevelopment import character as char
from coopgame.characterDevelopment import stats as stat
from typing import Callable, Tuple
import logging
import random as rnd

logger = logging.getLogger(__name__)

STRENGTH = 'STRENGTH'
SPEED = 'SPEED'
MARTIAL_COMBAT = 'MARTIAL_COMBAT'
FORTUNE = 'FORTUNE'



class DualStartedStatEvent(stat.DeltaStatStatsPackageStateEvent):
    def __init__(self, opponent: char.Character):


        super().__init__(

        )



DualingEpochHandler=Callable[[char.Character, char.Character],
                                Tuple[char.Character, char.Character]]



def basic_attack(attacker: char.Character,
                 defender: char.Character) -> Tuple[char.Character, char.Character]:
    attacker_stats = attacker.stats.State.InternallyResolvedStats.stats
    defender_stats = defender.stats.State.InternallyResolvedStats.stats

    fortune_window = 0.5


    attack_score = attacker_stats[STRENGTH].val * rnd.uniform(1 - fortune_window * 0.5 * (1 + attacker_stats[FORTUNE].val / 100),
                                                              1 + fortune_window * 0.5 * (1 + attacker_stats[FORTUNE].val / 100))
    defender_score = defender_stats[STRENGTH].val * rnd.uniform(1 - fortune_window * 0.5 * (1 + defender_stats[FORTUNE].val / 100),
                                                              1 + fortune_window * 0.5 * (1 + defender_stats[FORTUNE].val / 100))

    damage = int(max(0.0, attack_score - 0.75 * defender_score))

    attacker_speed = attacker_stats[SPEED].val
    defender_speed = defender_stats[SPEED].val

    p_miss = max(0.0, (defender_speed - attacker_speed) / 100)

    if rnd.random() > p_miss:
        hp.damage(defender, damage)

    return attacker, defender

def basic_dualing_epoch_handler(char1: char.Character, char2: char.Character) -> Tuple[char.Character, char.Character]:
    basic_attack(char1, char2)
    if hp.alive(character=char2):
        basic_attack(char2, char1)

    return char1, char2


def dual(char1: char.Character,
           char2: char.Character,
           dual_epoch_handler: DualingEpochHandler) -> Tuple[char.Character, char.Character]:
    while True:
        char1, char2 = dual_epoch_handler(char1, char2)

        dead_chars = []
        for char in [char1, char2]:
            if hp.dead(character=char):
                logger.info(f"Character: {char.name} was killed!")
                dead_chars.append(char)

        if len(dead_chars) > 0:
            break

    return char1, char2






