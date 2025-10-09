import logging
import threading

import numpy as np
import pygame
from coopstructs.geometry import Rectangle
from cooptools.colors import Color
from coopgame.pygbutton import PygButton
from cooptools.decor import timer, try_handler

from typing import Callable, List, Dict, Optional, Any
import coopgame.pygamehelpers as help
from coopgame.spriteHandling.sprites import AnimatedSprite
from coopstructs.geometry import Rectangle as cRect
from coopgame.monitoredClassLogger import MonitoredClassLogger
from cooptools.coopEnum import CoopEnum
from enum import auto
from coopgame.pygame_k_constant_names import PyKeys, PyMouse
from coopgame.gameTimeTracker import GameTimeTracker
from cooptools.toggles import BooleanToggleable, IntegerRangeToggleable
from cooptools.timedDecay import Timer
from coopgame.label_drawing.pyLabel import TextAlignmentType
from coopgame.handleKeyPressedArgs import basic_key_actions, InputState, InputStateHandler, InputEvent, InputEventType, CallbackPackage, InputAction
from coopgame.logger import logger
from cooptools.decor import TimeableProtocol
import coopgame.label_drawing.label_drawing_utils as labutils
from cooptools.coopEnum import CardinalPosition
import time

DEBUG_COLORKEY = Color.DARK_SLATE_GRAY
DEBUGGER_MASK_ALPHA = 65
key_mapper = Callable[[InputState], Any]
DEBUG_LABEL_ARGS = labutils.DrawLabelArgs(
    color=Color.LEMON_CHIFFON
)

class BuiltInSurfaceType(CoopEnum):
    BACKGROUND = auto()
    FOREGROUND = auto()
    HELP = auto()
    DEBUGGER = auto()
    DEBUGGER_MASK = auto()

class TimeTracker(TimeableProtocol):
    def __init__(self):
        self.internally_tracked_times = {}

tt = TimeTracker()

TransformMatrixProvider: Callable[[], np.array]


class GameTemplate:

    def __init__(self,
                 fullscreen: bool = False,
                 screen_width: int = 1000,
                 screen_height: int = 500,
                 max_fps: int = 120,
                 debug_mode=False,
                 input_state_handler: InputStateHandler = None,
                 log_stats_interval_ms: int = 5000,
                 help_on_init: bool = False,
                 start_paused: bool = False):
        self.init_screen_width = screen_width
        self.init_screen_height = screen_height
        self.log_stats_interval_ms = log_stats_interval_ms

        self._lock = threading.RLock()

        self.fullscreen = fullscreen
        self.screen: pygame.Surface = None
        self._init_screen(self.fullscreen, self.screen_width, self.screen_height)
        self._monitored_class_logger = MonitoredClassLogger()

        self.debug_mode_toggle = BooleanToggleable(default=debug_mode)
        self.help_toggle = BooleanToggleable(default=help_on_init)
        self.paused_toggle = BooleanToggleable(default=start_paused)
        self.run_speed = IntegerRangeToggleable(min=1, max=10, starting_value=1)
        self.input_state_handler = input_state_handler if input_state_handler is not None else \
            InputStateHandler(key_actions=self.default_key_actions())

        self.game_time_tracker = GameTimeTracker(max_fps=max_fps)

        self.running = False

        self.buttons = {}
        self.sprites = {}

        # build in surfaces
        self.built_in_surfaces: Dict[BuiltInSurfaceType, Optional[pygame.Surface]] = {
            BuiltInSurfaceType.BACKGROUND: None,
            BuiltInSurfaceType.FOREGROUND: None,
            BuiltInSurfaceType.HELP: None,
            BuiltInSurfaceType.DEBUGGER: None
        }

        self.game_time_tracker.set_start()
        self.start_timers()
        # self.log_stats_refresher = DataRefresher('log_stats',
        #                                          refresh_callback=lambda: logger.info(
        #                                              f"FPS: {int(self.game_time_tracker.fps) if self.game_time_tracker.fps else None}"),
        #                                          refresh_interval_ms=1000)
        pygame.init()

    def start_timers(self):
        self.debug_surface_update_timer = Timer(100,
                                                start_on_init=True,
                                                as_async=True)
        self.log_stats_timer = Timer(5000,
                                     start_on_init=True,
                                     as_async=True)

    def default_key_actions(self):
        return basic_key_actions(
            fullscreen_package=CallbackPackage(down=lambda x: self.toggle_fullscreen()),
            debug_mode_package=CallbackPackage(lambda x: self.debug_mode_toggle.toggle()),
            quit_package=CallbackPackage(lambda x: self.quit()),
            pause_package=CallbackPackage(lambda x: self.paused_toggle.toggle()),
            runspeed_package=(CallbackPackage(lambda x: self.run_speed.toggle(loop=False)),
                              CallbackPackage(lambda x: self.run_speed.toggle(reverse=True, loop=False))),
            help_package=CallbackPackage(lambda x: self.help_toggle.toggle())
        )


    def quit(self):
        self.running = False

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self._init_screen(self.fullscreen, self.screen_width, self.screen_height)

    def _init_screen(self, fullscreen=None, screen_width=None, screen_height=None):
        if fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        elif screen_width and screen_height:
            self.screen = pygame.display.set_mode((self.init_screen_width, self.init_screen_height))
        else:
            self.screen = pygame.display.set_mode((0, 0))

    def register_button(self, id, text, callback, postion_rect):
        self.buttons[id] = PygButton(postion_rect, caption=text, callback=callback)

    @timer(logger=logger, time_tracking_class=tt)
    def main(self, debug: bool = False):
        self.debug_mode_toggle.set_value(debug)

        self.init_builtin_surfaces()
        self.initialize_game()

        self.running = True

        while self.running:
            self._update()
            self._draw(frames=self.game_time_tracker.frames)

        pygame.quit()

    def _check_log_stats(self):
        if self.log_stats_timer.Finished:
            logger.info(f"FPS: {int(self.game_time_tracker.fps) if self.game_time_tracker.fps else None}")
            self.log_stats_timer.reset(start=True)

    @timer(logger=logger, time_tracking_class=tt)
    def _update(self):
        """return
            Update environment based on time delta and any input
        """

        ''' Calculate the ticks between update calls so that the update functions can handle correct time deltas '''
        delta_time_ms = self.game_time_tracker.update(self.run_speed.value)

        # '''Log Stats'''
        # self._monitored_class_logger.check_and_log(logger=logger, delta_time_ms=delta_time_ms, log_interval_ms=self.log_stats_interval_ms)
        # self.log_stats_refresher.check_and_refresh()

        '''Handle Events'''
        """ Handling events should come before updating the model so that any updates to input, etc
        are appropriately handled in the model prior to drawing. O/w, the draw can be written explicitly
        on the last state (not model) and can cause it to be out of order"""
        self._handle_events(delta_time_ms)

        if self.paused_toggle.value == True:
            return

        '''Update Model'''
        self._model_updater(delta_time_ms)

        '''Update Sprites'''
        self.sprite_updater(delta_time_ms)

        '''Animate Sprites'''
        self._sprite_animator(delta_time_ms)

        time.sleep(.001)

    @timer(logger=logger, time_tracking_class=tt)
    def _handle_events(self, delta_time_ms: int):
        """return
            handle all the registered events that have been captured since last iteration
        """

        '''Mouse Pos'''
        inp_state = InputState(delta_ms=delta_time_ms)
        inp_state.register(mouse_pos=help.mouse_pos_as_vector().as_tuple())

        '''Get next event'''
        for event in pygame.event.get():
            '''Check and handle button press'''
            self.handle_buttons(event)

            '''Debug Printer'''
            if event.type not in (0, 1, 4, 6):
                logger.debug(f"Pygame EventType: {event.type}")

            '''Event Type Switch'''
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                inp_state.register(events=[InputEvent(event_type=InputEventType.DOWN, input_key=PyKeys.by_val(event.key))])
            elif event.type == pygame.MOUSEBUTTONDOWN:
                inp_state.register(events=[InputEvent(event_type=InputEventType.DOWN, input_key=PyMouse.by_val(event.button))])
            elif event.type == pygame.KEYUP:
                inp_state.register(events=[InputEvent(event_type=InputEventType.UP, input_key=PyKeys.by_val(event.key))])
            elif event.type == pygame.MOUSEBUTTONUP:
                inp_state.register(events=[InputEvent(event_type=InputEventType.UP, input_key=PyMouse.by_val(event.button))])
            elif event.type == pygame.WINDOWSIZECHANGED:
                self._on_resize()
            else:
                logger.debug(f"Unhandled event: {event.type}")

        '''Handle Input State'''
        self.input_state_handler.handle_input(inp_state)

    # def register_action_to_keys(self, keys_tuple, func: key_mapper, react_while_holding: bool = False):
    #     """
    #         Takes a tuple of keys (integers) and maps that key combo to a callable function
    #
    #         :param keys_tuple a list of keys (integers) that will be mapped to the input callable. Note that a single
    #         value Tuple is input as ([key],) *note the comma
    #         :param func a callable that is mapped to the key combo
    #     """
    #     self._key_handlers[keys_tuple] = (func, react_while_holding)

    @timer(logger=logger, time_tracking_class=tt)
    @try_handler(logger=logger)
    def handle_buttons(self, event):
        for id, button in self.buttons:
            if 'click' in button.handleEvent(event):
                button.callback()

    @timer(logger=logger, time_tracking_class=tt)
    @try_handler(logger=logger)
    def _model_updater(self, delta_time_ms: int):
        return self.model_updater(delta_time_ms)

    @timer(logger=logger, time_tracking_class=tt)
    @try_handler(logger=logger)
    def initialize_game(self):
        raise NotImplementedError()

    @timer(logger=logger, time_tracking_class=tt)
    # @try_handler(logger=logger)
    def handle_hover_over(self, input_state: InputState):
        raise NotImplementedError()

    @timer(logger=logger, time_tracking_class=tt)
    # @try_handler(logger=logger)
    def draw(self, frames: int, debug_mode: bool = False):
        raise NotImplementedError()

    @timer(logger=logger, time_tracking_class=tt)
    # @try_handler(logger=logger)
    def model_updater(self, delta_time_ms: int):
        raise NotImplementedError()

    @timer(logger=logger, time_tracking_class=tt)
    @try_handler(logger=logger)
    def sprite_updater(self, delta_time_ms: int):
        raise NotImplementedError()

    def _on_resize(self):
        logger.info(f"Window Resized [{self.screen.get_width()}x{self.screen.get_height()}]")
        self.init_builtin_surfaces()
        self.on_resize()

    @timer(logger=logger, time_tracking_class=tt)
    # @try_handler(logger=logger)
    def on_resize(self):
        raise NotImplementedError()

    @timer(logger=logger, time_tracking_class=tt)
    # @try_handler(logger=logger)
    def update_built_in_surfaces(self, surface_types: List[BuiltInSurfaceType]):
        raise NotImplementedError()

    @timer(logger=logger, time_tracking_class=tt)
    def _draw(self, frames: int):
        self.screen.fill(Color.BLACK.value)
        self.draw(frames, self.debug_mode_toggle.value)

        '''Draw Sprites'''
        self.sprite_drawer(self.screen)

        if self.debug_mode_toggle.value:
            self._check_update_debugger_surface()
            self.screen.blit(self.built_in_surfaces[BuiltInSurfaceType.DEBUGGER_MASK], (0, 0))
            self.screen.blit(self.built_in_surfaces[BuiltInSurfaceType.DEBUGGER], (0, 0))

        if self.help_toggle.value:
            self._update_help_surface()
            self.screen.blit(self.built_in_surfaces[BuiltInSurfaceType.HELP], (0, 0))

        # Update the display
        pygame.display.flip()

    def _check_update_debugger_surface(self):
        if self.debug_surface_update_timer.Finished:
            self._update_debugger_surface()
            self.debug_surface_update_timer.reset(start=True)

    def _update_debugger_surface(self):
        txt_y_off = 15

        deb_surf = self.built_in_surfaces[BuiltInSurfaceType.DEBUGGER]
        if deb_surf is None:
            return

        deb_surf.fill(DEBUG_COLORKEY.value)
        deb_deb = False

        # draw sprites
        labutils.draw_label(
            hud=deb_surf,
            args=labutils.LabelArgs(
                text=f"Sprite Count: {len(self.sprites)}",
                draw_args=DEBUG_LABEL_ARGS.with_(
                    alignment=TextAlignmentType.TOPRIGHT
                ),
                offset_rect=cRect.from_tuple((self.screen.get_width(),
                                              self.screen.get_height() - txt_y_off * 3,
                                              400,
                                              20),
                                             anchor_cardinality=CardinalPosition.BOTTOM_RIGHT,
                                             inverted_y=True)
            ),
            deb=deb_deb

        )

        # draw RunSpeed
        labutils.draw_label(
            hud=deb_surf,
            args=labutils.LabelArgs(
                text=f"Run Speed: {self.run_speed.value}x",
                draw_args=DEBUG_LABEL_ARGS.with_(
                    alignment=TextAlignmentType.TOPRIGHT
                ),
                offset_rect=cRect.from_tuple((self.screen.get_width(),
                                              self.screen.get_height() - txt_y_off * 5,
                                              400,
                                              20),
                                             anchor_cardinality=CardinalPosition.BOTTOM_RIGHT,
                                             inverted_y=True),
            ),
            deb=deb_deb
        )

        #draw fps
        labutils.draw_label(
            hud=deb_surf,
            args=labutils.LabelArgs(
                text=f"FPS: {str(int(self.game_time_tracker.fps))}",
                draw_args=DEBUG_LABEL_ARGS.with_(
                    alignment=TextAlignmentType.TOPRIGHT
                ),
                offset_rect=cRect.from_tuple((self.screen.get_width(),
                                              self.screen.get_height() - txt_y_off * 4,
                                              400,
                                              20),
                                             anchor_cardinality=CardinalPosition.BOTTOM_RIGHT,
                                             inverted_y=True),
            ),
            deb=deb_deb
        )

        # draw mouse coords
        labutils.draw_label(
            hud=deb_surf,
            args=labutils.LabelArgs(
                text=f"M:<{help.mouse_pos()}>",
                draw_args=DEBUG_LABEL_ARGS.with_(
                    alignment=TextAlignmentType.TOPRIGHT
                ),
                offset_rect=cRect.from_tuple((self.screen.get_width(),
                                              self.screen.get_height(),
                                              400,
                                              20),
                                             anchor_cardinality=CardinalPosition.BOTTOM_RIGHT,
                                             inverted_y=True),
            ),
            deb=deb_deb
        )

        # draw game time
        game_time_s = self.game_time_tracker.ticks / 1000
        hrs = int(game_time_s / 3600)
        min = int((game_time_s - hrs * 3600) / 60)
        s = round(game_time_s - hrs * 3600 - min * 60, 2)
        txt = f"GameTime: {hrs} hrs, {min} min, {s} sec"
        labutils.draw_label(
            hud=deb_surf,
            args=labutils.LabelArgs(
                text=txt,
                draw_args=DEBUG_LABEL_ARGS.with_(
                    alignment=TextAlignmentType.TOPRIGHT
                ),
                offset_rect=cRect.from_tuple((self.screen.get_width(),
                                              self.screen.get_height() - txt_y_off,
                                              400,
                                              20),
                                             anchor_cardinality=CardinalPosition.BOTTOM_RIGHT,
                                             inverted_y=True),
            ),

            deb=deb_deb
        )

        self.draw_monitoredclass_stats(surface=deb_surf, deb=deb_deb)

    def draw_monitoredclass_stats(self,
                                  surface: pygame.Surface,
                                  deb:bool=False):
        offset = 0
        offset = labutils.draw_dict(dict_to_draw=tt.internally_tracked_times,
                                    surface=surface,
                                    total_game_time_sec=self.game_time_tracker.ticks / 1000,
                                    title=f"RunTime Stats",
                                    draw_args=DEBUG_LABEL_ARGS.with_(
                                        alignment=TextAlignmentType.TOPLEFT
                                    ),
                                    deb=deb
        )

    def _sprite_animator(self,
                         delta_time_ms: int):

        for name, sprite in self.sprites.items():
            if type(sprite) == AnimatedSprite:
                sprite.animate(delta_time_ms)

    @timer(logger=logger, time_tracking_class=tt)
    def sprite_drawer(self,
                      surface: pygame.surface):

        sprites = list(self.sprites.values())
        sprites.sort(key=lambda x: x.bottom_center_pos.y)
        for sprite in sprites:
            sprite.blit(surface, display_handle=self.debug_mode_toggle.value, display_rect=self.debug_mode_toggle.value)

    # def register_monitored_classes(self, new_classes: List[TimeableProtocol]):
    #     self._monitored_class_logger.register_classes(new_classes)

    def init_builtin_surfaces(self, types: List[BuiltInSurfaceType] = None, colorkey: Color = None):
        if colorkey is None: colorkey = DEBUG_COLORKEY
        if types is None: types = [e for e in BuiltInSurfaceType]

        for type in types:
            self.built_in_surfaces[type] = pygame.Surface(self.screen.get_size()).convert()
            self.built_in_surfaces[type].set_colorkey(colorkey.value)
            if type == BuiltInSurfaceType.DEBUGGER_MASK:
                self.built_in_surfaces[type].set_alpha(DEBUGGER_MASK_ALPHA)

    @timer(logger=logger, time_tracking_class=tt)
    def _update_help_surface(self):
        text = self._help_txt()

        self.built_in_surfaces[BuiltInSurfaceType.HELP].fill(Color.WHEAT.value)

        font = pygame.font.Font(None, 20)
        fontsize = font.get_height()
        offSet = 0

        for idx, line in enumerate(text):
            labutils.draw_label(
                hud=self.built_in_surfaces[BuiltInSurfaceType.HELP],
                args=labutils.LabelArgs(
                    text=line,
                    draw_args=labutils.DrawLabelArgs(
                        font=font,
                        color=Color.BLACK
                    ),
                    offset_rect=Rectangle.from_tuple((0,
                                                      idx * fontsize + offSet,
                                                      self.built_in_surfaces[BuiltInSurfaceType.HELP].get_width(),
                                                      fontsize + 3))
                )

            )
            # help.draw_text(line,
            #                self.built_in_surfaces[BuiltInSurfaceType.HELP],
            #                font=font,
            #                offset_rect=Rectangle.from_tuple((0,
            #                                      idx * fontsize + offSet,
            #                                      fontsize + 3,
            #                                      self.built_in_surfaces[BuiltInSurfaceType.HELP].get_width())))

    def _help_txt(self):

        txt = []
        txt.append("HELP")
        txt.append("\n--------")
        txt.append("\n")
        for k, v in self.input_state_handler.InputActions.items():
            txt.append(f"{','.join(f'{x.input_key.id} {x.event_type.id}' for x in k)} --> {v.description}")

        return txt


    @property
    def screen_width(self):
        return self.screen.get_width() if self.screen else self.init_screen_width

    @property
    def screen_height(self):
        return self.screen.get_height() if self.screen else self.init_screen_height

    @property
    def game_area_rectangle(self):
        return Rectangle.from_tuple((0, 0, self.screen.get_width(), self.screen.get_height()))

    @property
    def ScreenCenter(self):
        return self.game_area_rectangle.Center

if __name__ == "__main__":
    import coopgame.pointdrawing.point_draw_utils as pdu

    class HelpTest(GameTemplate):

        def __init__(self):
            super().__init__()

        def draw(self, frames: int, debug_mode: bool = False):
            pdu.draw_points(
                points={
                    (self.ScreenCenter): pdu.DrawPointArgs(
                        color=Color.BLUE,
                        outline_color=Color.ORANGE,
                        radius=50,
                        outline_width=4
                    )
                },
                surface=self.screen
            )
            help.draw_arrow(self.screen,
                            self.ScreenCenter,
                            help.mouse_pos_as_vector().as_tuple(),
                            Color.GREEN)

    logging.basicConfig(level=logging.INFO)
    g = HelpTest()
    g.main()