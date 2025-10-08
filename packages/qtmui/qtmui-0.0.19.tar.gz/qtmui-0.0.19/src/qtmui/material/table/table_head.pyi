import asyncio
from functools import lru_cache
from typing import Optional, Union, Callable, Any, List, Dict
import uuid
from qtmui.hooks.use_state import State
from qtpy.QtWidgets import QWidget, QVBoxLayout, QFrame, QSizePolicy, QHBoxLayout
from qtpy.QtCore import Qt, QTimer
from ..widget_base import PyWidgetBase
from qtmui.material.styles import useTheme
from qtmui.material.styles.create_theme.components.get_qss_styles import get_qss_style
from ..utils.validate_params import _validate_param
class TableHead:
    def __init__(self, children: Optional[Union[State, Any, List[Any]]], order: Union[State, str], checked: Union[State, str], orderBy: Union[State, str], headLabel: Union[State, List[Any]], rowCount: Union[State, int], numSelected: Union[State, int], onSort: Union[State, Callable], onSelectAllRows: Union[State, Callable], tableSelectedAction: Union[State, QWidget]): ...