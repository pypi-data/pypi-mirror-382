import asyncio
from functools import lru_cache
from typing import Callable, Optional, Union, Dict
from qtpy.QtGui import QMouseEvent
from qtpy.QtWidgets import QHBoxLayout, QLabel, QWidget, QToolButton
from qtpy.QtCore import Qt, QThreadPool, QTimer
import uuid
from qtmui.hooks.use_runable import useRunnable
from qtmui.hooks.use_state import State
from qtmui.material.styles import useTheme
from qtmui.material.styles.create_theme.theme_reducer import ThemeState
from qtmui.material.styles.create_theme.create_palette import PaletteColor, TypeText
from qtmui.material.styles.create_theme.typography import TypographyStyle
from qtmui.material.styles.create_theme.components.get_qss_styles import get_qss_style
from qtmui.i18n.use_translation import translate, i18n
from ..widget_base import PyWidgetBase
from ..py_iconify import PyIconify
from ...utils.data import convert_sx_params_to_str, convert_sx_params_to_dict
class Typography:
    def __init__(self, id, align, children, text, color: str, value: object, classes, gutterBottom, wrap, width: Optional[int], paragraph, onClick: Callable, sx: Optional[Union[Callable, str, Dict]], variant: str, typography: str, *args, **kwargs): ...
    def _init_ui(self): ...
    def reTranslation(self): ...
    def _set_stylesheet(self, component_styled): ...
    def mousePressEvent(self, ev: QMouseEvent): ...