from dataclasses import dataclass, field, asdict
from typing import List, Dict, Iterable, Callable
import uuid
import coopgame.characterDevelopment.stats as stat
from cooptools.transform import Transform
from cooptools.typeProviders import StringProvider, resolve_string_provider

NameProvider = Callable[[str], str] | StringProvider

@dataclass(frozen=True, slots=True)
class CharacterGeneratorArgs:
    name_provider: NameProvider
    init_stats_package: stat.StatsPackageState
    traits_manifest: stat.StatEffectPackageManifest

@dataclass(frozen=True, slots=True)
class Opinion:
    factors: Dict[str, float]

    @property
    def Score(self):
        return sum(self.factors.values())


class Character:
    def __init__(self,
                name_provider: NameProvider,
                init_stats: stat.StatsPackageState,
                traits: Iterable[stat.StatEffectPackage]=None):
        self.id = str(uuid.uuid4())
        self.stats: stat.StatsPackageCommandController=stat.StatsPackageCommandController()\
            .init_stats(stat_args=init_stats.base_stats.stats.values())
        self.transform: Transform=Transform()
        self.stats.acquire_stat_effect_packages(stat_effect_packages=traits)
        self.name: str=self._resolve_name(name_provider)

    def __repr__(self):
        return f"{self.name}, [{self.id}] ({', '.join([x.id for x in self.stats.State.stat_modifiers])})"

    @classmethod
    def generate(self,
                 args: CharacterGeneratorArgs,
                 trait_count_args: Dict[str, int]):
        traits = []

        for trait_type, count in trait_count_args.items():
            used = []
            for ii in range(count):
                type, choice = args.traits_manifest.stat_effect_type_manifests[trait_type].random(excluded_types=used)
                used.append(type)
                traits.append(choice)

        return Character(
            name_provider=args.name_provider,
            init_stats=args.init_stats_package,
            traits=traits
        )

    def _resolve_name(self, name_provider: NameProvider):
        try:
            return name_provider(self.Race.id)
        except:
            return resolve_string_provider(name_provider)

    def opinon_of(self, character) -> Opinion:
        if type(character) != Character:
            raise TypeError(f"Cannot calculate opinion of type {type(character)}")

        factors = {}
        for stat_package in self.stats.State.stat_modifiers:
            if stat_package.stat_opinions is None:
                deb = True
            for trait, effect in stat_package.stat_opinions.items():
                if trait in character.stats.State.stat_modifiers:
                    factors[trait] = effect

        return Opinion(
            factors=factors
        )

    @property
    def Race(self):
        ret = next((i for i in self.stats.State.stat_modifiers if i.category == 'race'), None)
        return ret

if __name__ == "__main__":
    from pprint import pprint

    config_fn_provider = r'C:\Users\tburns\PycharmProjects\coopgame\coopgame\characterDevelopment\manifest.json'
    me = Character.generate(
        args=CharacterGeneratorArgs(
            name_provider="Ralphius",
            init_stats_package=stat.StatsPackageState.from_config(config_fn_provider),
            traits_manifest=stat.StatEffectPackageManifest.from_config_data(config_fn_provider)
        ),
        trait_count_args={
            "personality_traits": 3,
            "physical_traits": 2,
            "race": 1
        }
    )

    # pprint(me.stats.State.Summary)
    pprint(me)
    me.stats.register_events(events=[
        stat.DeltaStatStatsPackageStateEvent(stat_name='HP', delta=-19),
        stat.StatsPackageStateEvent(description="character gained rage",
                                    added_stat_modifiers=[
                            stat.StatEffectPackage(
                                stat_effects=frozenset([
                                    stat.StatEffect(stat_name='rage', delta_effect=5)]),
                                id='Enraged'
                            )
                                    ],

                                    )
    ])

    pprint(me)
    pprint(me.stats.State.Summary)

    print(f"All My Events:")
    pprint(me.stats.Events)