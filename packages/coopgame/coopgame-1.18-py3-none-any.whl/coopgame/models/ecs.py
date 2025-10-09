from cooptools.register import Register
from typing import Protocol, Dict

class ComponentProtocol(Protocol):
    def on_update(self, delta_time: int, **kwargs):
        pass

class EntityComponentSystem:

    def __init__(self, components: Dict[str, ComponentProtocol] = None):
        self._component_registry = Register[ComponentProtocol]()

        if components is not None:
            self.register_components(components)

    def register_components(self, components: Dict[str, ComponentProtocol]):
        self._component_registry.register(list(components.values()), ids=list(components.keys()))

    def update(self, delta_time: int, **kwargs):
        for id, component in self._component_registry.Registry.items():
            component.on_update(delta_time, **kwargs)

    @property
    def Components(self) -> Dict[str, ComponentProtocol]:
        return self._component_registry.Registry

if __name__ == "__main__":
    class Health:
        def __init__(self):
            self.health = 0

        def on_update(self, delta_time, amount):
            self.health += amount

        def __repr__(self):
            return str(self.health)

    ecs = EntityComponentSystem({'health': Health()})

    print(ecs.Components)

    ecs.update(500, amount=5)

    print(ecs.Components)

