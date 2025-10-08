from __future__ import annotations
from qtmui.hooks.use_state import State
from typing import Callable, Optional, Union, List, Dict, Any
import random
from qtpy.QtCore import QPointF, Qt
from qtpy.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from qtpy.QtCharts import QChart, QChartView, QLineSeries, QAreaSeries, QPercentBarSeries, QBarCategoryAxis, QBarSeries, QBarSet, QValueAxis
from qtpy.QtGui import QGradient, QPen, QLinearGradient, QPainter, QColor, QBrush
from ..system.color_manipulator import alpha
from qtmui.material.styles import useTheme
class ChartBar:
    def __init__(self, dir: str, type: str, series: List[Dict[str, Any]], width: Optional[Union[str, int]], height: Optional[Union[str, int]], options: Optional[Dict[str, Any]], key: str, title: Optional[Union[State, str, Callable]], *args, **kwargs): ...
    def _get_unique_color(self): ...
    def _init_bar_chart(self): ...
    def _set_stylesheet(self): ...