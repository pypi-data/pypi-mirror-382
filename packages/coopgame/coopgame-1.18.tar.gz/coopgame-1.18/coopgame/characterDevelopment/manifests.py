from dataclasses import dataclass, asdict
from typing import Dict, List, Iterable
import random as rnd
from cooptools.config import JsonConfigHandler
from cooptools.typeProviders import StringProvider, resolve_string_provider

@dataclass(frozen=True)
class MutuallyExclusiveManifest:
    options: Dict[str, List]

    def random(self,
               type: str = None,
               excluded_types: Iterable[str] = None
               ):

        available_types = [x for x in self.options.keys() if excluded_types is None or x not in excluded_types]
        if len(available_types) == 0:
            return None, None

        if type is None: type = rnd.choice(available_types)

        return (type, rnd.choice(self.options[type]))

    @classmethod
    def from_config(cls,
                    config_file_name_provider: StringProvider,
                    key: str):
        config = JsonConfigHandler(file_path_provider=config_file_name_provider)
        data = config.resolve(key)

        return MutuallyExclusiveManifest(
            options=data
        )





if __name__ == '__main__':
    manifest = MutuallyExclusiveManifest(
        options={
            'beauty': 'Ugly / Plain / Attractive / Beautiful'.split(' / '),
            'strength': 'Puny / Weak / Strong / Mighty'.split(' / '),
            'height': 'Dwarf / Short / Tall / Giant'.split(' / '),
            'weight': 'Skinny / Thin / Stout / Obese'.split(' / ')
        }
    )

    used_types = []
    for i in range(10):
        type, choice = manifest.random(excluded_types=used_types)
        used_types.append(type)
        print(type, choice)



