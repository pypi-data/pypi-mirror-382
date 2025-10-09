from typing import Dict
from cooptools.colors import Color

class RuntimeConfig:
    def __init__(self, runtime_config: Dict = None):
        self.runtime_config = runtime_config if runtime_config else {}
        self._txt__fps_txt_offset_x = "fps_txt_offset_x"
        self._txt__fps_txt_offset_y = "fps_txt_offset_y"
        self._txt__fps_txt_font_size = "fps_txt_font_size"
        self._txt__mousecoords_txt_offset_x = "mousecoords_txt_offset_x"
        self._txt__mousecoords_txt_offset_y = "mousecoords_txt_offset_y"
        self._txt__mousecoord_txt_font_size = "mousecoords_txt_font_size"
        self._txt__mousecoords_color_rgb = "mousecoords_color_rgb"
        self._txt__monitoredclass_txt_offset_x = "monitoredclass_txt_offset_x"
        self._txt__monitoredclass_txt_offset_y = "monitoredclass_txt_offset_y"
        self._txt__monitoredclass_txt_font_size = "monitoredclass_txt_font_size"
        self._txt__monitoredclass_color_rgb = "monitoredclass_color_rgb"
        self._txt__debug_mode = "debug_mode"
        self._txt__fullscreen = "fullscreen"
        self._txt__screen_width = "screen_width"
        self._txt__screen_height = "screen_height"
        self._txt__max_fps = "max_fps"
        self._txt__fps_color_rgb = "fps_color_rgb"
        self._txt__log_tracked_time_interval_sec = "log_tracked_time_interval_sec"

    @property
    def log_tracked_time_interval_sec(self):
        return int(self.runtime_config.get(self._txt__log_tracked_time_interval_sec, 5))

    @property
    def fps_txt_offset_x(self):
        return int(self.runtime_config.get(self._txt__fps_txt_offset_x, 0))

    @property
    def fps_txt_offset_y(self):
        return int(self.runtime_config.get(self._txt__fps_txt_offset_y, 0))

    @property
    def fps_txt_font_size(self):
        return int(self.runtime_config.get(self._txt__fps_txt_font_size, 10))

    @property
    def fps_color(self):
        evald_rgb = eval(self.runtime_config.get(self._txt__fps_color_rgb, "(255, 255, 255)"))
        return Color.closest_color(evald_rgb)

    @property
    def mousecoords_txt_offset_x(self):
        return int(self.runtime_config.get(self._txt__mousecoords_txt_offset_x, 0))

    @property
    def mousecoords_txt_offset_y(self):
        return int(self.runtime_config.get(self._txt__mousecoords_txt_offset_y, 13))

    @property
    def mousecoords_txt_font_size(self):
        return int(self.runtime_config.get(self._txt__mousecoord_txt_font_size, 10))

    @property
    def mousecoords_txt_color(self):
        evald_rgb = eval(self.runtime_config.get(self._txt__mousecoords_color_rgb, "(255, 255, 255)"))
        return Color.closest_color(evald_rgb)

    @property
    def monitoredclass_txt_offset_x(self):
        return int(self.runtime_config.get(self._txt__monitoredclass_txt_offset_x, 0))

    @property
    def monitoredclass_txt_offset_y(self):
        return int(self.runtime_config.get(self._txt__monitoredclass_txt_offset_y, 0))

    @property
    def monitoredclass_txt_font_size(self):
        return int(self.runtime_config.get(self._txt__monitoredclass_txt_font_size, 10))

    @property
    def monitoredclass_txt_color(self):
        evald_rgb = eval(self.runtime_config.get(self._txt__monitoredclass_color_rgb, "(255, 255, 255)"))
        return Color.closest_color(evald_rgb)

    @property
    def debug_mode(self):
        return bool(self.runtime_config.get(self._txt__debug_mode, False))

    @property
    def fullscreen(self):
        return bool(self.runtime_config.get(self._txt__fullscreen, False))

    @property
    def screen_dims(self):
        width = int(self.runtime_config.get(self._txt__screen_width, 1000))
        height = int(self.runtime_config.get(self._txt__screen_height, 1000))
        return (width, height)

    @property
    def max_fps(self):
        return int(self.runtime_config.get(self._txt__max_fps, 120))