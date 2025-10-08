from typing import Callable, Optional
import uuid
from qtpy.QtWidgets import QHBoxLayout, QFrame, QSizePolicy, QPushButton, QSpacerItem
from qtpy.QtCore import QEvent, QTimer, QPoint, QSize
from qtmui.hooks.use_state import State
from ...box import Box
from ...button import Button
from ._accept_drop_frame import AcceptDropFrame
from ...popover import Popover
from ...py_iconify import PyIconify
from qtmui.material.styles import useTheme
from qtmui.material.styles.create_theme.components.get_qss_styles import get_qss_style
from ....i18n.use_translation import translate, i18n
from ....qtmui_assets import QTMUI_ASSETS
class NavItem:
    def __init__(self, ref, item: object, depth: int, open: Optional[State], active: bool, externalLink: str, onActionButtonClicked: Callable, onClick: Callable, onDrop: Callable, onMouseEnter: Callable, onMouseLeave: Callable, config: dict, popover: object, child: object, selected: bool): ...
    def reTranslation(self): ...
    def _set_stylesheet(self): ...
    def togle_collapse(self): ...
    def eventFilter(self, source, event): ...
    def check_cursor(self): ...