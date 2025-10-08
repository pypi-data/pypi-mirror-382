import uuid
from typing import Optional, Callable
from qtpy.QtWidgets import QVBoxLayout, QFileDialog, QFrame, QPushButton
from qtpy.QtCore import Qt, QSize
from qtpy.QtGui import QCursor, QMouseEvent
from ..typography import Typography
from ..box import Box
from ..py_iconify import PyIconify, Iconify
from ..py_svg_widget import PySvgWidget
from ...qtmui_assets import QTMUI_ASSETS
from ..button.button import Button
from qtmui.material.styles import useTheme
class UploadBox:
    def __init__(self, files: str, onDrop: Optional[Callable], error: object, placeholder: object, sx: object, *args, **kwargs): ...
    def _init_ui(self): ...
    def mousePressEvent(self, event: QMouseEvent): ...
    def open_file(self): ...
    def format_size(self, bytes): ...