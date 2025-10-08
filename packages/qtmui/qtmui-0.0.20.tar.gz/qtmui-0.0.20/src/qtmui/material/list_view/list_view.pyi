from typing import Dict
from qtpy.QtWidgets import QVBoxLayout, QFrame, QListView, QAbstractItemView, QLabel, QFrame, QScrollArea, QWidget, QSizePolicy
from qtpy.QtCore import Qt, QStringListModel, QEvent, QPoint, QRect
import sys
from qtpy.QtGui import QFocusEvent
class ListView:
    def __init__(self, parent_frame, context, fullWidth: bool, children: list): ...
    def update_height(self): ...