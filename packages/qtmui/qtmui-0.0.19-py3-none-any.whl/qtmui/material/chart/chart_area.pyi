from __future__ import annotations
from typing import Optional, Union
import sys
from qtpy.QtCore import QPointF, Qt
from qtpy.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout
from qtpy.QtCharts import QChart, QChartView, QLineSeries, QAreaSeries, QBarCategoryAxis, QBarSeries, QBarSet, QChart, QChartView, QValueAxis
from qtpy.QtGui import QGradient, QPen, QLinearGradient, QPainter, QColor
from qtmui.material.styles import useTheme
class ChartArea:
    def __init__(self, dir: str, type: str, series: object, width: Optional[Union[str, int]], height: Optional[Union[str, int]], options: object, key: str, *args, **kwargs): ...
    def _init_area_chart(self): ...
    def _set_stylesheet(self): ...