from dataclasses import dataclass, field, asdict, fields, _MISSING_TYPE
from typing import Dict, Iterable, List
from cooptools.common import verify_val, bound_value, verify
import uuid
from cooptools.commandDesignPattern import CommandController, CommandProtocol
import datetime
import cooptools.date_utils as du
import cooptools.config as conf
import cooptools.os_manip as osm
from cooptools.typeProviders import StringProvider, resolve_string_provider
from coopgame.characterDevelopment.manifests import MutuallyExclusiveManifest

@dataclass(frozen=True, slots=True)
class StatMeta:
    min: float = None
    max: float = None

@dataclass(frozen=True, slots=True)
class StatState:
    stat_name: str
    val: float
    description: str = field(default="")
    meta: StatMeta = None

    def with_(self,
            stat_name: str = None,
            val: float = None,
            meta: StatMeta = None
    ):
        obj_dict = asdict(self)

        obj_dict.update({k: v for k, v in {
            f'{self.stat_name=}'.split('=')[0].replace('self.', ''): stat_name,
            f'{self.val=}'.split('=')[0].replace('self.', ''): val,
            f'{self.meta=}'.split('=')[0].replace('self.', ''): meta,
        }.items() if v is not None})

        return StatState(**obj_dict)

    def __post_init__(self):
        if type(self.meta) == dict:
            object.__setattr__(self, f'{self.meta=}'.split('=')[0].replace('self.', ''), StatMeta(**self.meta))

        verify_val(self.val, gte=self.meta.min, lte=self.meta.max)



@dataclass(frozen=True, slots=True)
class StatEffect:
    stat_name: str
    new_name: str = None
    set_effect: float = None
    delta_effect: float = None
    new_meta: StatMeta = None

    @classmethod
    def from_delta(cls, name: str, delta: float):
        return StatEffect(stat_name=name, delta_effect=delta)

    def with_(self,
        stat_name: str=None,
        new_name: str = None,
        set_effect: float = None,
        delta_effect: float = None,
        new_meta: StatMeta = None,
    ):
        obj_dict = asdict(self)

        obj_dict.update({k: v for k, v in {
            f'{self.stat_name=}'.split('=')[0].replace('self.', ''): stat_name,
            f'{self.new_name=}'.split('=')[0].replace('self.', ''): new_name,
            f'{self.set_effect=}'.split('=')[0].replace('self.', ''): set_effect,
            f'{self.delta_effect=}'.split('=')[0].replace('self.', ''): delta_effect,
            f'{self.new_meta=}'.split('=')[0].replace('self.', ''): new_meta,
        }.items() if v is not None})

        return StatEffect(**obj_dict)

    def opposite(self):
        return self.with_(
            delta_effect=-self.delta_effect
        )

    def apply(self, current_state: StatState) -> StatState:
        if not verify(lambda: self.stat_name==current_state.stat_name, msg=f"Cannot apply effect to stat: {self.stat_name} != {current_state.stat_name}", block=False):
            return current_state

        new = self.set_effect if self.set_effect is not None else current_state.val
        new += self.delta_effect if self.delta_effect is not None else 0

        return current_state.with_(
            stat_name=self.new_name,
            val=bound_value(val=new, gte=current_state.meta.min, lte=current_state.meta.max) if any([self.set_effect, self.delta_effect]) else None,
            meta=self.new_meta
        )

    def summary(self)-> Dict:
        raw = asdict(self)
        raw[f'{self.new_meta=}'.split('=')[0].replace('self.', '')] = asdict(self.new_meta) if self.new_meta else None

        return {k: v for k, v in raw.items() if v is not None}

@dataclass(frozen=True, slots=True)
class StatStates:
    stats: Dict[str, StatState] = field(default_factory=dict)

    def init_new_stat(self,
                  state: StatState):
        new_stats = self.stats
        new_stats[state.stat_name] = state

        return StatStates(
            stats=new_stats
        )

    def with_(self,
              stat_effects: Iterable[StatEffect]=None):
        if stat_effects is None:
            return self

        new_stats = self.stats
        for effect in stat_effects:
            if effect.stat_name not in new_stats.keys() and effect.set_effect is None and effect.new_meta is None:
                raise ValueError(f"Cannot set a new stat {effect} without a default value for effect.set_effect and effect.new_meta")
            if effect.stat_name not in new_stats.keys():
                self.init_new_stat(state=StatState(
                    stat_name=effect.stat_name,
                    val=effect.set_effect,
                    meta=effect.new_meta
                ))

            new_stats[effect.stat_name] = effect.apply(self.stats[effect.stat_name])


        if len(new_stats) == 0:
            deb = True
        return StatStates(
            stats=new_stats
        )

    @property
    def Stats(self)-> Dict[str, StatState]:
        return self.stats

    @property
    def Summary(self)-> Dict[str, float]:
        return {
            k: v.val for k, v in self.stats.items()
        }

@dataclass(frozen=True, slots=True)
class StatEffectPackage:
    stat_effects: frozenset[StatEffect]
    description: str = field(default="")
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    category: str = field(default='DEFAULT')
    stat_opinions: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        if type(self.stat_effects) == dict:
            object.__setattr__(self, f'{self.stat_effects=}'.split('=')[0].replace('self.', ''), frozenset([StatEffect(**x) for x in self.stat_effects.values()]))

        if self.stat_opinions is None:
            object.__setattr__(self, f'{self.stat_opinions=}'.split('=')[0].replace('self.', ''), {})

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return hash(other) == hash(self)

    def summary(self) -> Dict:
        raw = asdict(self)

        raw[f'{self.stat_effects=}'.split('=')[0].replace('self.', '')] = [x.summary() for x in self.stat_effects]

        return {k: v for k, v in raw.items() if v is not None}

    def with_opposite_stat_effects(self, id: str = None, description: str = None):
        new = [x.opposite() for x in self.stat_effects]

        if description is None: description = f"[OPPOSITE OF] {self.description}"
        return StatEffectPackage(
            stat_effects=frozenset(new),
            description=description,
            category=self.category,
            id=id
        )

class StatEffectPackageManifest:
    def __init__(self, manifests: Dict[str, MutuallyExclusiveManifest] = None):
        self.stat_effect_type_manifests: Dict[str, MutuallyExclusiveManifest] = manifests if manifests is not None else {}

    @classmethod
    def from_config_data(self, config_file_name_provider: StringProvider):
        config = conf.JsonConfigHandler(file_path_provider=config_file_name_provider,
                                        file_creation_args=conf.FileCreationArgs(fileType=osm.FileType.JSON))
        traits_types: Dict[str, Dict] = config.resolve('traits')
        trait_details: Dict[str, Dict] = config.resolve('trait_details')

        traits = {
            k: StatEffectPackage(stat_effects=frozenset([StatEffect(stat_name=name,
                                                                   delta_effect=val) for name, val in v.get('stat_effects', {}).items()]),
                                 id=k,
                                 category=next(type for type, options in traits_types.items()
                                               if any(k in option_lst for option_lst in options.values())),
                                 stat_opinions=v.get('trait_opinions', None)
                                 )
            for k, v in trait_details.items()
        }

        stat_effect_type_manifests = {
            trait_type: MutuallyExclusiveManifest(
                options={
                    k: [traits[v] for v in options] for k, options in trait_relationship.items()
                }) for trait_type, trait_relationship in traits_types.items()
        }
        return StatEffectPackageManifest(
            manifests=stat_effect_type_manifests
        )

@dataclass(frozen=True, slots=True)
class StatsPackageState:
    base_stats: StatStates = field(default_factory=StatStates)
    stat_modifiers: frozenset[StatEffectPackage] = field(default_factory=frozenset)

    def with_(self,
              base_stat_effect_modifications: StatEffectPackage=None,
              added_modifiers: Iterable[StatEffectPackage] = None,
              removed_modifiers: Iterable[StatEffectPackage] = None,
              ):

        # update skills set
        new_skills = set(self.stat_modifiers)
        new_skills.update(added_modifiers)
        new_skills = [x for x in new_skills if x not in removed_modifiers]

        base_stat_effects = base_stat_effect_modifications.stat_effects if base_stat_effect_modifications is not None else None

        return StatsPackageState(
            base_stats=self.base_stats.with_(
                stat_effects=base_stat_effects
            ),
            stat_modifiers=frozenset(new_skills)
        )

    def resolve_stat(self,
                     stat_name: str,
                     external_stat_modifiers: Iterable[StatEffectPackage] = None) -> StatState:
        stat = self.base_stats.Stats[stat_name]

        all_mods = list(self.stat_modifiers) + (list(external_stat_modifiers) if external_stat_modifiers is not None else [])

        for mod in all_mods:
            for stat_effect in mod.stat_effects:
                stat = stat_effect.apply(stat)

        return stat

    @classmethod
    def from_config(self, config_file_name_provider: StringProvider):
        config = conf.JsonConfigHandler(file_path_provider=config_file_name_provider,
                                   file_creation_args=conf.FileCreationArgs(fileType=osm.FileType.JSON))

        stats: Dict[str, Dict] = config.resolve('stats')

        return StatsPackageState(
            base_stats=StatStates(stats={k: StatState(stat_name=k,
                                                      val=v['base_val'],
                                                      meta=StatMeta(min=v['min_val'] if 'min_val' in v.keys() else None,
                                                                    max=v['max_val'] if 'max_val' in v.keys() else None),
                                                      description=v["description"]) for k, v in stats.items()})
        )



    @property
    def InternallyResolvedStats(self) -> StatStates:
        return StatStates(
            stats={x: self.resolve_stat(
                x) for x in self.BaseStats.stats.keys()}
        )

    @property
    def BaseStats(self) -> StatStates:
        return self.base_stats

    @property
    def StatModifiers(self) -> List[StatEffectPackage]:
        return list(self.stat_modifiers)

    @property
    def Summary(self) -> Dict:
        return {
            'base_stats': self.BaseStats.Summary,
            'stat_modifiers': [x.summary() for x in self.stat_modifiers],
            'internally_resolved_stats': self.InternallyResolvedStats.Summary,
        }


class StatsPackageStateEvent(CommandProtocol):
    def __init__(self,
                 description: str,
                 base_stat_modifiers: StatEffectPackage=None,
                 added_stat_modifiers: Iterable[StatEffectPackage]=None,
                 removed_stat_modifiers: Iterable[StatEffectPackage]=None,
                 date: datetime.datetime = None,
                 id: str = None
                 ):
       self.description: str = description
       self.base_stat_modifiers: StatEffectPackage = base_stat_modifiers
       self.added_stat_modifiers: List[StatEffectPackage] = list(added_stat_modifiers) if added_stat_modifiers is not None else []
       self.removed_stat_modifiers: List[StatEffectPackage] = list(removed_stat_modifiers) if removed_stat_modifiers is not None else []
       self.date: datetime.datetime = date if date is not None else du.today(remove_ms=True)
       self.id: str = id if id is not None else str(uuid.uuid4())

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __repr__(self):
        return f"""{self.date} - {self.description} [{self.id}]
                    \tbase_stat_modifiers: {self.base_stat_modifiers}
                    \tadded_stat_modifiers: {self.added_stat_modifiers}
                    \tremoved_stat_modifiers: {self.removed_stat_modifiers}"""

    def execute(self, state: StatsPackageState):
        return state.with_(
            base_stat_effect_modifications=self.base_stat_modifiers,
            added_modifiers=self.added_stat_modifiers,
            removed_modifiers=self.removed_stat_modifiers
        )

class InitStatStatsPackageStateEvent(StatsPackageStateEvent):
    def __init__(self,
                 stat_args: Iterable[StatState]
                 ):
        super().__init__(
            description="Init Char Stats",
            base_stat_modifiers=StatEffectPackage(
                stat_effects=frozenset([StatEffect(v.stat_name,
                                                        set_effect=v.val,
                                                        new_meta=v.meta) for v in stat_args]))
        )

class DeltaStatStatsPackageStateEvent(StatsPackageStateEvent):
    def __init__(self,
                 stat_name: str,
                 delta: float,
                 description: str=None):
        if description is None: description = f"Adjust [{stat_name}] by {delta}"
        super().__init__(
            description=description,
            base_stat_modifiers=StatEffectPackage(
                stat_effects=frozenset([StatEffect(stat_name, delta_effect=delta)]))
            )


class StatsPackageCommandController:
    def __init__(self,
                 init_stats_package_state: StatsPackageState = None):
        self._init_state = StatsPackageState()
        self._event_command_controller: CommandController = CommandController(init_state=self._init_state, cache_interval=10)
        self.id = str(uuid.uuid4())

        if init_stats_package_state is not None:
            self.init_stats(init_stats_package_state.base_stats.stats.values())
            self.acquire_stat_effect_packages(init_stats_package_state.stat_modifiers)


    def __repr__(self):
        return str(self._event_command_controller.State)

    def register_events(self, events: Iterable[StatsPackageStateEvent]):
        self._event_command_controller.execute(commands=list(events))

    @property
    def State(self) -> StatsPackageState:
        return self._event_command_controller.State

    @property
    def Events(self) -> List[StatsPackageStateEvent]:
        return self._event_command_controller.command_store.get_commands()

    def init_stats(self,
                    stat_args: Iterable[StatState]
                   ):
        self.register_events(events=[InitStatStatsPackageStateEvent(stat_args)])
        return self

    def acquire_stat_effect_packages(self, stat_effect_packages: Iterable[StatEffectPackage]):
        self.register_events(events=[StatsPackageStateEvent(description="Add Stat Effect Package",
                                                            added_stat_modifiers=stat_effect_packages)])
        return self

    def lose_stat_effect_packages(self, stat_effect_packages: Iterable[StatEffectPackage]):
        self.register_events(events=[StatsPackageStateEvent(description="Add Traits",
                                                            removed_stat_modifiers=stat_effect_packages)])
        return self

if __name__ == "__main__":
    from pprint import pprint
    import coopgame.characterDevelopment.race_manifest as rm
    import coopgame.characterDevelopment.stat_modifier_manifest as smm

    def test1():
        spcc = StatsPackageCommandController()\
            .init_stats([
                StatState('hp', val=1000, meta=StatMeta(0, 1000)),
                StatState('mana', val=100, meta=StatMeta(0, 100)),
                StatState('rage', val=0, meta=StatMeta(0, 100))
            ])


        pprint(spcc.State.Summary)

        spcc.register_events(events=[
            DeltaStatStatsPackageStateEvent(stat_name='hp', delta=-19),
            StatsPackageStateEvent(description="character gained rage",
                                        added_stat_modifiers=[
                                StatEffectPackage(stat_effects=frozenset([
                                   StatEffect(stat_name='rage', delta_effect=5)]))
                            ]
                                        )
        ])

        pprint(spcc.State.Summary)
        print(f"All My Events:")
        pprint(spcc.Events)

    def test2():
        config_fn_provider = r'C:\Users\tburns\PycharmProjects\coopgame\coopgame\characterDevelopment\manifest.json'
        manif = StatEffectPackageManifest.from_config_data(config_file_name_provider=config_fn_provider)
        used_types = []

        for trait_type, trait_manif in manif.stat_effect_type_manifests.items():
            for i in trait_manif.options:
                type, choice = trait_manif.random(excluded_types=used_types)
                used_types.append(type)
                print(type, choice.id if choice else None)

    # test1()
    test2()
