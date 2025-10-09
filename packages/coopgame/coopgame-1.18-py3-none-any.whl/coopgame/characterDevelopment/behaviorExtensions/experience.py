import coopgame.characterDevelopment.stats as stat
from coopgame.characterDevelopment import character as char

EXPERIENCE = 'EXPERIENCE'

def gain_experience(character: char.Character,
                    xp_amount: float,
                    experience_stat_name: str = EXPERIENCE):
    character.stats.register_events(events=[stat.DeltaStatStatsPackageStateEvent(stat_name=experience_stat_name, delta=xp_amount)])
    return character