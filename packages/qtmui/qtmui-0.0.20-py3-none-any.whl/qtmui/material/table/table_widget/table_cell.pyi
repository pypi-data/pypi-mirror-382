from typing import TYPE_CHECKING, Callable
from qtpy.QtWidgets import QFrame, QHBoxLayout, QWidget
from qtpy.QtCore import Qt
from ...typography import Typography
from ...avatar import Avatar
from ...label import Label
class TableCell:
    def __init__(self, key: str, padding: str, align: str, children: object, colSpan: int, onClick: Callable, sx: str, text: str): ...
    def enterEvent(self, event): ...