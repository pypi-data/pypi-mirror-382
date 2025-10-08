from qtpy.QtWidgets import QPushButton
from qtpy.QtCore import QSize, QCoreApplication, QEvent, Signal, QRect
from qtpy.QtGui import QMovie, QIcon, Qt, QColor
from qtpy.QtWidgets import QStyledItemDelegate, QStyle, QApplication, QStyleOptionButton, QPushButton
from ...utils.icon import icon_base64_to_pixmap
class StyledOptionButton:
    def __init__(self, parent, name: str, iconBase64: object, size: QSize, iconSize: QSize): ...