import asyncio
from typing import Callable, Dict, List, Optional, Union
from qtmui.hooks.use_state import State
from qtpy.QtWidgets import QWidget
from qtpy.QtCore import Qt, QTimer
from qtmui.material.styles import useTheme
from qtmui.material.styles.create_theme.components.get_qss_styles import get_qss_style
from .button import Button
from ..py_iconify import Iconify
class IconButton:
    def __init__(self, color: Union[State, str], margin: Union[State, int], whileTap: Union[State, str], whileHover: Union[State, str], icon: Optional[Union[str, Iconify]], *args, **kwargs): ...
    def ___set_stylesheet(self, component_styled): ...