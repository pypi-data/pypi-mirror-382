import uuid
from typing import Optional, Union, Callable, Dict
from qtpy.QtWidgets import QFrame, QVBoxLayout, QSizePolicy
from qtpy.QtCore import Qt
from qtmui.material.styles import useTheme
from qtmui.material.styles.create_theme.components.get_qss_styles import get_qss_style
class TableContainer:
    def __init__(self, children: object, data: object, sx: Optional[Union[Callable, str, Dict]]): ...
    def _init_ui(self): ...
    def _set_stylesheet(self): ...