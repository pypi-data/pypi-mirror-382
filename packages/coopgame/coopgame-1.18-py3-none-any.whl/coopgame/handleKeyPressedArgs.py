from dataclasses import dataclass
from typing import Dict, Tuple, List, Callable, Any
import pygame
import pygame.event

from coopgame.pygame_k_constant_names import PyKeys, PyMouse, InputType
from cooptools.decor import try_handler
from coopgame.logger import logger
from cooptools.coopEnum import CoopEnum, auto

class InputEventType(CoopEnum):
    DOWN = auto()
    UP = auto()
    HELD = auto()
    HOVER = auto()

SupportedInput = PyKeys | PyMouse

@dataclass(frozen=True, slots=True, eq=True)
class InputEvent:
    input_key: SupportedInput
    event_type: InputEventType = InputEventType.DOWN

    @property
    def InputType(self):
        if type(self.input_key) == PyKeys:
            return InputType.KEYBOARD
        elif type(self.input_key) == PyMouse:
            return InputType.MOUSE
        else:
            raise TypeError(f"Unhandled input type {self.input_key}")

    def with_event_type(self, event_type: InputEventType):
        return InputEvent(
            input_key=self.input_key,
            event_type=event_type
        )

class InputState:
    def __init__(self,
                 delta_ms: int,
                 events: List[InputEvent] = None
                ):
        # init
        self._index: int = -1
        self._delta_ms: int = delta_ms
        self._events: Dict[int, InputEvent] = {}
        self._mouse_pos = None

        # register events that have been provided
        if events is not None:
            self.register(events)

        # Get currently pressed keys
        keys = pygame.key.get_pressed()
        self.register(events=
                      [InputEvent(event_type=InputEventType.HELD,
                                  input_key=x) for x in PyKeys if keys[x.value]]
        )

        # Get currently pressed Mouse
        self.register(events=
                      [InputEvent(event_type=InputEventType.HELD,
                                  input_key=PyMouse.by_val(ii+1)) for ii, x in enumerate(pygame.mouse.get_pressed()) if x is True]
        )

        # Register Mouse Pos Event
        self.register(events=[
            InputEvent(event_type=InputEventType.HOVER,
                       input_key=PyMouse.POSITION)
        ])

    def _get_next_index(self):
        self._index += 1
        return self._index

    def __iter__(self):
        for x, v in self._events.items():
            yield v

    def register(self,
                 events: List[InputEvent] =None,
                 mouse_pos: Tuple[float, float] = None):
        if events is not None:
            # delete any HELD (dont want both a MU and MH event in same iteration)
            for event in events:
                held_ = event.with_event_type(event_type=InputEventType.HELD)
                if held_ in self._events.values():
                    self._events = {k: v for k, v in self._events.items() if v != held_}

            # capture events
            for event in events:
                self._events[self._get_next_index()] = event

        if mouse_pos is not None:
            self._mouse_pos = mouse_pos

    @property
    def KeyDownEvents(self) -> List[PyKeys]:
        return [x.input_key for x in self._events.values() if x.InputType == InputType.KEYBOARD and x.event_type == InputEventType.DOWN]

    @property
    def KeyUpEvents(self) -> List[PyKeys]:
        return [x.input_key for x in self._events.values() if x.InputType == InputType.KEYBOARD and x.event_type == InputEventType.UP]

    @property
    def MouseDownEvents(self) -> List[PyMouse]:
        return [x.input_key for x in self._events.values() if x.InputType == InputType.MOUSE and x.event_type == InputEventType.DOWN]

    @property
    def MouseUpEvents(self) -> List[PyMouse]:
        return [x.input_key for x in self._events.values() if x.InputType == InputType.MOUSE and x.event_type == InputEventType.UP]

    @property
    def MouseHeld(self) -> List[PyMouse]:
        return [x.input_key for x in self._events.values() if x.InputType == InputType.MOUSE and x.event_type == InputEventType.HELD]

    @property
    def KeysHeld(self) -> List[PyMouse]:
        return [x.input_key for x in self._events.values() if x.InputType == InputType.KEYBOARD and x.event_type == InputEventType.HELD]

    @property
    def Events(self) -> List[InputEvent]:
        return list(self._events.values())

    @property
    def DeltaEvents(self) -> List[InputEvent]:
        return [x for x in self._events.values() if x.event_type in [InputEventType.UP, InputEventType.DOWN]]

    @property
    def DeltaMs(self) -> int:
        return self._delta_ms

    @property
    def MousePos(self) -> Tuple[float, float]:
        return self._mouse_pos

    def __repr__(self):
        return f"deltaMs: {self._delta_ms}, MU: {self.MouseUpEvents}, MD: {self.MouseDownEvents}, KU: {self.KeyUpEvents}, KD:{self.KeyDownEvents}, MH: {self.MouseHeld}, KH:{self.KeysHeld}"

def pygame_event_handler(inp_state: InputState, event: pygame.event.Event):
    if event.type == pygame.KEYDOWN:
        inp_state.register(events=[InputEvent(event_type=InputEventType.DOWN, input_key=PyKeys.by_val(event.key))])
    elif event.type == pygame.MOUSEBUTTONDOWN:
        inp_state.register(events=[InputEvent(event_type=InputEventType.DOWN, input_key=PyMouse.by_val(event.button))])
    elif event.type == pygame.KEYUP:
        inp_state.register(events=[InputEvent(event_type=InputEventType.UP, input_key=PyKeys.by_val(event.key))])
    elif event.type == pygame.MOUSEBUTTONUP:
        inp_state.register(events=[InputEvent(event_type=InputEventType.UP, input_key=PyMouse.by_val(event.button))])

    return inp_state

InputCallback = Callable[[InputState], Any]


@dataclass(frozen=True, slots=True, eq=True)
class InputAction:
    input_events: List[InputEvent]
    callback: InputCallback
    description: str = None

@dataclass(frozen=True)
class CallbackPackage:
    down: InputCallback = None
    up: InputCallback = None
    held: InputCallback = None
    hover: InputCallback = None

    def actions(self, keys: List[SupportedInput]) -> List[InputAction]:
        ret = []

        for key in keys:
            if self.down is not None:
                ret.append(InputAction(input_events=[InputEvent(input_key=key,
                                                                event_type=InputEventType.DOWN)],
                                       callback=self.down))

            if self.up is not None:
                ret.append(InputAction(input_events=[InputEvent(input_key=key,
                                                                event_type=InputEventType.UP)],
                                       callback=self.up))
            if self.held is not None:
                ret.append(InputAction(input_events=[InputEvent(input_key=key,
                                                                event_type=InputEventType.HELD)],
                                       callback=self.held))

            if self.hover is not None:
                ret.append(InputAction(input_events=[InputEvent(input_key=key,
                                                                event_type=InputEventType.HOVER)],
                                       callback=self.hover))

        return ret

class InputStateHandler:
    def __init__(self,
                 key_actions: List[InputAction] = None,
                 quit_callback_package: CallbackPackage = None,
                 debug_callback_package: CallbackPackage = None,
                 fullscreen_callback_package: CallbackPackage = None
                 ):
        self._input_actions: Dict[List[Tuple[SupportedInput]], InputAction] = {}

        to_register = key_actions if key_actions is not None else []
        if quit_callback_package is not None:
            to_register += quit_callback_package.actions([PyKeys.K_ESCAPE])

        if debug_callback_package is not None:
            to_register += debug_callback_package.actions([PyKeys.K_F12])

        if fullscreen_callback_package is not None:
            to_register += fullscreen_callback_package.actions([PyKeys.K_F11])

        self.register_key_actions(to_register)

    @property
    def InputActions(self):
        return self._input_actions

    def register_key_actions(self, key_actions: List[InputAction]):
        self._input_actions = {**self._input_actions, **{tuple(x.input_events): x for x in key_actions}}

    @staticmethod
    def _handle_callback(input_action, input_state):
        logger.info(f"Handling callback for input_action {input_action} with state {input_state}")
        input_action.callback(input_state)


    @try_handler(logger=logger)
    def handle_input(self, input_state: InputState):

        # log state
        if len(input_state.Events) > 0:
            logger.debug(input_state)

        if len(input_state.DeltaEvents) > 0:
            logger.info(f"Pressed Keys: [{','.join([x.input_key.name for x in input_state.DeltaEvents if x.event_type==InputEventType.DOWN])}] "
                        f"Released Keys: [{','.join([x.input_key.name for x in input_state.DeltaEvents if x.event_type==InputEventType.UP])}]")

        # handle input
        for input_action in self._input_actions.values():
            # if, by chance a trigger button was pressed twice in one input_state, make sure to handle the callback twice
            triggers = [x for x in input_action.input_events if x.event_type in [InputEventType.UP, InputEventType.DOWN]]
            trigger_count = len(triggers)
            n_times = trigger_count if trigger_count > 1 else 1

            # check to make sure all events have occurred
            if all(x in input_state.Events for x in input_action.input_events):
                for n in range(n_times):
                    self._handle_callback(input_action=input_action, input_state=input_state)

        # # handle hover over
        # if input_state.MousePos is not None and self._hover_callback is not None:
        #     MonitoredClassTimer.timer(self._hover_callback(input_state))

def basic_key_actions(
        up_package: CallbackPackage = None,
        down_package: CallbackPackage = None,
        left_package: CallbackPackage = None,
        right_package: CallbackPackage = None,
        rot_left_package: CallbackPackage = None,
        rot_right_package: CallbackPackage = None,
        scale_up_package: CallbackPackage = None,
        scale_down_package: CallbackPackage = None,
        quit_package: CallbackPackage = None,
        fullscreen_package: CallbackPackage = None,
        debug_mode_package: CallbackPackage = None,
        pause_package: CallbackPackage = None,
        runspeed_package: (CallbackPackage, CallbackPackage) = None,
        help_package: CallbackPackage = None
) -> List[InputAction]:
    ret: List[InputAction] = []

    if up_package:
        ret += up_package.actions(keys=[PyKeys.K_UP, PyKeys.K_w, PyKeys.K_KP8])

    if down_package:
        ret += down_package.actions(keys=[PyKeys.K_DOWN, PyKeys.K_s, PyKeys.K_KP2])

    if left_package:
        ret += left_package.actions(keys=[PyKeys.K_LEFT, PyKeys.K_a, PyKeys.K_KP4])

    if right_package:
        ret += right_package.actions(keys=[PyKeys.K_RIGHT, PyKeys.K_d, PyKeys.K_KP6])

    if rot_left_package:
        ret += rot_left_package.actions(keys=[PyKeys.K_q, PyKeys.K_COMMA, PyKeys.K_PAGEUP])

    if rot_right_package:
        ret += rot_right_package.actions(keys=[PyKeys.K_e, PyKeys.K_PERIOD, PyKeys.K_PAGEDOWN])

    if scale_up_package:
        ret += scale_up_package.actions(keys=[PyKeys.K_PLUS, PyKeys.K_EQUALS, PyKeys.SCROLLUP, PyKeys.K_KP_PLUS])

    if scale_down_package:
        ret += scale_down_package.actions(keys=[PyKeys.K_MINUS, PyKeys.SCROLLDOWN, PyKeys.K_KP_MINUS])

    if quit_package:
        ret += quit_package.actions(keys=[PyKeys.K_ESCAPE])

    if fullscreen_package:
        ret += fullscreen_package.actions(keys=[PyKeys.K_F12])

    if debug_mode_package:
        ret += debug_mode_package.actions(keys=[PyKeys.K_F11])

    if pause_package:
        ret += pause_package.actions(keys=[PyKeys.K_p])

    if runspeed_package:
        ret += runspeed_package[0].actions(keys=[PyKeys.K_PLUS, PyKeys.K_EQUALS])
        ret += runspeed_package[1].actions(keys=[PyKeys.K_MINUS])

    if help_package:
        ret += help_package.actions(keys=[PyKeys.K_h])

    return ret


