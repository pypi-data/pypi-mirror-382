import asyncio
import uuid
from typing import Optional, Callable, Any, Dict, Union
from qtpy.QtWidgets import QLineEdit, QHBoxLayout, QGroupBox
from qtpy.QtCore import Signal, Qt, QTimer
from qtmui.material.styles import useTheme
from qtmui.material.styles.create_theme.components.get_qss_styles import get_qss_style
from qtmui.hooks.use_state import State
from .py_input import PyInput
class PyStandardInput:
    def __init__(self, *args, **kwargs): ...
    def _set_stylesheet(self): ...
    def _set_prop_has_start_adornment(self, state: bool): ...