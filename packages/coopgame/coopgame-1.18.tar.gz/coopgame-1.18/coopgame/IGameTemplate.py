import functools
import logging
from coopbugger.monitoredclass import MonitoredClass
import time
from typing import Callable, Tuple
from coopstructs.vectors import Vector2
from coopstructs.geometry import Rectangle
from cooptools.colors import Color
from coopgame.runtime_config import RuntimeConfig
# from coopgame.inputListener import InputState

def try_handler(func):
    @functools.wraps(func)
    def wrapper_handler(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except NotImplementedError as e:
            error = f"Inherited class should implement logic for {func.__name__}"
            logging.warning(error)
        except Exception as e:
            logging.exception(e)

    return wrapper_handler


class IGameTemplate(MonitoredClass):

    def __init__(self,
                 config: RuntimeConfig = None):
        super().__init__()
        self.runtime_config = config if config else RuntimeConfig()

        self.screen = None
        self._init_screen(self.runtime_config)

        self.ticks = 0
        self.frame_times = []
        self.fps = None

        self.buttons = {}
        self._key_handlers = {}
        self.register_keys()

        self.running = False

        self.input_state = InputState()

        self.time_since_logged_tracked_time = 0

    @property
    def screen_width(self):
        return self.runtime_config.screen_dims[0]

    @property
    def screen_height(self):
        return self.runtime_config.screen_dims[1]

    def _break_run_loop(self):
        self.running = False

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self._init_screen(self.fullscreen)


    def main(self):

        self.initialize_game()

        self.running = True
        ii = 0


        while self.running:
            ''' Calculate the ticks between update calls so that the update functions can handle correct time deltas '''
            t = time.perf_counter() * 1000
            delta_time_ms = int(t - self.ticks)
            self.ticks = t

            self._update(delta_time_ms)
            self._draw(frames=ii)
            self._log_tracked_time(delta_time_ms)
            ii += 1

        self._quit()

    def calculate_fps(self, ticks_last_frame: int):
        if len(self.frame_times) > 20:
            self.frame_times.pop(0)

        self.frame_times.append(ticks_last_frame)

        avg_sec_per_frame = sum(self.frame_times) / len(self.frame_times) / 1000.0
        self.fps = 1 / avg_sec_per_frame if avg_sec_per_frame > 0 else 0

    def _update(self, delta_time_ms: int):
        """:return
            Update environment based on time delta and any input
        """
        self.calculate_fps(delta_time_ms)

        '''Update Model'''
        self.model_updater(delta_time_ms)

        '''Update Sprites'''
        self.sprite_updater(delta_time_ms)

        '''Handle Events'''
        self._handle_events()

        '''Clear Input Events'''
        self.input_state.clear_events()

    def _handle_events(self):
        self._handle_library_specific_events()
        self._handle_key_pressed()
        self._handle_held_keys()
        self._handle_hover_over()

    def _log_tracked_time(self, delta_time_ms: int):
        self.time_since_logged_tracked_time += delta_time_ms / 1000.0

        if self.time_since_logged_tracked_time > self.runtime_config.log_tracked_time_interval_sec:
            logging.info(self.tracked_time)
            self.time_since_logged_tracked_time = 0

    def register_action_to_keys(self, keys_tuple, func: Callable, react_while_holding: bool = False):
        """
            Takes a tuple of keys (integers) and maps that key combo to a callable function

            :param keys_tuple a list of keys (integers) that will be mapped to the input callable. Note that a single
            value Tuple is input as ([key],) *note the comma
            :param func a callable that is mapped to the key combo
        """
        self._key_handlers[keys_tuple] = (func, react_while_holding)

    @MonitoredClass.timer
    @try_handler
    def handle_buttons(self, event):
        for id, button in self.buttons:
            if 'click' in button.handleEvent(event):
                button.callback()

    @MonitoredClass.timer
    @try_handler
    def _handle_key_pressed(self):
        for key in self.input_state.keys_pressed_events:
            logging.info(f"{key} pressed")

        for mapped_keys, reaction in self._key_handlers.items():
            if self.input_state.is_pressed(mapped_keys):
                func = reaction[0]
                logging.info(f"callback triggered for [{mapped_keys}] --> {func}")
                func()

    @MonitoredClass.timer
    @try_handler
    def _handle_held_keys(self):
        for mapped_keys, reaction in self._key_handlers.items():
            if self.input_state.is_pressed(mapped_keys):
                func = reaction[0]
                react_while_holding = reaction[1]
                if react_while_holding:
                    logging.info(f"callback triggered for [{mapped_keys}] (while held)--> {func}")
                    func()

    @MonitoredClass.timer
    def _handle_hover_over(self):
        mouse_pos_as_vector = self.mouse_pos_as_vector()
        if mouse_pos_as_vector:
            self.handle_hover_over(mouse_pos_as_vector)

    @MonitoredClass.timer
    def _draw(self,
              frames: int):
        self._init_frame()
        self.draw(frames)
        if self.runtime_config.debug_mode:
            self._draw_debug_stuff()

        self._render_frame()

    @MonitoredClass.timer
    def _draw_debug_stuff(self):
        # Monitored class stats
        self._draw_monitoredclass_stats(self, self.runtime_config)

        # FPS
        self._draw_fps(self.runtime_config)

        # Mouse Coords
        self.draw_mouse_coord(self.runtime_config)

    @try_handler
    def draw_mouse_coord(self,
                         config: RuntimeConfig):
        mouse_pos_as_vector = self.mouse_pos_as_vector()

        offset_rect = Rectangle(self.runtime_config.mousecoords_txt_offset_x,
                                self.runtime_config.mousecoords_txt_offset_y,
                                1, 1)

        txt = f"M:<{int(mouse_pos_as_vector.x)}, {int(mouse_pos_as_vector.y)}>"
        self._draw_text(txt,
                        offset_rect=offset_rect,
                        color=config.mousecoords_txt_color,
                        font_size=config.mousecoords_txt_font_size
                        )

    def _draw_fps(self, config: RuntimeConfig):
        fps_offset_rect = Rectangle(self.runtime_config.fps_txt_offset_x,
                                    self.runtime_config.fps_txt_offset_y,
                                    1, 1)
        txt = f"FPS: {int(self.fps)}"
        self._draw_text(txt,
                        offset_rect=fps_offset_rect,
                        color=config.fps_color,
                        font_size=config.fps_txt_font_size)

    def window_rect(self):
        return Rectangle(0, 0, self.screen.get_height(), self.screen.get_width())

    def toggle_debug_mode(self):
        self._debug_mode = not self._debug_mode


    ############### IGAMETEMPLATE IMPLEMNENTER SPECIFIC LOGIC ###############

    @MonitoredClass.timer
    @try_handler
    def initialize_game(self):
        raise NotImplementedError()

    @MonitoredClass.timer
    @try_handler
    def handle_left_click(self, pressed_keys):
        raise NotImplementedError()

    @MonitoredClass.timer
    @try_handler
    def handle_right_click(self, pressed_keys):
        raise NotImplementedError()

    @MonitoredClass.timer
    @try_handler
    def handle_hover_over(self, mouse_pos_as_vector: Vector2):
        raise NotImplementedError()

    @MonitoredClass.timer
    @try_handler
    def handle_mouse_scroll_up(self, pressed_keys):
        raise NotImplementedError()

    @MonitoredClass.timer
    @try_handler
    def handle_mouse_scroll_down(self, pressed_keys):
        raise NotImplementedError()

    @MonitoredClass.timer
    @try_handler
    def draw(self, frames: int, debug_mode: bool = False):
        raise NotImplementedError()

    @MonitoredClass.timer
    @try_handler
    def model_updater(self, delta_time_ms: int):
        raise NotImplementedError()

    @MonitoredClass.timer
    @try_handler
    def sprite_updater(self, delta_time_ms: int):
        raise NotImplementedError()

    @MonitoredClass.timer
    @try_handler
    def on_resize(self):
        raise NotImplementedError()

    @try_handler
    def register_keys(self):
        raise NotImplementedError()

    def _quit(self):
        raise NotImplementedError()

    def _init_screen(self, fullscreen):
        raise NotImplementedError()

    def register_button(self, id, text, callback, postion_rect):
        raise NotImplementedError()

    def _handle_library_specific_events(self):
        raise NotImplementedError()


    @MonitoredClass.timer
    @try_handler
    def _init_frame(self):
        raise NotImplementedError()

    @MonitoredClass.timer
    @try_handler
    def _render_frame(self):
        raise NotImplementedError()

    @MonitoredClass.timer
    @try_handler
    def _draw_text(self,
                  text: str,
                  offset_rect: Rectangle = None,
                  color: Color = None,
                  **kwargs):
        raise NotImplementedError()

    @try_handler
    def _draw_monitoredclass_stats(self,
                                  monitoredClass: MonitoredClass,
                                  config: RuntimeConfig):
        raise NotImplementedError()


    @staticmethod
    def mouse_pos_as_vector() -> Vector2:
        raise NotImplementedError()
