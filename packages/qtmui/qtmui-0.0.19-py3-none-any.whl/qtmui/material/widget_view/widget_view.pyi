from typing import Callable
from qtpy.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton
from ...common.ui_functions import clear_layout
from qtmui.hooks.use_state import State
class WidgetView:
    def __init__(self, direction, renderView: Callable, renderViewProps: Callable, children: State, view: State): ...
    def _render_ui(self, widget): ...