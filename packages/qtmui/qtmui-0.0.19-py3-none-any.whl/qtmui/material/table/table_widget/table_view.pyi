import uuid
from typing import List, Union, Optional, Dict
from qtpy.QtGui import QAction
from qtpy.QtWidgets import QTableWidget, QHeaderView, QWidget, QTableWidgetItem, QStyledItemDelegate, QApplication, QStyleOptionViewItem, QTableView, QTableWidget, QWidget, QTableWidgetItem, QStyle, QStyleOptionButton, QFrame, QVBoxLayout, QProxyStyle, QStyleOption, QCheckBox, QHBoxLayout
from qtpy.QtCore import Qt, QMargins, QModelIndex, QItemSelectionModel, Property, QRectF, QRect
from qtpy.QtGui import QPainter, QColor, QKeyEvent, QPalette, QBrush, QFont
from typing import TYPE_CHECKING, Callable
from qtmui.hooks import useState
from qtmui.material.styles.create_theme.components.get_qss_styles import get_qss_style
from qtmui.material.styles import useTheme
from ....i18n.use_translation import translate, i18n
from ....common.font import getFont
from ....common.style_sheet import isDarkTheme, FluentStyleSheet, themeColor, setCustomStyleSheet
from ...widgets.check_box import CheckBoxIcon
from ...widgets.line_edit import LineEdit
from ...py_iconify import PyIconify
from ...widgets.scroll_bar import SmoothScrollDelegate
from ....qtmui_assets import QTMUI_ASSETS
from ...checkbox import Checkbox
from ...button import Button
from ...box import Box
from ...spacer import HSpacer
from .table_base import TableBase
class TableView:
    def __init__(self, parent, fullWidth: bool, isBorderVisible: bool, tableHead: list, children: list, sortingEnabled: bool, size: str, sx: Optional[Union[Callable, str, Dict]]): ...
    def _init_ui(self): ...
    def isSelectRightClickedRow(self): ...
    def setSelectRightClickedRow(self, isSelect: bool): ...