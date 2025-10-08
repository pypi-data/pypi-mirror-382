from __future__ import annotations
from typing import Optional, Union
import sys
from qtpy.QtCore import QPointF, Qt
from qtpy.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout
from .map_change_theme import MapChangeTheme
from .map_widget import MapWindow
class Map:
    def __init__(self, initialViewState: dict, *args, **kwargs): ...