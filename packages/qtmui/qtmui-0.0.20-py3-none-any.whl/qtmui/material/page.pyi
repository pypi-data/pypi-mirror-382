import threading
import time
from qtpy.QtWidgets import QVBoxLayout, QWidget, QSizePolicy, QFrame
from qtpy.QtGui import QPainter
from qtpy.QtCore import Qt, QPoint, QRect, Signal, QTimer
from .view import View
from qtmui.hooks.use_state import useState
class Page:
    def __init__(self, *args, **kwargs): ...
    def _wait_for_3s(self): ...
    def add_widget(self, element: QWidget): ...