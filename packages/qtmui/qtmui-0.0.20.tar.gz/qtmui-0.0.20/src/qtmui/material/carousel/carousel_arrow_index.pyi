from __future__ import annotations
import uuid
from typing import Optional, Union, Callable
from qtpy.QtWidgets import QFrame, QHBoxLayout
from ..button import IconButton
from ..typography import Typography
from ..box import Box
from ..spacer import VSpacer
from qtmui.hooks.use_state import useState
from ..system.color_manipulator import alpha
from qtmui.material.styles.create_theme.components.get_qss_styles import get_qss_style
from ..py_iconify import PyIconify, Iconify
from ...qtmui_assets import QTMUI_ASSETS
from qtmui.material.styles import useTheme
class CarouselArrowIndex:
    def __init__(self, index: object, setCurrentIndex: object, total: int, onNext: Callable, onPrev: Callable, sx: dict, *args, **kwargs): ...
    def _init_ui(self): ...
    def _set_stylesheet(self): ...
    def _set_index_arrow_text(self, value): ...