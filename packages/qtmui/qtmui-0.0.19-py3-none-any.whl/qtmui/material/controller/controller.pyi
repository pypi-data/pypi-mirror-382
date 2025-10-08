from typing import Callable, Optional
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QFrame
class Controller:
    def __init__(self, name: str, control: object, render: Callable, defaultValue, rules: object, shouldUnregister: bool): ...