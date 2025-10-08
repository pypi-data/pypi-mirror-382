from __future__ import annotations
from typing import Callable, Optional, Union, List, Dict
import math
from qtpy.QtWidgets import QWidget, QVBoxLayout
from qtpy.QtGui import QPainter, QColor, QBrush, QPen, QFont, QPainterPath
from qtpy.QtCore import Qt, QPointF, QRectF
from qtmui.hooks.use_state import State
from qtmui.material.styles import useTheme
class ChartPolarArea:
    def __init__(self, dir: str, series: Optional[Union[List[Dict], List[float]]], width: Optional[Union[str, int]], height: Optional[Union[str, int]], options: Optional[Dict], key: str, title: Optional[Union[State, str, Callable]], *args, **kwargs): ...
    def paintEvent(self, event): ...