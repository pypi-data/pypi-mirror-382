import uuid
from qtpy.QtWidgets import QVBoxLayout, QFrame, QSizePolicy
from qtpy.QtCore import Qt
from typing import Optional, Union, List, Callable
from qtmui.hooks.use_state import State
from ..typography import Typography
from ..box import Box
from qtmui.material.styles import store, useTheme
class AlignBox:
    def __init__(self, **kwargs): ...
class TimelineContent:
    def __init__(self, children, classes: dict, sx: Union[List[Union[Callable, dict, bool]], Callable, dict], text: Optional[Union[str, State, Callable]]): ...
    def _initUI(self): ...