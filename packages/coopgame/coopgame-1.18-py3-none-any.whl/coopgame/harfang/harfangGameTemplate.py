from coopbugger.monitoredclass import MonitoredClass
from coopstructs.geometry import Rectangle
from coopstructs.vectors import Vector2
from coopgame.gameTemplate import GameTemplate
import harfang as hg
from coopgame.harfang.harfangColorConverter import harfang_color_from_coopcolor
from cooptools.colors import Color
from coopgame.runtime_config import RuntimeConfig
from typing import Tuple

class HarfangGameTemplate(GameTemplate):

    def __init__(self,
                 config: RuntimeConfig = None):
        self.plus = hg.GetPlus()
        hg.LoadPlugins()
        self.keyboard = hg.GetInputSystem().GetDevice("keyboard")
        super().__init__(config)



    ######## HARFANG SPECIFIC IMPLEMENTATION OF IGameTemplate

    def _quit(self):
        self.plus.RenderUninit()

    def _init_screen(self, fullscreen):
        self.plus.RenderInit(self.screen_width, self.screen_height)

    def _handle_library_specific_events(self):
        if self.keyboard.WasPressed(hg.KeyEscape) \
                or self.plus.IsAppEnded():
            self.running = False

    def _init_frame(self):
        self.plus.Clear()

    def _render_frame(self):
        self.plus.Flip()
        self.plus.EndFrame()

    def _draw_text(self,
                   text: str,
                   offset_rect: Rectangle = None,
                   color: Color = None,
                   font_size: int = None):
        if font_size is None:
            font_size = 10

        if color is None:
            color = Color.WHITE

        if offset_rect is None:
            offset_rect = Rectangle(0, 0, 1, 1)

        hcolor = harfang_color_from_coopcolor(color)
        self.plus.Text2D(offset_rect.x, offset_rect.y, f"{text}", font_size, hcolor)

    def _draw_monitoredclass_stats(self,
                                  monitoredClass: MonitoredClass,
                                  config: RuntimeConfig):

        tracked_time = [(key, val) for key, val in monitoredClass.tracked_time.items()]
        tracked_time.sort(key=lambda x: x[1], reverse=True)

        offset_rectangle = Rectangle(config.monitoredclass_txt_offset_x,
                                     self.screen_height - config.monitoredclass_txt_font_size + config.monitoredclass_txt_offset_y,
                                     1, 1)
        y_off = offset_rectangle.y

        self._draw_text(f"RunTime Stats for {type(monitoredClass).__name__}",
                        color=Color.LEMON_CHIFFON,
                        offset_rect=offset_rectangle,
                        font_size=config.monitoredclass_txt_font_size)
        y_off -= config.monitoredclass_txt_font_size + 3
        for key, val in tracked_time:
            offset_rectangle.y = y_off
            self._draw_text(f"{key}: {round(val, 2)} sec",
                            color=Color.LEMON_CHIFFON,
                            offset_rect=offset_rectangle,
                            font_size=config.monitoredclass_txt_font_size)
            y_off -= config.monitoredclass_txt_font_size + 3


    @staticmethod
    def mouse_pos_as_vector() -> Vector2:
        # get the mouse device
        mouse_device = hg.GetInputSystem().GetDevice("mouse")
        return Vector2(mouse_device.GetValue(hg.InputAxisX), mouse_device.GetValue(hg.InputAxisY))

    ############ USER DEFINED FOR GAME ####################
    def initialize_game(self):
        raise NotImplementedError()

    def handle_left_click(self, pressed_keys):
        raise NotImplementedError()

    def handle_right_click(self, pressed_keys):
        raise NotImplementedError()

    def handle_hover_over(self, mouse_pos_as_vector: Vector2):
        raise NotImplementedError()

    def handle_mouse_scroll_up(self, pressed_keys):
        raise NotImplementedError()

    def handle_mouse_scroll_down(self, pressed_keys):
        raise NotImplementedError()

    def draw(self, frames: int, debug_mode: bool = False):
        raise NotImplementedError()

    def model_updater(self, delta_time_ms: int):
        raise NotImplementedError()

    def sprite_updater(self, delta_time_ms: int):
        raise NotImplementedError()

    def on_resize(self):
        raise NotImplementedError()

    def register_button(self, id, text, callback, postion_rect):
        raise NotImplementedError()

    def register_keys(self):
        raise NotImplementedError()

