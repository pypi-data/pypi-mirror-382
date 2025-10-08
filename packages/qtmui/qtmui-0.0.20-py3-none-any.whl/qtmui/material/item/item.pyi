import sys
import uuid
from qtpy.QtWidgets import QFrame, QVBoxLayout, QWidget
from qtpy.QtCore import Qt, QSize
from qtpy.QtGui import QColor
class Item:
    def __init__(self, content: QWidget): ...