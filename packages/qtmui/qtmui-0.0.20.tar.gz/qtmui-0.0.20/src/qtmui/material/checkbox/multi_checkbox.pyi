from typing import Callable
from qtpy.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qtpy.QtGui import QPainter, QPen, QIcon
from qtpy.QtCore import Qt, QSize, Signal
from qtmui.material.styles.create_theme.theme_reducer import ThemeState
from qtmui.material.styles.create_theme.create_palette import PaletteColor
from ..system.color_manipulator import hex_string_to_qcolor
from qtmui.material.styles.create_theme.components.get_qss_styles import get_qss_style
from .checkbox import Checkbox
from ..form_control_label import FormControlLabel
from qtmui.hooks.use_state import State
from qtmui.material.styles import useTheme
class MultiCheckbox:
    def __init__(self, value: object, orientation: str, options: bool, onChange: Callable, *args, **kwargs): ...
    def _init_ui(self): ...
    def _set_stylesheet(self): ...
    def _on_field_value_change(self, data): ...