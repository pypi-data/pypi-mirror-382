from __future__ import annotations
from typing import Optional, Union
import sys
from qtpy.QtCore import QPointF, Qt
from qtpy.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout
from qtpy.QtCharts import QChart, QChartView, QLineSeries, QAreaSeries, QBarCategoryAxis, QBarSeries, QBarSet, QChart, QChartView, QValueAxis
from qtpy.QtGui import QGradient, QPen, QLinearGradient, QPainter
from .map_change_theme import MapChangeTheme
class Map:
    def __init__(self, initialViewState: dict, *args, **kwargs): ...