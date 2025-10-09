import coopgame.characterDevelopment.stats as stat
from cooptools.coopEnum import CoopEnum, auto
from cooptools.common import verify_val, bound_value, verify
from coopgame.characterDevelopment.manifests import MutuallyExclusiveManifest

###################
# stats
###################
class BuiltInStatType(CoopEnum):
    HEIGHT_M = auto()  # General attribute
    WEIGHT_KG = auto()  # General attribute
    HP = auto()  # General attribute
    # MAX_HP = auto() # General attribute # TODO: How to handle this correctly? Its both part of meta AND a good stat to track. How will updating HP honor this stat?
    EXPERIENCE = auto()  # General attribute
    INTELLECT = auto()  # affects how the character is capable of figuring out problems using intuition
    EMOTION = auto()  # affects how the character is capable of figuring out problems using feeling
    CHARISMA = auto()  # affects how the character interacts with other characters and their willingness to accept the character
    PREMONITION = auto()  # affects if the character can "sense" things that are about to happen
    OBSERVATION = auto()  # affects if the character can notice details in the environment
    STRENGTH = auto()  # physical ability to perform heavy feats
    NIMBLENESS = auto()  # physical ability to perform complex feats
    SPEED = auto()  # physical ability to perform fast feats
    MAGIC = auto()  # "strength" of the magic order
    MANA = auto()  # amount of available pool to cast spells
    ATTRACTIVENESS = auto()  # affects how other characters perceive the character
    LEADERSHIP = auto()  # affects the ability of the character to maintain control over other characters
    MARTIAL_TACTICS = auto() # affects the ability of the character to perform combat related decisions
    MARTIAL_STRATEGY = auto()  # affects the ability of the character to perform war planning related decisions
    RATIONALITY = auto()  # affects the ability of the character to use 'INTELLECT' rather than 'EMOTION' when making decisions
    AMBITION = auto()  # affects the characters likelihood to strive for better position
    BOLDNESS = auto()  # affects the characters likelihood to take risks
    HEALTH = auto() # describes the characters overall well-being and likelihood to contract ailments
    FORTUNE = auto() # affects many other attributes when

STAT_DEFAULTS = {
    BuiltInStatType.HEIGHT_M: stat.StatState(stat_name=BuiltInStatType.HEIGHT_M.name, val=2, meta=stat.StatMeta(min=0.25, max=5)),
    BuiltInStatType.WEIGHT_KG: stat.StatState(stat_name=BuiltInStatType.WEIGHT_KG.name, val=75, meta=stat.StatMeta(min=25, max=250)),
    BuiltInStatType.SPEED: stat.StatState(stat_name=BuiltInStatType.SPEED.name, val=15, meta=stat.StatMeta(min=0, max=100)),
    BuiltInStatType.HP: stat.StatState(stat_name=BuiltInStatType.HP.name, val=1000, meta=stat.StatMeta(min=0, max=1000)),
    BuiltInStatType.INTELLECT: stat.StatState(stat_name=BuiltInStatType.INTELLECT.name, val=15, meta=stat.StatMeta(min=0, max=100)),
    BuiltInStatType.CHARISMA: stat.StatState(stat_name=BuiltInStatType.CHARISMA.name, val=15, meta=stat.StatMeta(min=0, max=100)),
    BuiltInStatType.PREMONITION: stat.StatState(stat_name=BuiltInStatType.PREMONITION.name, val=15, meta=stat.StatMeta(min=0, max=100)),
    BuiltInStatType.OBSERVATION: stat.StatState(stat_name=BuiltInStatType.OBSERVATION.name, val=15, meta=stat.StatMeta(min=0, max=100)),
    BuiltInStatType.MAGIC: stat.StatState(stat_name=BuiltInStatType.MAGIC.name, val=15, meta=stat.StatMeta(min=0, max=100)),
    BuiltInStatType.MANA: stat.StatState(stat_name=BuiltInStatType.MANA.name, val=100, meta=stat.StatMeta(min=0, max=100)),
    BuiltInStatType.EXPERIENCE: stat.StatState(stat_name=BuiltInStatType.EXPERIENCE.name, val=0, meta=stat.StatMeta(min=0)),
    BuiltInStatType.STRENGTH: stat.StatState(stat_name=BuiltInStatType.STRENGTH.name, val=15, meta=stat.StatMeta(min=0, max=100)),
    BuiltInStatType.ATTRACTIVENESS: stat.StatState(stat_name=BuiltInStatType.ATTRACTIVENESS.name, val=10, meta=stat.StatMeta(min=0, max=100)),
    BuiltInStatType.EMOTION: stat.StatState(stat_name=BuiltInStatType.EMOTION.name, val=15, meta=stat.StatMeta(min=0, max=100)),
    BuiltInStatType.NIMBLENESS: stat.StatState(stat_name=BuiltInStatType.NIMBLENESS.name, val=15, meta=stat.StatMeta(min=0, max=100)),
    BuiltInStatType.LEADERSHIP: stat.StatState(stat_name=BuiltInStatType.LEADERSHIP.name, val=15, meta=stat.StatMeta(min=0, max=100)),
    BuiltInStatType.MARTIAL_TACTICS: stat.StatState(stat_name=BuiltInStatType.MARTIAL_TACTICS.name, val=15, meta=stat.StatMeta(min=0, max=100)),
    BuiltInStatType.MARTIAL_STRATEGY: stat.StatState(stat_name=BuiltInStatType.MARTIAL_STRATEGY.name, val=15, meta=stat.StatMeta(min=0, max=100)),
    BuiltInStatType.RATIONALITY: stat.StatState(stat_name=BuiltInStatType.RATIONALITY.name, val=15, meta=stat.StatMeta(min=0, max=100)),
    BuiltInStatType.AMBITION: stat.StatState(stat_name=BuiltInStatType.AMBITION.name, val=15, meta=stat.StatMeta(min=0, max=100)),
    BuiltInStatType.BOLDNESS: stat.StatState(stat_name=BuiltInStatType.BOLDNESS.name, val=15, meta=stat.StatMeta(min=0, max=100)),
    BuiltInStatType.HEALTH: stat.StatState(stat_name=BuiltInStatType.HEALTH.name, val=15, meta=stat.StatMeta(min=0, max=100)),
    BuiltInStatType.FORTUNE: stat.StatState(stat_name=BuiltInStatType.FORTUNE.name, val=0, meta=stat.StatMeta(min=-25, max=25))
}

def _verify_stat_defaults():
    verify(lambda: all(x in STAT_DEFAULTS.keys() for x in BuiltInStatType), msg=f"Missing trait(s) definitions: \n {[x for x in BuiltInStatType if x not in STAT_DEFAULTS.keys()]}")
_verify_stat_defaults()


##################
# skills
##################
class Skill(CoopEnum):
    WOODCUTTER = auto()

skills_manifest = {
    Skill.WOODCUTTER: stat.StatEffectPackage(id=Skill.WOODCUTTER.name, description="Cut wood",
                                             stat_effects=frozenset([stat.StatEffect(BuiltInStatType.STRENGTH.name, delta_effect=5)]),
                                           category='SKILL')
}

def _verify_skill_manifest():
    verify(lambda: all(x in skills_manifest.keys() for x in Skill), msg=f"Missing trait(s) definitions: \n {[x for x in Skill if x not in skills_manifest.keys()]}")
_verify_skill_manifest()


###################
# Personality traits
###################
class PersonalityTrait(CoopEnum):
    CAUTIOUS = auto()
    CARELESS = auto()
    BRAVE = auto()

"""
Intended Trait effect relationships:
    Courage: Brave / Cowardly
    Sexuality: Chaste / Lustful
    Disturb: Peaceful / Excitable
    Ambition: Content / Ambitious
    WorkEthic: Diligent / Lazy
    Acceptance: Forgiving / Vengeful
    Giving: Generous / Greedy
    Charisma: Introverted / Extroverted
    Honesty: Truthful / Deceitful
    Humility: Humble / Arrogant
    Justice: Just / Arbitrary
    Patience: Patient / Impatient
    Paranoia: Trusting / Paranoid
    Fortune: Lucky / UnLucky
"""


personality_trait_manifest =  {
    PersonalityTrait.CAUTIOUS: stat.StatEffectPackage(id=PersonalityTrait.CAUTIOUS.name, description="affects observation premonition speed",
                                                      stat_effects=frozenset([stat.StatEffect(BuiltInStatType.PREMONITION.name, delta_effect=10),
                                                             stat.StatEffect(BuiltInStatType.OBSERVATION.name, delta_effect=10),
                                                             stat.StatEffect(BuiltInStatType.SPEED.name, delta_effect=-10)]),
                                           category='PERSONALITY_TRAIT'),
    PersonalityTrait.CARELESS: stat.StatEffectPackage(id=PersonalityTrait.CARELESS.name, description="affects observation premonition speed",
                                                      stat_effects=frozenset([stat.StatEffect(BuiltInStatType.PREMONITION.name, delta_effect=-10),
                                                             stat.StatEffect(BuiltInStatType.OBSERVATION.name, delta_effect=-10),
                                                             stat.StatEffect(BuiltInStatType.SPEED.name, delta_effect=10)]),
                                           category='PERSONALITY_TRAIT'),
    PersonalityTrait.BRAVE: stat.StatEffectPackage(id=PersonalityTrait.BRAVE.name, description="affects observation premonition speed",
                                                   stat_effects=frozenset([stat.StatEffect(BuiltInStatType.ATTRACTIVENESS.name, delta_effect=5),
                                                        stat.StatEffect(BuiltInStatType.CHARISMA.name, delta_effect=5),
                                                        stat.StatEffect(BuiltInStatType.AMBITION.name, delta_effect=5),
                                                        stat.StatEffect(BuiltInStatType.BOLDNESS.name, delta_effect=15),
                                                        stat.StatEffect(BuiltInStatType.LEADERSHIP.name, delta_effect=10)]),
                                           category='PERSONALITY_TRAIT')
}

def _verify_personality_trait_manifest():
    verify(lambda: all(x in personality_trait_manifest.keys() for x in PersonalityTrait), msg=f"Missing trait(s) definitions: \n {[x for x in PersonalityTrait if x not in personality_trait_manifest.keys()]}")
_verify_personality_trait_manifest()



###################
# Physical Traits
###################
class PhysicalTraitType(CoopEnum):
    BEAUTY = auto()


class PhysicalTrait(CoopEnum):
    UGLY = auto()
    WEAK = auto()

"""
Intended Trait effect relationships:
    Beauty: Ugly / Plain / Attractive / Beautiful
    Strength: Puny / Weak / Strong / Mighty
    Height: Dwarf / Short / Tall / Giant
    Weight: Skinny / Thin / Stout / Obese


"""

physical_trait_manifest = {
    PhysicalTrait.UGLY: stat.StatEffectPackage(id=PhysicalTrait.UGLY.name, description="affects others perception of their beauty",
                                                  stat_effects=frozenset([stat.StatEffect(BuiltInStatType.ATTRACTIVENESS.name, delta_effect=-15)]),
                                           category='PHYSICAL_TRAIT'),
    PhysicalTrait.WEAK: stat.StatEffectPackage(id=PhysicalTrait.WEAK.name, description="affects strength",
                                                  stat_effects=frozenset([stat.StatEffect(BuiltInStatType.STRENGTH.name, delta_effect=-15)]),
                                           category='PHYSICAL_TRAIT'),
}


def _verify_personality_trait_manifest():
    verify(lambda: all(x in personality_trait_manifest.keys() for x in PersonalityTrait),
           msg=f"Missing trait(s) definitions: \n {[x for x in PersonalityTrait if x not in personality_trait_manifest.keys()]}")


_verify_personality_trait_manifest()


###################
# status effects
###################
class StatusEffect(CoopEnum):
    FATIGUED = auto()
    ENERGIZED = auto()
    PANICKED = auto()
    CALM = auto()

"""
Intended Status Efects:

"""
panicked = stat.StatEffectPackage(id=StatusEffect.PANICKED.name, description="affects strength and speed and charisma and observation",
                                                   stat_effects=frozenset([stat.StatEffect(BuiltInStatType.STRENGTH.name, delta_effect=10),
                                                                           stat.StatEffect(BuiltInStatType.SPEED.name, delta_effect=10),
                                                                           stat.StatEffect(BuiltInStatType.CHARISMA.name, delta_effect=-10),
                                                                           stat.StatEffect(BuiltInStatType.OBSERVATION.name, delta_effect=-20),
                                                                           stat.StatEffect(BuiltInStatType.BOLDNESS.name, delta_effect=-20),
                                                                           stat.StatEffect(BuiltInStatType.AMBITION.name, delta_effect=-20),
                                                                           stat.StatEffect(BuiltInStatType.ATTRACTIVENESS.name, delta_effect=-10),
                                                                           stat.StatEffect(BuiltInStatType.RATIONALITY.name, delta_effect=-15),
                                                                           stat.StatEffect(BuiltInStatType.MARTIAL_STRATEGY.name, delta_effect=-15),
                                                                           stat.StatEffect(BuiltInStatType.MARTIAL_TACTICS.name, delta_effect=-15),
                                                                           stat.StatEffect(BuiltInStatType.LEADERSHIP.name, delta_effect=-10),
                                                                           stat.StatEffect(BuiltInStatType.NIMBLENESS.name, delta_effect=-10),
                                                                           stat.StatEffect(BuiltInStatType.EMOTION.name, delta_effect=10),
                                                                           stat.StatEffect(BuiltInStatType.INTELLECT.name, delta_effect=-10)]),
                                           category='STATUS_EFFECT')
fatigued = stat.StatEffectPackage(id=StatusEffect.FATIGUED.name, description="affects strength and speed and charisma and observation",
                                                  stat_effects=frozenset([stat.StatEffect(BuiltInStatType.STRENGTH.name, delta_effect=-10),
                                                        stat.StatEffect(BuiltInStatType.SPEED.name, delta_effect=-10),
                                                        stat.StatEffect(BuiltInStatType.CHARISMA.name, delta_effect=-5),
                                                        stat.StatEffect(BuiltInStatType.OBSERVATION.name, delta_effect=-3)]),
                                           category='STATUS_EFFECT')
status_effect_manifest = {
    StatusEffect.FATIGUED: fatigued,
    StatusEffect.ENERGIZED: fatigued.with_opposite_stat_effects(id=StatusEffect.ENERGIZED.name, description="Energized"),
    StatusEffect.PANICKED: panicked,
    StatusEffect.CALM: panicked.with_opposite_stat_effects(id=StatusEffect.CALM.name, description="Calm")
}
def _verify_status_effect_manifest():
    verify(lambda: all(x in status_effect_manifest.keys() for x in StatusEffect), msg=f"Missing trait(s) definitions: \n {[x for x in StatusEffect if x not in status_effect_manifest.keys()]}")
_verify_status_effect_manifest()




########################
# Global Events
########################
class GlobalEffect(CoopEnum):
    FAMINE = auto()

global_effect_manifest = {
    GlobalEffect.FAMINE: stat.StatEffectPackage(id=GlobalEffect.FAMINE.name, description="Worldwide food shortage. Affects strength, speed, emotion and rationality",
                                                  stat_effects=frozenset([stat.StatEffect(BuiltInStatType.STRENGTH.name, delta_effect=-10),
                                                        stat.StatEffect(BuiltInStatType.SPEED.name, delta_effect=-10),
                                                        stat.StatEffect(BuiltInStatType.EMOTION.name, delta_effect=10),
                                                        stat.StatEffect(BuiltInStatType.RATIONALITY.name, delta_effect=-15)]),
                                           category='GLOBAL')
}


def _verify_global_effect_manifest():
    verify(lambda: all(x in global_effect_manifest.keys() for x in GlobalEffect), msg=f"Missing gloableffect(s) definitions: \n {[x for x in GlobalEffect if x not in global_effect_manifest.keys()]}")
_verify_global_effect_manifest()


########################
# Races
########################
class RaceType(CoopEnum):
    HUMAN = auto()
    ORC = auto()
    ELF = auto()
    DARK_ELF = auto()
    DWARF = auto()

races_manifest = {
    RaceType.HUMAN: stat.StatEffectPackage(id=RaceType.HUMAN.name, description="",
                                           stat_effects=frozenset([
                                                        stat.StatEffect(BuiltInStatType.EMOTION.name, delta_effect=10),
                                                        stat.StatEffect(BuiltInStatType.RATIONALITY.name, delta_effect=-5)
                                                  ]),
                                           category='RACE'),
    RaceType.ORC: stat.StatEffectPackage(id=RaceType.ORC.name, description="",
                                         stat_effects=frozenset([
                                                   stat.StatEffect(BuiltInStatType.STRENGTH.name, delta_effect=10),
                                                   stat.StatEffect(BuiltInStatType.SPEED.name, delta_effect=-10),
                                                   stat.StatEffect(BuiltInStatType.EMOTION.name, delta_effect=10),
                                                   stat.StatEffect(BuiltInStatType.RATIONALITY.name, delta_effect=-10),
                                                   stat.StatEffect(BuiltInStatType.MAGIC.name, delta_effect=-5),
                                                   stat.StatEffect(BuiltInStatType.WEIGHT_KG.name, delta_effect=20),
                                                   stat.StatEffect(BuiltInStatType.HEIGHT_M.name, delta_effect=.5),
                                               ]),
                                           category='RACE'),
    RaceType.ELF: stat.StatEffectPackage(id=RaceType.ELF.name, description="",
                                         stat_effects=frozenset([
                                                 stat.StatEffect(BuiltInStatType.STRENGTH.name, delta_effect=-10),
                                                 stat.StatEffect(BuiltInStatType.SPEED.name, delta_effect=15),
                                                 stat.StatEffect(BuiltInStatType.RATIONALITY.name, delta_effect=10),
                                                 stat.StatEffect(BuiltInStatType.MAGIC.name, delta_effect=5),
                                                 stat.StatEffect(BuiltInStatType.WEIGHT_KG.name, delta_effect=-20),
                                                 stat.StatEffect(BuiltInStatType.HEIGHT_M.name, delta_effect=.25),
                                             ]),
                                           category='RACE'),
    RaceType.DARK_ELF: stat.StatEffectPackage(id=RaceType.DARK_ELF.name, description="",
                                              stat_effects=frozenset([
                                                 stat.StatEffect(BuiltInStatType.STRENGTH.name, delta_effect=5),
                                                 stat.StatEffect(BuiltInStatType.SPEED.name, delta_effect=10),
                                                 stat.StatEffect(BuiltInStatType.MAGIC.name, delta_effect=-5),
                                                 stat.StatEffect(BuiltInStatType.WEIGHT_KG.name, delta_effect=-20),
                                                 stat.StatEffect(BuiltInStatType.HEIGHT_M.name, delta_effect=.25),
                                             ]),
                                           category='RACE'),
    RaceType.DWARF: stat.StatEffectPackage(id=RaceType.DWARF.name, description="",
                                           stat_effects=frozenset([
                                                      stat.StatEffect(BuiltInStatType.STRENGTH.name, delta_effect=15),
                                                      stat.StatEffect(BuiltInStatType.SPEED.name, delta_effect=-10),
                                                      stat.StatEffect(BuiltInStatType.MAGIC.name, delta_effect=-5),
                                                      stat.StatEffect(BuiltInStatType.WEIGHT_KG.name, delta_effect=15),
                                                      stat.StatEffect(BuiltInStatType.HEIGHT_M.name, delta_effect=-.5),
                                                  ]),
                                           category='RACE'),
}


def _verify_races_manifest():
    verify(lambda: all(x in races_manifest.keys() for x in RaceType),
           msg=f"Missing race(s) definitions: \n {[x for x in RaceType if x not in races_manifest.keys()]}")
_verify_races_manifest()



if __name__ == "__main__":
    pass



