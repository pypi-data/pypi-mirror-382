from __future__ import annotations
from typing import Optional, Union
import sys
from qtpy.QtCore import QPointF, Qt
from qtpy.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout
from qtpy.QtCharts import QChart, QChartView, QLineSeries, QAreaSeries, QBarCategoryAxis, QBarSeries, QBarSet, QChart, QChartView, QValueAxis
from qtpy.QtGui import QGradient, QPen, QLinearGradient, QPainter
from .chart_line import ChartLine
from .map_change_theme import ChartArea
from .chart_bar import ChartBar
class Chart:
    def __init__(self, dir: str, type: str, series: object, width: Optional[Union[str, int]], height: Optional[Union[str, int]], options: object, key: str, *args, **kwargs): ...