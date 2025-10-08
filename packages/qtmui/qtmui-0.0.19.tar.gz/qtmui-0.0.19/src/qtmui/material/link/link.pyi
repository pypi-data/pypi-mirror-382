from typing import Callable, Optional, Union
from qtpy.QtWidgets import QWidget, QVBoxLayout
from qtpy.QtCore import Qt
from qtmui.material.styles.create_theme.create_palette import PaletteColor
from ..typography import Typography
from qtmui.material.styles import useTheme
from ..widget_base import PyWidgetBase
class Link:
    def __init__(self, onClick: Callable, underline: str, href: str, children: Optional[Union[list, QWidget]], *args, **kwargs): ...
    def _init_ui(self): ...
    def _set_stylesheet(self, component_styled): ...