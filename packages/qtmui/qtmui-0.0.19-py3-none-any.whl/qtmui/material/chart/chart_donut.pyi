from __future__ import annotations
from qtmui.hooks.use_state import State
from typing import Callable, Optional, Union
import random
from qtpy.QtCore import QPointF, Qt
from qtpy.QtWidgets import QWidget, QVBoxLayout
from qtpy.QtCharts import QChart, QChartView, QPieSeries, QChart, QChartView
from qtpy.QtGui import QGradient, QLinearGradient, QPainter, QColor, QBrush
from ..system.color_manipulator import alpha
from qtmui.material.styles import useTheme
class ChartDonut:
    def __init__(self, dir: str, series: object, width: Optional[Union[str, int]], height: Optional[Union[str, int]], options: object, key: str, title: Optional[Union[State, str, Callable]], *args, **kwargs): ...
    def _get_unique_color(self): ...
    def _init_donut_chart(self): ...
    def _set_stylesheet(self): ...