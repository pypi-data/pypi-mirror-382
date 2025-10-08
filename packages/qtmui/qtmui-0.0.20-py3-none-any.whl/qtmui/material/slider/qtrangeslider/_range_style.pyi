from __future__ import annotations
import platform
import re
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING
from qtpy import PYQT_VERSION
from qtpy.QtCore import Qt
from qtpy.QtGui import QBrush, QColor, QGradient, QLinearGradient, QPalette, QRadialGradient
from qtpy.QtWidgets import QApplication, QSlider, QStyleOptionSlider
class RangeSliderStyle:
    brush_active: Any
    brush_inactive: Any
    brush_disabled: Any
    pen_active: Any
    pen_inactive: Any
    pen_disabled: Any
    vertical_thickness: Any
    horizontal_thickness: Any
    tick_offset: Any
    tick_bar_alpha: Any
    v_offset: Any
    h_offset: Any
    has_stylesheet: bool
    def brush(self, opt: QStyleOptionSlider): ...
    def pen(self, opt: QStyleOptionSlider): ...
    def offset(self, opt: QStyleOptionSlider): ...
    def thickness(self, opt: QStyleOptionSlider): ...
def parse_color(color: str, default_attr): ...
def update_styles_from_stylesheet(obj: _GenericRangeSlider): ...