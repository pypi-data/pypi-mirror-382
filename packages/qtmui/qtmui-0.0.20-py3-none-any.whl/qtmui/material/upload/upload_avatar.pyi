from typing import Callable, Optional
import uuid
from ..system.color_manipulator import alpha
from qtpy.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QVBoxLayout, QLabel, QFileDialog, QFrame
from qtpy.QtCore import Qt, QSize
from qtpy.QtGui import QIcon, QCursor, QMouseEvent
from ..typography import Typography
from ..stack import Stack
from ..box import Box
from ..py_svg_widget import PySvgWidget
from ..view import View
from ..image import Image
from qtmui.hooks import useState
from qtmui.material.styles import store, useTheme
class UploadAvatar:
    def __init__(self, multiple: bool, thumbnail: str, file: str, files: str, onDrop: Callable, onChange: Callable, onRemove: Callable, onRemoveAll: Callable, onUpload: Callable, error: bool, value: Optional[str], *args, **kwargs): ...
    def _init_ui(self): ...
    def mousePressEvent(self, event: QMouseEvent): ...
    def open_file(self): ...
    def _set_value(self, value): ...
    def format_size(self, bytes): ...