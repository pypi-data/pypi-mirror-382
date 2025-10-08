from __future__ import annotations
from typing import Optional, Union
import sys
from qtpy.QtCore import QPointF, Qt
from qtpy.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout
from qtpy.QtGui import QGradient, QPen, QLinearGradient, QPainter
from .chart_line import ChartLine
from .chart_area import ChartArea
from .chart_bar import ChartBar
from .chart_donut import ChartDonut
from .chart_radial_bar import ChartRadialBar
from .chart_radial_bar_1 import ChartRadialBar1
from .chart_pie import ChartPie
from .chart_radar import ChartRadar
from .chart_polar_area import ChartPolarArea
class Chart:
    def __init__(self, dir: str, type: str, series: object, width: Optional[Union[str, int]], height: Optional[Union[str, int]], options: object, key: str, total: int, *args, **kwargs): ...