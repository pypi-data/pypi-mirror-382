from qtpy.QtCore import Qt, QSize
from qtmui.material.styles import useTheme
from qtmui.material.styles.create_theme.theme_reducer import ThemeState
from qtmui.material.styles.create_theme.create_palette import PaletteColor
from ..py_tool_button.py_tool_button import Iconify
from .button import Button
from ...common.icon import FluentIconBase
class IconButton:
    def __init__(self, icon: str, edge: str, margin: int, color: str, whileTap: str, whileHover: str, *args, **kwargs): ...
    def set_icon(self, theme): ...