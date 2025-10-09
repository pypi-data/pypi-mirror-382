import time

from cooptools.register import Register
from coopgame.characterDevelopment import character as char
from typing import Iterable
from cooptools.typeProviders import StringProvider, resolve_string_provider
from cooptools.common import verify_val
import coopgame.characterDevelopment.stats as stat

class Community:
    def __init__(self,
                 name: str,
                 character_generator_options: Iterable[char.CharacterGeneratorArgs],
                 init_pop_size: int = None,
                 init_pop: Iterable[char.Character] = None):
        self.name: str = name
        self.character_registry = Register[char.Character]()
        self.global_effects_registry = Register[stat.StatEffectPackage]()
        self.char_generator_options = character_generator_options

        if init_pop_size is not None: self.add_new_characters(count=init_pop_size)
        if init_pop is not None: self.add_new_characters(new_characters=init_pop)

    def add_new_characters(self,
                           count: int = None,
                           new_characters: Iterable[char.Character] = None):
        if new_characters is not None:
            self.character_registry.register(new_characters, ids=[x.id for x in new_characters])

        if count is not None:
            verify_val(count, gte=0, error_msg=f"New character count {count} is invalid")
            self.add_new_characters(new_characters=[
                char.Character().generate()
                    args=rnd.choice(list(self.char_generator_options)))
                for x in range(count)
            ])




    def __repr__(self):
        chars_txt = "\n\t" + "\n\t".join([f"{ii}: {x}" for ii, x in enumerate(self.character_registry.Registry.values())])
        return f"Community Name: {self.name}" \
               f"\nCharacters: {chars_txt}"


if __name__ == "__main__":
    from cooptools.randoms import a_string
    import random as rnd
    import coopgame.characterDevelopment.stat_modifier_manifest as smm
    from coopgame.characterDevelopment.behaviorExtensions import traits as traits

    character_naming_provider = lambda: a_string(10)

    default_stats = [
        stat.StatState('hp', val=1000, meta=stat.StatMeta(0, 1000)),
        stat.StatState('mana', val=100, meta=stat.StatMeta(0, 100)),
        stat.StatState('rage', val=0, meta=stat.StatMeta(0, 100))
    ]

    config_fn_provider = r'C:\Users\tburns\PycharmProjects\coopgame\coopgame\characterDevelopment\manifest.json'
    char_gen_options = [
        char.CharacterGeneratorArgs(
            name_provider=character_naming_provider,
            init_stats_package=stat.StatsPackageState(
                base_stats=stat.StatStates({x.stat_name: x for x in default_stats})
            ),
            traits_manifest=stat.StatEffectPackageManifest.from_config_data(config_fn_provider)
        ) for k, v in smm.races_manifest.items()
    ]

    my_community = Community(name='c1',
                             character_generator_options=char_gen_options,
                             init_pop_size=10)

    active_global_events = []

    # Eventually, this should become some sort of "World" class
    epoch = 0
    while True:
        epoch += 1
        p_global_event_occurs = 0.35
        p_global_event_ends = 0.15
        p_char_gain_personality_trait = 0.10
        p_char_gain_physical_trait = 0.05
        p_char_lose_personality_trait = 0.01
        p_char_lose_physical_trait = 0.01

        # handle global event(s)
        for x in active_global_events:
            if rnd.random() < p_global_event_ends:
                active_global_events.remove(x)

        if rnd.random() < p_global_event_occurs:
            active_global_events.append(smm.global_effect_manifest[rnd.choice(list(smm.GlobalEffect))])

        for k, v in my_community.character_registry.Registry.items():
            # add new personality traits:
            if rnd.random() < p_char_gain_personality_trait:
                traits.acquire_traits(v,
                                      traits=[smm.personality_trait_manifest[rnd.choice(list(smm.PersonalityTrait))]])

            # add new physical traits:
            if rnd.random() < p_char_gain_personality_trait:
                traits.acquire_traits(v,
                                      traits=[smm.physical_trait_manifest[rnd.choice(list(smm.PhysicalTrait))]])

        print(my_community)
        time.sleep(1)


