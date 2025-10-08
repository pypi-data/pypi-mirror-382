from qtpy.QtWidgets import QPushButton
from qtpy.QtCore import QSize, QCoreApplication, QEvent, Signal, QRect
from qtpy.QtGui import QMovie, QIcon, Qt, QColor
from qtpy.QtWidgets import QStyledItemDelegate, QStyle, QApplication, QStyleOptionButton, QPushButton
from ..icon import icon_profile_edit
from ...utils.icon import icon_base64_to_pixmap
from ...button import Button
class StyleOptionButton:
    def __init__(self, parent, name: str, iconBase64: object, size: QSize, iconSize: QSize): ...